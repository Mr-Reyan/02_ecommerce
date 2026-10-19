"""
MOCK payment gateway. No real money moves and no external service is called.
Replace charge() with a real gateway call (e.g. Stripe) in production.
"""
import uuid
from dataclasses import dataclass
from decimal import Decimal

SUPPORTED_CURRENCIES = {"usd", "eur", "pkr"}


class PaymentGatewayError(Exception):
    """Gateway unreachable or timed out (safe to retry)."""


@dataclass
class PaymentResult:
    success: bool
    reference: str = ""
    failure_reason: str = ""


def charge(amount: Decimal, currency: str, payment_token: str = "tok_success") -> PaymentResult:
    currency = (currency or "").lower()
    if currency not in SUPPORTED_CURRENCIES:
        return PaymentResult(False, failure_reason="unsupported_currency")
    if amount <= 0:
        return PaymentResult(False, failure_reason="invalid_amount")

    # Magic tokens, so failures can be tested (like Stripe's test cards)
    if payment_token == "tok_declined":
        return PaymentResult(False, failure_reason="card_declined")
    if payment_token == "tok_insufficient_funds":
        return PaymentResult(False, failure_reason="insufficient_funds")
    if payment_token == "tok_timeout":
        raise PaymentGatewayError("Gateway timeout")

    return PaymentResult(True, reference=f"mock_pay_{uuid.uuid4().hex[:16]}")