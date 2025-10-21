# API Key Configuration Guide

## Where to Add Your API Key

You have **three options** for configuring your UniFi API key. Choose the one that works best for your workflow:

---

## Option 1: Using `config.py` (Recommended for Scripts)

This is the simplest approach for running example scripts.

### Steps:

1. **Copy the example configuration file**:

   ```powershell
   Copy-Item config.example.py config.py
   ```

2. **Edit `config.py`** and replace the placeholder with your actual API key:

   ```python
   API_KEY = "your-actual-api-key-here"
   ```

3. **Done!** The examples will automatically use this file. It's already in `.gitignore` so it won't be committed.

### Usage:

```python
import config
from src.unifi_client import UniFiClient

client = UniFiClient(config.API_KEY)
```

---

## Option 2: Using `.env` File (More Secure)

This approach is better for production use and keeping secrets separate from code.

### Steps:

1. **Copy the example environment file**:

   ```powershell
   Copy-Item .env.example .env
   ```

2. **Edit `.env`** and add your API key:

   ```bash
   UNIFI_API_KEY=your-actual-api-key-here
   UNIFI_BASE_URL=https://api.ui.com/v1
   ```

3. **Use the config loader** in your code:

   ```python
   from src.config_loader import load_api_key, get_base_url
   from src.unifi_client import UniFiClient

   api_key = load_api_key()
   client = UniFiClient(api_key, get_base_url())
   ```

---

## Option 3: Environment Variable (Most Secure)

Set the API key as an environment variable - best for CI/CD or shared environments.

### PowerShell (Current Session):

```powershell
$env:UNIFI_API_KEY = "your-actual-api-key-here"
```

### PowerShell (Permanent - User Scope):

```powershell
[System.Environment]::SetEnvironmentVariable('UNIFI_API_KEY', 'your-actual-api-key-here', 'User')
```

### Usage:

Same as Option 2 - use the config loader which checks environment variables first.

---

## Priority Order

The `config_loader` utility checks for your API key in this order:

1. **Environment variable** `UNIFI_API_KEY` (highest priority)
2. **config.py** file
3. **.env** file (lowest priority)

This allows you to override the configuration as needed without modifying files.

---

## Getting Your API Key

### For UniFi Site Manager (Cloud):

1. Go to https://unifi.ui.com
2. Navigate to **Settings** → **API**
3. Click **Create New API Key**
4. Give it a descriptive name (e.g., "Python API Client")
5. Copy the key immediately (you can't view it again!)

### For Local UniFi Controller:

If you're using a local controller (not the cloud), you'll need username/password authentication instead. See the `.env.example` file for those settings.

---

## Security Best Practices

✅ **DO:**

- Use `.env` or environment variables for production
- Keep API keys out of version control
- Rotate API keys regularly
- Use separate keys for different environments (dev/prod)
- Set appropriate permissions on `config.py` and `.env` files

❌ **DON'T:**

- Commit `config.py` or `.env` to git (they're in `.gitignore`)
- Share API keys in chat, email, or documentation
- Use production keys in development
- Hardcode keys in your scripts

---

## Testing Your Configuration

Run the example script to verify your API key is configured correctly:

```powershell
python examples/api_key_example.py
```

You should see:

```
✓ Connected to https://api.ui.com/v1
```

---

## Troubleshooting

### "API key not found!"

- Make sure you've created either `config.py` or `.env`
- Check that the API key is not empty or still set to placeholder text
- Verify the file is in the root of the project (same directory as `config.example.py`)

### "Authentication failed"

- Verify your API key is correct (copy/paste it again)
- Check that you haven't accidentally added spaces or quotes around the key
- Ensure your API key hasn't been revoked or expired

### "Wrong authentication method"

- This project supports **API key authentication** (for cloud)
- If using a local controller, you need username/password (see `.env.example`)
