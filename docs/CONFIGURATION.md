# Configuration Checklist

## ✅ What You Have Configured

Based on your current setup, you have:

1. **API Key** - Already in `config.py` ✓
2. **Base URL** - Set to `https://api.ui.com/v1` ✓
3. **Basic logging** - INFO level, logs to `logs/unifi_api.log` ✓

---

## 🔍 Additional Configuration You May Need

### 1. **Timeout Settings** (Optional but Recommended)

Add request timeout to prevent hanging requests:

```python
# In config.py
REQUEST_TIMEOUT = 30  # seconds
```

Then update the client to use it:

```python
client = UniFiClient(api_key, base_url, timeout=REQUEST_TIMEOUT)
```

---

### 2. **SSL/TLS Verification** (Important for Security)

If using a local controller with self-signed certificates:

```python
# In config.py
VERIFY_SSL = True  # Set to False only for self-signed certs in dev
```

---

### 3. **Retry Configuration** (Recommended for Production)

Handle transient API failures:

```python
# In config.py
MAX_RETRIES = 3
RETRY_BACKOFF = 2  # seconds between retries (exponential)
```

---

### 4. **Rate Limiting** (Important to Avoid API Throttling)

```python
# In config.py
REQUESTS_PER_SECOND = 10  # Adjust based on your API limits
MIN_REQUEST_INTERVAL = 0.1  # Minimum seconds between requests
```

---

### 5. **Site/Location Information** (If Using Multiple Sites)

```python
# In config.py
DEFAULT_SITE = "default"  # Your primary site name
SITE_IDS = {
    "home": "abc123",
    "office": "def456"
}
```

---

### 6. **Logging Configuration** (Enhanced)

You already have basic logging. Consider adding:

```python
# In config.py
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE = "logs/unifi_api.log"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_MAX_BYTES = 10485760  # 10MB
LOG_BACKUP_COUNT = 5  # Keep 5 old log files
```

---

### 7. **Environment-Specific Settings** (Dev vs Production)

```python
# In config.py
ENVIRONMENT = "development"  # or "production", "testing"

# Different settings per environment
if ENVIRONMENT == "development":
    LOG_LEVEL = "DEBUG"
    VERIFY_SSL = False
elif ENVIRONMENT == "production":
    LOG_LEVEL = "WARNING"
    VERIFY_SSL = True
```

---

### 8. **Cache Configuration** (For Performance)

If making repeated calls:

```python
# In config.py
ENABLE_CACHE = True
CACHE_TTL = 300  # Cache results for 5 minutes
```

---

### 9. **Pagination Settings** (For Large Data Sets)

```python
# In config.py
DEFAULT_PAGE_SIZE = 100
MAX_PAGE_SIZE = 1000
```

---

### 10. **Feature Flags** (For Experimentation)

```python
# In config.py
FEATURES = {
    "auto_reconnect": True,
    "detailed_logging": False,
    "metrics_collection": False
}
```

---

## 📋 Quick Configuration Template

Here's a comprehensive `config.py` template with all recommended settings:

```python
"""
UniFi API Configuration
"""

# === REQUIRED SETTINGS ===
API_KEY = "your-api-key-here"
BASE_URL = "https://api.ui.com/v1"

# === CONNECTION SETTINGS ===
REQUEST_TIMEOUT = 30  # seconds
VERIFY_SSL = True  # Set to False for self-signed certs
MAX_RETRIES = 3
RETRY_BACKOFF = 2  # seconds

# === RATE LIMITING ===
REQUESTS_PER_SECOND = 10
MIN_REQUEST_INTERVAL = 0.1  # seconds

# === LOGGING ===
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE = "logs/unifi_api.log"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_MAX_BYTES = 10485760  # 10MB
LOG_BACKUP_COUNT = 5

# === SITES ===
DEFAULT_SITE = "default"

# === ENVIRONMENT ===
ENVIRONMENT = "development"  # development, production, testing

# === FEATURES (Optional) ===
ENABLE_CACHE = False
CACHE_TTL = 300  # seconds
DEFAULT_PAGE_SIZE = 100
```

---

## 🎯 What to Gather Right Now

### Immediate Needs:

1. **Your API Key** - ✅ Already have it
2. **Base URL** - ✅ Already set

### Good to Know (Check the UniFi Dashboard):

3. **Site Name/ID** - Go to unifi.ui.com → Settings → Find your site name
4. **API Rate Limits** - Check your API tier/plan limits at unifi.ui.com
5. **Device Count** - How many devices you're managing (affects pagination needs)

### For Production (Not needed for exploration):

6. **SSL Certificate Details** - If using local controller
7. **Monitoring/Alerting Endpoints** - If you want to track API health
8. **Backup API Keys** - Create a backup key for failover

---

## 🧪 Test Your Current Configuration

Run this to verify what you have works:

```bash
python examples/api_key_example.py
```

If successful, you're ready to explore the API! 🚀

---

## 📚 Next Steps

1. **Explore Available Endpoints** - Check `docs/API_REFERENCE.md`
2. **Run Example Scripts** - Try `examples/list_hosts.py`
3. **Use the API Explorer** - Open `api_explorer.http` in VS Code
4. **Enable Debug Logging** - Set `LOG_LEVEL = "DEBUG"` to see API calls

---

## 💡 Pro Tips

- Start with **read-only operations** (GET requests) for exploration
- Enable **DEBUG logging** to understand API responses
- Use the **API Explorer** (`api_explorer.http`) to test endpoints interactively
- Keep your **API key secure** - it's already in `.gitignore`
- Create **separate API keys** for development and production
