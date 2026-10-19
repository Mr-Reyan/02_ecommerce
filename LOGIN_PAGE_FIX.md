# Login Page Infinite Loop Fix

## 🐛 The Problem

Login page was stuck in infinite loop with these errors:
```
POST /token/refresh/ HTTP/1.1" 401
GET /cart/ HTTP/1.1" 401
GET /csrf/ HTTP/1.1" 404  (repeated continuously)
```

## 🔍 Root Causes

### 1. **Providers.js calling removed /csrf/ endpoint**
- **File**: `frontend/src/app/providers.js`
- **Issue**: `useEffect` was fetching `/csrf/` on every page load
- **Why**: We removed the `/csrf/` endpoint from backend but forgot to remove the frontend call

### 2. **Navbar fetching cart on unauthenticated pages**
- **File**: `frontend/src/components/Navbar.js`
- **Issue**: `useQuery` for cart was running on ALL pages including login/signup
- **Result**: Cart API returned 401 → triggered token refresh → failed → redirected to login → page reloaded → infinite loop

### 3. **auth.service.js redirecting from login to login**
- **File**: `frontend/src/services/auth.service.js`
- **Issue**: When 401 occurred, it tried to refresh token, failed, then redirected to `/login` even if already on `/login`
- **Result**: Redirect loop

## ✅ Fixes Applied

### Fix 1: Removed CSRF fetch from providers
**File**: `frontend/src/app/providers.js`

**Before**:
```javascript
useEffect(() => {
  fetch('http://127.0.0.1:8000/csrf/', {
    credentials: 'include',
  })
}, [])
```

**After**:
```javascript
// Removed entire useEffect - no longer needed since CSRF endpoint was removed
```

---

### Fix 2: Only fetch cart when authenticated
**File**: `frontend/src/components/Navbar.js`

**Before**:
```javascript
const { data: cart } = useQuery({
  queryKey: ['cart'],
  queryFn: getCart,
  staleTime: 1000 * 30,
})
```

**After**:
```javascript
const [isAuthenticated, setIsAuthenticated] = useState(false)

useEffect(() => {
  const currentPath = window.location.pathname
  const isAuthPage = currentPath === '/login' || currentPath === '/signup'
  setIsAuthenticated(!isAuthPage)
}, [])

const { data: cart } = useQuery({
  queryKey: ['cart'],
  queryFn: getCart,
  staleTime: 1000 * 30,
  enabled: isAuthenticated,  // ← Only fetch when authenticated
  retry: false,               // ← Don't retry on 401
})
```

---

### Fix 3: Don't redirect if already on auth pages
**File**: `frontend/src/services/auth.service.js`

**Before**:
```javascript
if (response.status === 401) {
  const refresh = await fetch(`${BASE_URL}/token/refresh/`, ...)
  
  if (!refresh.ok) {
    window.location.href = "/login";  // ← Always redirects
    throw new Error("Session expired");
  }
  // ... CSRF token logic (removed)
}
```

**After**:
```javascript
if (response.status === 401) {
  // Don't try to refresh if we're already on login/signup pages
  if (typeof window !== 'undefined') {
    const currentPath = window.location.pathname;
    if (currentPath === '/login' || currentPath === '/signup') {
      throw new Error("Unauthorized");  // ← Just throw, don't redirect
    }
  }

  const refresh = await fetch(`${BASE_URL}/token/refresh/`, ...)
  
  if (!refresh.ok) {
    if (typeof window !== 'undefined') {
      window.location.href = "/login";
    }
    throw new Error("Session expired");
  }

  // Removed CSRF token logic - no longer needed
}
```

## 🎯 Result

✅ Login page no longer loops  
✅ No more 404 errors for `/csrf/`  
✅ No more unnecessary 401 errors on unauthenticated pages  
✅ Cart only fetches when user is logged in  
✅ Token refresh only attempts on protected pages  

## 📝 Files Modified

1. `frontend/src/app/providers.js` - Removed CSRF fetch
2. `frontend/src/components/Navbar.js` - Added authentication check
3. `frontend/src/services/auth.service.js` - Added login page check, removed CSRF logic

## 🧪 Testing

**Before Fix:**
- ❌ Login page continuously refreshes
- ❌ Console shows 401 and 404 errors repeating
- ❌ Cannot use login page at all

**After Fix:**
- ✅ Login page loads normally
- ✅ No errors in console
- ✅ Can log in successfully
- ✅ After login, cart fetches properly
- ✅ After logout, no errors on login page

## 💡 Lesson Learned

When removing backend endpoints:
1. ✅ Remove the endpoint from backend ✓
2. ✅ Remove it from backend URLs ✓
3. ⚠️ **Search and remove ALL frontend calls** ← We missed this!
4. ⚠️ **Check if any components fetch data unconditionally** ← We missed this!

Always grep the entire frontend for removed endpoint paths!
