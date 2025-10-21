# Authentication Quick Reference

**UniFi Network API - Authentication System**
**Version**: 1.0.0
**Status**: Production Ready ✅

---

## 🚀 Quick Start

### 1. Start Server

```powershell
cd backend
python full_test_server.py
```

### 2. Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123!"}'
```

### 3. Use Token

```bash
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 🔐 Default Credentials

- **Username**: `admin`
- **Password**: `admin123!`
- **Role**: Superuser
- **Email**: `admin@unifi-monitor.local`

⚠️ **Change the password immediately in production!**

---

## 📡 API Endpoints

### Public Endpoints

**Login**

```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123!"
}

Response: 200 OK
{
  "access_token": "eyJ0eXAiOiJKV1...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": { ... }
}
```

### Protected Endpoints (Token Required)

**Get Current User**

```http
GET /api/auth/me
Authorization: Bearer <token>

Response: 200 OK
{
  "id": 1,
  "username": "admin",
  "email": "admin@unifi-monitor.local",
  "full_name": "System Administrator",
  "is_active": true,
  "is_superuser": true,
  "created_at": "2025-10-18T20:00:00",
  "last_login": "2025-10-18T20:30:00"
}
```

**Logout**

```http
POST /api/auth/logout
Authorization: Bearer <token>

Response: 200 OK
{
  "message": "Successfully logged out",
  "username": "admin"
}
```

**Change Password**

```http
POST /api/auth/change-password
Authorization: Bearer <token>
Content-Type: application/json

{
  "current_password": "admin123!",
  "new_password": "newpassword456!"
}

Response: 200 OK
{
  "message": "Password changed successfully"
}
```

### Admin-Only Endpoints (Superuser Required)

**Create User**

```http
POST /api/auth/users
Authorization: Bearer <token>
Content-Type: application/json

{
  "username": "newuser",
  "password": "password123!",
  "email": "user@example.com",
  "full_name": "New User",
  "is_active": true,
  "is_superuser": false
}

Response: 200 OK
{
  "id": 2,
  "username": "newuser",
  "email": "user@example.com",
  "full_name": "New User",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2025-10-18T20:35:00",
  "last_login": null
}
```

**List Users**

```http
GET /api/auth/users?skip=0&limit=100
Authorization: Bearer <token>

Response: 200 OK
[
  {
    "id": 1,
    "username": "admin",
    ...
  },
  {
    "id": 2,
    "username": "newuser",
    ...
  }
]
```

---

## 🐍 Python Examples

### Login and Get Token

```python
import requests

BASE_URL = "http://localhost:8000"

# Login
response = requests.post(
    f"{BASE_URL}/api/auth/login",
    json={"username": "admin", "password": "admin123!"}
)

data = response.json()
token = data["access_token"]
print(f"Token: {token}")
```

### Make Authenticated Request

```python
import requests

token = "your-token-here"
headers = {"Authorization": f"Bearer {token}"}

# Get current user
response = requests.get(
    f"{BASE_URL}/api/auth/me",
    headers=headers
)

user = response.json()
print(f"Logged in as: {user['username']}")
```

### Create New User (Admin Only)

```python
import requests

token = "admin-token-here"
headers = {"Authorization": f"Bearer {token}"}

response = requests.post(
    f"{BASE_URL}/api/auth/users",
    headers=headers,
    json={
        "username": "testuser",
        "password": "testpass123!",
        "email": "test@example.com",
        "full_name": "Test User",
        "is_active": True,
        "is_superuser": False
    }
)

new_user = response.json()
print(f"Created user: {new_user['username']}")
```

---

## 🌐 JavaScript/React Example

### Login Hook

```javascript
import { useState } from "react";

function useAuth() {
  const [token, setToken] = useState(null);
  const [user, setUser] = useState(null);

  const login = async (username, password) => {
    const response = await fetch("http://localhost:8000/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });

    if (response.ok) {
      const data = await response.json();
      setToken(data.access_token);
      setUser(data.user);
      localStorage.setItem("token", data.access_token);
      return true;
    }
    return false;
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem("token");
  };

  return { token, user, login, logout };
}
```

### Authenticated Fetch

```javascript
async function fetchWithAuth(url, options = {}) {
  const token = localStorage.getItem("token");

  const response = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      Authorization: `Bearer ${token}`,
    },
  });

  if (response.status === 401) {
    // Token expired or invalid
    localStorage.removeItem("token");
    window.location.href = "/login";
  }

  return response;
}

// Usage
const response = await fetchWithAuth("http://localhost:8000/api/auth/me");
const user = await response.json();
```

---

## 🔒 Protecting Endpoints

### Add Authentication to Existing Endpoints

```python
from fastapi import Depends
from typing import Annotated
from backend.src.auth.dependencies import get_current_user
from backend.src.database.user_repository import User

@router.get("/api/devices")
async def list_devices(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """List devices - authentication required."""
    # current_user is authenticated User object
    return {"devices": [...]}
```

### Require Superuser Permission

```python
from backend.src.auth.dependencies import get_current_superuser

@router.delete("/api/devices/{device_id}")
async def delete_device(
    device_id: str,
    current_user: Annotated[User, Depends(get_current_superuser)]
):
    """Delete device - superuser only."""
    # current_user is authenticated superuser
    return {"message": "Deleted"}
```

### Optional Authentication

```python
from typing import Optional
from backend.src.auth.dependencies import optional_auth

@router.get("/api/public/stats")
async def public_stats(
    current_user: Optional[User] = Depends(optional_auth)
):
    """Public endpoint with optional features for authenticated users."""
    if current_user:
        return {"stats": "detailed"}
    else:
        return {"stats": "public"}
```

---

## 🧪 Testing

### Quick Test

```bash
python backend/quick_auth_test.py
```

### Full Test Suite

```bash
python backend/test_auth.py
```

### Manual Testing with cURL

```bash
# 1. Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123!"}' \
  | jq -r '.access_token')

# 2. Get current user
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"

# 3. List users (admin only)
curl http://localhost:8000/api/auth/users \
  -H "Authorization: Bearer $TOKEN"

# 4. Create user (admin only)
curl -X POST http://localhost:8000/api/auth/users \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123!",
    "email": "test@example.com",
    "full_name": "Test User",
    "is_active": true,
    "is_superuser": false
  }'
```

---

## ⚠️ Error Responses

### 401 Unauthorized

```json
{
  "error": "Not authenticated"
}
```

**Causes**:

- No token provided
- Invalid token
- Expired token

### 403 Forbidden

```json
{
  "detail": "Not enough permissions"
}
```

**Causes**:

- User is not a superuser (for admin endpoints)

### 400 Bad Request

```json
{
  "error": "Validation error",
  "detail": "Username 'admin' already exists"
}
```

**Causes**:

- Invalid input data
- Duplicate username
- Password too short

---

## 🔧 Configuration

### Token Settings

```python
# backend/src/config.py
class Settings(BaseSettings):
    secret_key: str = "change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 hours
```

### Environment Variables

```bash
# .env file
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

---

## 📚 Additional Resources

- **Full Documentation**: `docs/PHASE_5.1.3_COMPLETE.md`
- **API Docs**: <http://localhost:8000/docs>
- **Test Scripts**: `backend/test_auth.py`, `backend/quick_auth_test.py`

---

**Last Updated**: October 18, 2025
**Status**: ✅ Production Ready
