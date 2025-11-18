# 🚀 Streamlit Cloud Deployment Checklist

Follow this step-by-step guide to deploy your Crypto Analyzer to Streamlit Cloud.

---

## ✅ Pre-Deployment Checklist

### 1. Verify Files Are Ready

- [x] `requirements.txt` - All dependencies listed
- [x] `.streamlit/config.toml` - App configuration
- [x] `.gitignore` - Protects sensitive data
- [x] `dashboard.py` - Main app file
- [x] `README.md` - Documentation
- [ ] `.env` file is in `.gitignore` (should NOT be committed!)

### 2. Test Locally

```bash
# Make sure app runs without errors
streamlit run dashboard.py
```

**Test these features:**
- [  ] Homepage loads
- [ ] Can analyze a cryptocurrency
- [ ] News fetching works
- [ ] AI recommendation generates (with API key)
- [ ] Performance tracking page loads

---

## 📤 Step 1: Push to GitHub

### 1.1 Initialize Git (if not done)

```bash
cd /Users/nghiadang/AIProjects/crypto_monitor
git init
```

### 1.2 Add files

```bash
git add .
```

### 1.3 Commit

```bash
git commit -m "Initial commit - Crypto Analyzer with AI"
```

### 1.4 Create GitHub Repository

1. Go to: https://github.com/new
2. Repository name: `crypto-analyzer` (or your choice)
3. Description: "AI-powered cryptocurrency trading analyzer"
4. Visibility: **Public** (required for Streamlit free tier)
5. **DO NOT** check "Initialize with README"
6. Click **"Create repository"**

### 1.5 Connect and Push

```bash
# Replace YOUR_USERNAME with your GitHub username
git remote add origin https://github.com/YOUR_USERNAME/crypto-analyzer.git
git branch -M main
git push -u origin main
```

**Verify:** Go to your GitHub repo URL and see if all files are there

---

## ☁️ Step 2: Deploy to Streamlit Cloud

### 2.1 Access Streamlit Cloud

1. Visit: https://share.streamlit.io
2. Click **"Sign in"**
3. Sign in with **GitHub**
4. Authorize Streamlit Cloud

### 2.2 Create New App

1. Click **"New app"** button
2. Fill in details:
   - **Repository:** Select `YOUR_USERNAME/crypto-analyzer`
   - **Branch:** `main`
   - **Main file path:** `dashboard.py`
   - **App URL:** Choose a custom subdomain (e.g., `my-crypto-analyzer`)

### 2.3 Configure Secrets (CRITICAL!)

1. Click **"Advanced settings"**
2. Click **"Secrets"** tab
3. Add your OpenAI API key:

```toml
OPENAI_API_KEY = "sk-proj-your-actual-api-key-here"
```

4. Click **"Save"**

**⚠️ IMPORTANT:** Don't forget this step or the AI features won't work!

### 2.4 Deploy

1. Click **"Deploy!"** button
2. Wait 2-3 minutes for build & deployment
3. Watch the logs for any errors

---

## 🎉 Step 3: Verify Deployment

### 3.1 Check Your Live App

Your app URL will be: `https://your-app-name.streamlit.app`

### 3.2 Test Features

- [ ] App loads successfully
- [ ] Can navigate between pages
- [ ] Can analyze a cryptocurrency (e.g., Bitcoin)
- [ ] News sentiment works
- [ ] AI recommendation generates
- [ ] Performance tracking page loads
- [ ] Charts and visualizations display correctly

### 3.3 Common Issues & Fixes

**Issue: "OpenAI API key not found"**
- Fix: Go to app settings → Secrets → Add `OPENAI_API_KEY`

**Issue: "Module not found"**
- Fix: Check `requirements.txt` has all dependencies
- Re-deploy after updating

**Issue: App crashes on startup**
- Fix: Check deployment logs for error details
- Usually missing dependency or syntax error

---

## 🔧 Post-Deployment Configuration

### Update App Settings

1. Go to your app dashboard on Streamlit Cloud
2. Click **"Settings"** (gear icon)
3. Configure:
   - **App URL**: Can change subdomain
   - **Secrets**: Update API keys if needed
   - **Resources**: Monitor usage

### Monitor Performance

- **Logs**: Check for errors/warnings
- **Analytics**: See visitor count (if enabled)
- **Resource usage**: Free tier limits

---

## 📊 Understanding Streamlit Cloud Limits

### Free Tier Includes:
✅ Unlimited public apps
✅ 1GB RAM per app
✅ Shared CPU
✅ Community support
✅ HTTPS enabled
✅ Automatic deploys from GitHub

### Limitations:
❌ Apps sleep after inactivity (wake up on visit)
❌ No persistent file storage (use external DB)
❌ Limited CPU/RAM
❌ Public apps only (private requires paid plan)

### For Production Use:
- Upgrade to Streamlit Cloud Pro ($20/month)
- Or self-host on AWS/GCP/Azure/Digital Ocean

---

## 🔄 Update Your Deployed App

Whenever you make code changes:

```bash
# Make changes locally
git add .
git commit -m "Update: description of changes"
git push
```

Streamlit Cloud **auto-deploys** from your main branch!

---

## 📱 Share Your App

Once deployed, share your app URL:
- `https://your-app-name.streamlit.app`

**Tips:**
- Add to your GitHub README
- Share on social media
- Add to your portfolio
- Share with trading communities

---

## 🆘 Troubleshooting

### App Won't Deploy

1. **Check logs** - Look for error messages
2. **Verify requirements.txt** - All packages listed with versions
3. **Test locally first** - Make sure it runs on your machine
4. **Check file paths** - All paths should be relative, not absolute

### App Deployed but Features Don't Work

1. **Check Secrets** - Is `OPENAI_API_KEY` set correctly?
2. **Check API limits** - CoinGecko/OpenAI rate limits
3. **Check logs** - Look for runtime errors
4. **Test features one by one** - Isolate the problem

### Data Not Persisting

- **Expected behavior** on free tier
- **Solution**: Use external database (PostgreSQL, MongoDB)
- **Workaround**: Accept data resets or upgrade to paid plan

### App is Slow

- **Normal** on free tier (shared resources)
- **Optimize**: Reduce API calls, cache data, optimize code
- **Upgrade**: Consider paid plan for better performance

---

## ✅ Deployment Complete!

Your Crypto Analyzer is now live and accessible worldwide! 🎉

**Next Steps:**
- Share with friends and get feedback
- Monitor usage and errors
- Add new features and improvements
- Consider monetization (if building a product)

---

## 📞 Support

**Streamlit Cloud Issues:**
- Docs: https://docs.streamlit.io/streamlit-community-cloud
- Forum: https://discuss.streamlit.io
- Status: https://streamlitstatus.com

**App Issues:**
- Check your GitHub repository issues
- Review app logs in Streamlit Cloud
- Test locally to isolate problems

---

**Happy Deploying! 🚀**
