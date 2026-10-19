"""
Tests for the `authen` app: signup, login, token refresh, logout, auth status.

Place in: authen/test_authen.py
Run:      python manage.py test authen -v 2

Every test docstring starts with a Test ID (AUTH-xx) followed by
Feature | Scenario | Expected, so it can be copied straight into
test-cases.xlsx.
"""
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from authen.models import Tenant

User = get_user_model()

SIGNUP_URL = "/signup/"
LOGIN_URL = "/login/"
REFRESH_URL = "/token/refresh/"
LOGOUT_URL = "/logout/"
STATUS_URL = "/status/"

PASSWORD = "StrongPass#123"


def expired_access_token(user):
    token = AccessToken.for_user(user)
    token.set_exp(lifetime=-timedelta(seconds=10))
    return str(token)


class AuthTestBase(TestCase):
    def setUp(self):
        # RegisterSerializer hardcodes Tenant id=2, so it must exist.
        self.tenant = Tenant.objects.create(id=2, name="Default Tenant")
        self.user = User.objects.create_user(
            username="alice",
            email="alice@example.com",
            password=PASSWORD,
            tenant=self.tenant,
        )
        self.client = APIClient()
        # Unhandled server errors become 500 responses we can assert on
        self.client.raise_request_exception = False

    def login(self, username="alice", password=PASSWORD):
        return self.client.post(
            LOGIN_URL, {"username": username, "password": password}, format="json"
        )


# --------------------------------------------------------------------------- #
# Signup
# --------------------------------------------------------------------------- #
class SignupTests(AuthTestBase):
    valid = {"username": "bob", "email": "bob@example.com", "password": PASSWORD}

    def test_auth01_valid_signup(self):
        """AUTH-01 | Signup | Valid payload creates a user in the default tenant | 201"""
        r = self.client.post(SIGNUP_URL, self.valid, format="json")
        self.assertEqual(r.status_code, 201)
        user = User.objects.get(username="bob")
        self.assertEqual(user.tenant_id, 2)
        self.assertTrue(user.check_password(PASSWORD))
        self.assertNotEqual(user.password, PASSWORD)  # stored hashed
        self.assertNotIn("password", r.data)  # never echoed back

    def test_auth02_missing_required_fields(self):
        """AUTH-02 | Signup | Missing username or password | 400, no user created"""
        for field in ("username", "password"):
            with self.subTest(missing=field):
                payload = {k: v for k, v in self.valid.items() if k != field}
                r = self.client.post(SIGNUP_URL, payload, format="json")
                self.assertEqual(r.status_code, 400)
                self.assertIn(field, r.data)
        self.assertEqual(User.objects.count(), 1)  # only the setUp user

    def test_auth03_duplicate_signup_retry(self):
        """AUTH-03 | Signup | Same payload submitted twice (retry) | 201 then 400, one row"""
        first = self.client.post(SIGNUP_URL, self.valid, format="json")
        second = self.client.post(SIGNUP_URL, self.valid, format="json")
        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 400)
        self.assertEqual(User.objects.filter(username="bob").count(), 1)

    def test_auth04_duplicate_of_existing_user(self):
        """AUTH-04 | Signup | Username already taken by existing user | 400"""
        payload = {**self.valid, "username": "alice"}
        r = self.client.post(SIGNUP_URL, payload, format="json")
        self.assertEqual(r.status_code, 400)
        self.assertIn("username", r.data)

    def test_auth05_invalid_email(self):
        """AUTH-05 | Signup | Malformed email | 400"""
        payload = {**self.valid, "email": "not-an-email"}
        r = self.client.post(SIGNUP_URL, payload, format="json")
        self.assertEqual(r.status_code, 400)
        self.assertIn("email", r.data)

    def test_auth06_username_length_boundary(self):
        """AUTH-06 | Signup | Username 150 chars accepted, 151 rejected | 201 / 400"""
        ok = self.client.post(
            SIGNUP_URL, {**self.valid, "username": "a" * 150}, format="json"
        )
        too_long = self.client.post(
            SIGNUP_URL, {**self.valid, "username": "b" * 151}, format="json"
        )
        self.assertEqual(ok.status_code, 201)
        self.assertEqual(too_long.status_code, 400)

    def test_auth07_weak_password_rejected(self):
        """AUTH-07 | Signup | One-character password | 400 (password validation)

        Expected to FAIL today: RegisterSerializer never runs Django's
        password validators. Log as a defect or add validate_password().
        """
        r = self.client.post(
            SIGNUP_URL, {**self.valid, "password": "1"}, format="json"
        )
        self.assertEqual(r.status_code, 400)

    def test_auth08_default_tenant_missing(self):
        """AUTH-08 | Signup | Default tenant (id=2) does not exist | handled error, not 500

        Expected to FAIL today: Tenant.objects.get(id=2) raises DoesNotExist
        and the API returns 500. Log as a defect.
        """
        Tenant.objects.filter(id=2).delete()
        r = self.client.post(SIGNUP_URL, self.valid, format="json")
        self.assertLess(r.status_code, 500)
        self.assertFalse(User.objects.filter(username="bob").exists())

    def test_auth09_wrong_method(self):
        """AUTH-09 | Signup | GET on signup endpoint | 405"""
        self.assertEqual(self.client.get(SIGNUP_URL).status_code, 405)


# --------------------------------------------------------------------------- #
# Login
# --------------------------------------------------------------------------- #
class LoginTests(AuthTestBase):
    def test_auth10_valid_login_sets_cookies(self):
        """AUTH-10 | Login | Valid credentials | 200, httpOnly access+refresh cookies, no tokens in body"""
        r = self.login()
        self.assertEqual(r.status_code, 200)
        self.assertIn("access", r.cookies)
        self.assertIn("refresh", r.cookies)
        self.assertTrue(r.cookies["access"]["httponly"])
        self.assertTrue(r.cookies["refresh"]["httponly"])
        self.assertEqual(r.cookies["access"]["max-age"], 60 * 15)
        self.assertEqual(r.cookies["refresh"]["max-age"], 60 * 60 * 24 * 7)
        self.assertNotIn("access", r.data)
        self.assertNotIn("refresh", r.data)

    def test_auth11_cookie_tokens_are_valid(self):
        """AUTH-11 | Login | Issued cookies contain valid JWTs for the right user | decode OK"""
        r = self.login()
        access = AccessToken(r.cookies["access"].value)
        RefreshToken(r.cookies["refresh"].value)  # raises if invalid
        self.assertEqual(str(access["user_id"]), str(self.user.id))

    def test_auth12_wrong_password(self):
        """AUTH-12 | Login | Wrong password | 401, no cookies"""
        r = self.login(password="wrong-password")
        self.assertEqual(r.status_code, 401)
        self.assertNotIn("access", r.cookies)
        self.assertNotIn("refresh", r.cookies)

    def test_auth13_unknown_user(self):
        """AUTH-13 | Login | Username does not exist | 401"""
        r = self.login(username="ghost")
        self.assertEqual(r.status_code, 401)

    def test_auth14_missing_fields(self):
        """AUTH-14 | Login | Missing username or password | 400"""
        for payload in ({"username": "alice"}, {"password": PASSWORD}, {}):
            with self.subTest(payload=payload):
                r = self.client.post(LOGIN_URL, payload, format="json")
                self.assertEqual(r.status_code, 400)

    def test_auth15_inactive_user(self):
        """AUTH-15 | Login | Deactivated account | 401, no cookies"""
        self.user.is_active = False
        self.user.save()
        r = self.login()
        self.assertEqual(r.status_code, 401)
        self.assertNotIn("access", r.cookies)

    def test_auth16_wrong_method(self):
        """AUTH-16 | Login | GET on login endpoint | 405"""
        self.assertEqual(self.client.get(LOGIN_URL).status_code, 405)


# --------------------------------------------------------------------------- #
# Token refresh
# --------------------------------------------------------------------------- #
class RefreshTests(AuthTestBase):
    def test_auth20_refresh_success(self):
        """AUTH-20 | Refresh | Valid refresh cookie | 200, new access cookie"""
        self.client.cookies["refresh"] = str(RefreshToken.for_user(self.user))
        r = self.client.post(REFRESH_URL)
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.data["success"])
        new_access = AccessToken(r.cookies["access"].value)
        self.assertEqual(str(new_access["user_id"]), str(self.user.id))
        self.assertTrue(r.cookies["access"]["httponly"])

    def test_auth21_missing_refresh_cookie(self):
        """AUTH-21 | Refresh | No refresh cookie | 401 'Refresh token missing'"""
        r = self.client.post(REFRESH_URL)
        self.assertEqual(r.status_code, 401)
        self.assertEqual(r.data["detail"], "Refresh token missing")

    def test_auth22_garbage_refresh_cookie(self):
        """AUTH-22 | Refresh | Malformed token | 401 'Invalid refresh token'"""
        self.client.cookies["refresh"] = "not.a.jwt"
        r = self.client.post(REFRESH_URL)
        self.assertEqual(r.status_code, 401)
        self.assertEqual(r.data["detail"], "Invalid refresh token")

    def test_auth23_access_token_cannot_be_used_as_refresh(self):
        """AUTH-23 | Refresh | Access token sent in refresh cookie | 401 (token type check)"""
        self.client.cookies["refresh"] = str(AccessToken.for_user(self.user))
        r = self.client.post(REFRESH_URL)
        self.assertEqual(r.status_code, 401)

    def test_auth24_expired_refresh_token(self):
        """AUTH-24 | Refresh | Expired refresh token | 401"""
        token = RefreshToken.for_user(self.user)
        token.set_exp(lifetime=-timedelta(seconds=10))
        self.client.cookies["refresh"] = str(token)
        r = self.client.post(REFRESH_URL)
        self.assertEqual(r.status_code, 401)


# --------------------------------------------------------------------------- #
# Auth status
# --------------------------------------------------------------------------- #
class AuthStatusTests(AuthTestBase):
    def test_auth30_no_cookie(self):
        """AUTH-30 | Status | No access cookie | 200 authenticated=false"""
        r = self.client.get(STATUS_URL)
        self.assertEqual(r.status_code, 200)
        self.assertFalse(r.data["authenticated"])

    def test_auth31_valid_access_cookie(self):
        """AUTH-31 | Status | Valid access cookie | 200 authenticated=true"""
        self.client.cookies["access"] = str(AccessToken.for_user(self.user))
        r = self.client.get(STATUS_URL)
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.data["authenticated"])

    def test_auth32_garbage_cookie(self):
        """AUTH-32 | Status | Malformed access cookie | 200 authenticated=false"""
        self.client.cookies["access"] = "garbage"
        r = self.client.get(STATUS_URL)
        self.assertEqual(r.status_code, 200)
        self.assertFalse(r.data["authenticated"])

    def test_auth33_expired_cookie(self):
        """AUTH-33 | Status | Expired access cookie | 200 authenticated=false"""
        self.client.cookies["access"] = expired_access_token(self.user)
        r = self.client.get(STATUS_URL)
        self.assertFalse(r.data["authenticated"])

    def test_auth34_refresh_token_in_access_cookie(self):
        """AUTH-34 | Status | Refresh token placed in access cookie | authenticated=false"""
        self.client.cookies["access"] = str(RefreshToken.for_user(self.user))
        r = self.client.get(STATUS_URL)
        self.assertFalse(r.data["authenticated"])


# --------------------------------------------------------------------------- #
# Logout + end-to-end regression flows
# --------------------------------------------------------------------------- #
class LogoutAndFlowTests(AuthTestBase):
    def test_auth40_logout_clears_cookies(self):
        """AUTH-40 | Logout | Authenticated logout | 200, access+refresh cookies expired"""
        self.client.force_authenticate(self.user)
        r = self.client.post(LOGOUT_URL)
        self.assertEqual(r.status_code, 200)
        for name in ("access", "refresh"):
            self.assertEqual(r.cookies[name].value, "")
            self.assertEqual(r.cookies[name]["max-age"], 0)

    def test_auth41_logout_wrong_method(self):
        """AUTH-41 | Logout | GET on logout endpoint | 405"""
        self.client.force_authenticate(self.user)
        self.assertEqual(self.client.get(LOGOUT_URL).status_code, 405)

    def test_auth42_login_status_logout_status(self):
        """AUTH-42 | Regression flow | login -> status true -> logout -> status false"""
        self.assertEqual(self.login().status_code, 200)
        self.assertTrue(self.client.get(STATUS_URL).data["authenticated"])

        self.client.force_authenticate(self.user)
        self.assertEqual(self.client.post(LOGOUT_URL).status_code, 200)
        self.client.force_authenticate(None)

        self.assertFalse(self.client.get(STATUS_URL).data["authenticated"])

    def test_auth43_expired_access_then_refresh_restores_session(self):
        """AUTH-43 | Regression flow | expired access -> status false -> refresh -> status true"""
        self.client.cookies["access"] = expired_access_token(self.user)
        self.client.cookies["refresh"] = str(RefreshToken.for_user(self.user))
        self.assertFalse(self.client.get(STATUS_URL).data["authenticated"])

        self.assertEqual(self.client.post(REFRESH_URL).status_code, 200)
        self.assertTrue(self.client.get(STATUS_URL).data["authenticated"])

"""
Tests for the Redis sliding-window rate limiter (is_rate_limited).

Uses an in-memory fake Redis and a controllable clock, so no Redis server is
needed and the tests are deterministic.

Place next to the rate-limiter module and set RATE_LIMIT_MODULE below.
Run: python manage.py test <app_or_package> -v 2
"""
import importlib
import unittest
from unittest import mock

RATE_LIMIT_MODULE = "config.redis_client"  # TODO: dotted path of the file with is_rate_limited


class FakeRedis:
    """Minimal sorted-set implementation of the four calls the limiter uses."""

    def __init__(self):
        self.store = {}
        self.expiry = {}

    def zremrangebyscore(self, key, low, high):
        zset = self.store.get(key, {})
        for member in [m for m, score in zset.items() if low <= score <= high]:
            del zset[member]

    def zcard(self, key):
        return len(self.store.get(key, {}))

    def zadd(self, key, mapping):
        self.store.setdefault(key, {}).update(mapping)

    def expire(self, key, seconds):
        self.expiry[key] = seconds


class RateLimiterTests(unittest.TestCase):
    def setUp(self):
        self.rl = importlib.import_module(RATE_LIMIT_MODULE)
        self.fake = FakeRedis()

        patch_redis = mock.patch.object(self.rl, "redis_client", self.fake)
        patch_redis.start()
        self.addCleanup(patch_redis.stop)

        # Controllable clock: each call advances 1 ms so members never collide
        self.now = 1000.0
        patch_time = mock.patch.object(self.rl, "time")
        mock_time = patch_time.start()
        self.addCleanup(patch_time.stop)
        mock_time.time.side_effect = self._tick

    def _tick(self):
        value = self.now
        self.now += 0.001
        return value

    def hit(self, user_id=1, times=1):
        return [self.rl.is_rate_limited(user_id) for _ in range(times)]

    def test_rl01_first_request_allowed(self):
        """RL-01 | Rate limit | First request | allowed (False)"""
        self.assertFalse(self.rl.is_rate_limited(1))

    def test_rl02_limit_boundary(self):
        """RL-02 | Rate limit | Exactly LIMIT requests allowed, LIMIT+1 blocked | all False, then True"""
        results = self.hit(times=self.rl.LIMIT)
        self.assertFalse(any(results))
        self.assertTrue(self.rl.is_rate_limited(1))

    def test_rl03_blocked_requests_are_not_counted(self):
        """RL-03 | Rate limit | Rejected requests do not extend the window count | count stays at LIMIT"""
        self.hit(times=self.rl.LIMIT)
        self.hit(times=10)
        self.assertEqual(self.fake.zcard("rate_limit:1"), self.rl.LIMIT)

    def test_rl04_window_expiry_allows_again(self):
        """RL-04 | Rate limit | After WINDOW seconds old hits expire | allowed again"""
        self.hit(times=self.rl.LIMIT)
        self.assertTrue(self.rl.is_rate_limited(1))
        self.now += self.rl.WINDOW + 1
        self.assertFalse(self.rl.is_rate_limited(1))

    def test_rl05_users_are_independent(self):
        """RL-05 | Rate limit | User 1 exhausted, user 2 unaffected | user 2 allowed"""
        self.hit(user_id=1, times=self.rl.LIMIT)
        self.assertTrue(self.rl.is_rate_limited(1))
        self.assertFalse(self.rl.is_rate_limited(2))

    def test_rl06_fails_open_when_redis_down(self):
        """RL-06 | Rate limit | Redis raises ConnectionError | allowed (fail-open), no exception"""
        broken = mock.Mock()
        broken.zremrangebyscore.side_effect = ConnectionError("redis down")
        with mock.patch.object(self.rl, "redis_client", broken):
            self.assertFalse(self.rl.is_rate_limited(1))

    def test_rl07_key_format_and_ttl(self):
        """RL-07 | Rate limit | Key is rate_limit:<user_id> with TTL = WINDOW | key present, TTL set"""
        self.rl.is_rate_limited(42)
        self.assertIn("rate_limit:42", self.fake.store)
        self.assertEqual(self.fake.expiry["rate_limit:42"], self.rl.WINDOW)

    def test_rl08_sliding_window_partial_expiry(self):
        """RL-08 | Rate limit | Hits older than WINDOW drop out one by one | blocked until the oldest expires"""
        self.hit(times=self.rl.LIMIT)
        self.assertTrue(self.rl.is_rate_limited(1))
        # Advance so only the very first hit has aged out of the window
        self.now = 1000.0 + self.rl.WINDOW + 0.0005
        self.assertFalse(self.rl.is_rate_limited(1))
        # Window is full again: 99 surviving hits + the one just added
        self.assertEqual(self.fake.zcard("rate_limit:1"), self.rl.LIMIT)


if __name__ == "__main__":
    unittest.main()