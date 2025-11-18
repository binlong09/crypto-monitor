# CoinGecko API Key Setup Guide

## ✅ Yes, CoinGecko Now Requires an API Key

CoinGecko changed their API policy - even the **free tier** now requires an API key.

**Good News:** The free tier is still FREE and sufficient for our needs!

---

## 🔑 Step 1: Get Your Free API Key

### Option A: Demo API (Instant, No Signup)
1. Go to: https://www.coingecko.com/en/api
2. Look for "Demo API" section
3. You might get an instant demo key

### Option B: Free Account (Recommended)
1. Go to: https://www.coingecko.com/en/api
2. Click **"Get Your Free API Key"**
3. Sign up for a free account
4. Go to your Dashboard → API Keys
5. Copy your API key (looks like: `CG-xxxxxxxxxxxxxxxxxxxx`)

**Free Tier Limits:**
- ✅ 10,000 API calls per month
- ✅ 10-30 calls per minute
- ✅ Access to all basic endpoints
- ✅ Perfect for our crypto monitor!

---

## 📝 Step 2: Add API Key to .env File

Open your `.env` file in the `crypto_monitor` directory:

```bash
# .env file
OPENAI_API_KEY=sk-your-openai-key-here
COINGECKO_API_KEY=CG-your-coingecko-key-here
```

**Example:**
```bash
OPENAI_API_KEY=sk-proj-abc123...
COINGECKO_API_KEY=CG-xyz789abc456def123...
```

---

## ✅ Step 3: Verify Setup

### Method 1: Check Settings Page
```bash
streamlit run dashboard.py
```

1. Go to **⚙️ Settings** page
2. You should see:
   - ✅ OpenAI API key configured
   - ✅ CoinGecko API key configured

### Method 2: Test with Python
```python
import os
from dotenv import load_dotenv

load_dotenv()

openai_key = os.getenv('OPENAI_API_KEY')
coingecko_key = os.getenv('COINGECKO_API_KEY')

print(f"OpenAI: {'✅ Set' if openai_key else '❌ Missing'}")
print(f"CoinGecko: {'✅ Set' if coingecko_key else '❌ Missing'}")
```

---

## 🧪 Step 4: Test the App

```bash
streamlit run dashboard.py
```

1. Go to "🔍 Analyze Individual Crypto"
2. Select BTC
3. Choose "30 Days" period
4. Click "Run Complete Analysis"

**If API key is working:**
- ✅ You'll see price charts
- ✅ Technical indicators will populate
- ✅ No 401 errors

**If API key is missing:**
- ❌ Error: "401 Unauthorized"
- ❌ Message: "CoinGecko API Authentication Error!"
- ❌ Instructions to set COINGECKO_API_KEY

---

## 🔍 What Changed in the Code

### Updated: `src/data/coingecko_client.py`
```python
class CoinGeckoClient:
    def __init__(self, api_key: Optional[str] = None):
        # Now accepts API key from env or parameter
        self.api_key = api_key or os.getenv('COINGECKO_API_KEY')

        # Adds authentication header
        if self.api_key:
            self.session.headers.update({
                'x-cg-demo-api-key': self.api_key
            })
```

### Updated: `dashboard.py`
- Added CoinGecko API key status in Settings page
- Shows clear error if key is missing
- Provides link to get free key

---

## 📊 Free Tier Usage Estimate

For our crypto monitor:

**Per Complete Analysis:**
- Market data: 1 call
- Historical prices: 1 call
- On-chain metrics: 1 call
- **Total: ~3 calls**

**Monthly Usage:**
- 10 analyses per day × 30 days = 300 analyses
- 300 × 3 calls = 900 calls
- **Well within 10,000/month limit!** ✅

---

## ❓ Troubleshooting

### "401 Unauthorized" Error
**Cause:** API key missing or invalid

**Fix:**
1. Check `.env` file has `COINGECKO_API_KEY=CG-...`
2. Restart Streamlit app
3. Verify key is correct (no extra spaces)

### "Rate Limit Exceeded"
**Cause:** Too many requests too fast

**Fix:**
- Our code has rate limiting built-in (1.5 sec delay)
- Shouldn't happen with normal use
- If it does, wait a minute and try again

### "API Key Not Detected"
**Cause:** .env file not loaded

**Fix:**
1. Ensure `.env` is in the same directory as `dashboard.py`
2. Restart Streamlit
3. Check file is named `.env` not `env.txt` or `.env.txt`

---

## 🆚 Alternative: Use Paid Tier?

**Not Recommended for This App**

The free tier (10,000 calls/month) is perfect for our use case.

**Paid tier ($129/month) only adds:**
- Higher rate limits (we don't need)
- More historical data (365 days works fine)
- Commercial license (personal use = not needed)

**Stick with free tier!** ✅

---

## 📚 Related Files

- **Code:** `src/data/coingecko_client.py` - API client with authentication
- **Config:** `.env` - Store your API keys here
- **Settings:** Dashboard → ⚙️ Settings - Check API key status

---

## ✅ Summary

1. **Get free API key** from https://www.coingecko.com/en/api
2. **Add to .env file**: `COINGECKO_API_KEY=CG-your-key`
3. **Restart app**: `streamlit run dashboard.py`
4. **Verify in Settings** page: Should show ✅

**The app will now work with technical indicators!** 📊🚀
