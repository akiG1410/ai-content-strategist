# 🚀 GitHub & Streamlit Cloud Deployment Guide

## 📋 Complete Deployment Checklist

### ✅ Pre-Deployment Verification

Run these commands to verify everything is ready:

```bash
# 1. Check for secrets in repository
./scripts/check_secrets.sh

# 2. Run security tests
./venv/bin/python scripts/test_security.py

# 3. Verify git status
git status
```

**Expected Results:**
- ✅ No secrets in tracked files
- ✅ All security tests pass
- ✅ Only safe files are staged

---

## 🔐 Step 1: Create GitHub Repository

### Option A: Using GitHub Web Interface

1. Go to [github.com/new](https://github.com/new)
2. Fill in repository details:
   - **Repository name**: `ai-content-strategist`
   - **Description**: `AI-powered content marketing strategy generator using CrewAI and Claude`
   - **Visibility**: Choose **Public** or **Private**
   - **DO NOT** initialize with README (we have one)
3. Click **Create repository**

### Option B: Using GitHub CLI

```bash
# Install GitHub CLI if needed: https://cli.github.com/

# Create repository
gh repo create ai-content-strategist \
  --public \
  --description "AI-powered content marketing strategy generator using CrewAI and Claude" \
  --source=. \
  --push

# If you want it private instead:
gh repo create ai-content-strategist \
  --private \
  --description "AI-powered content marketing strategy generator using CrewAI and Claude" \
  --source=. \
  --push
```

---

## 📤 Step 2: Push to GitHub

### First Time Push

```bash
# 1. Commit all files
git commit -m "Initial commit: AI Content Marketing Strategist with security features

- Complete Streamlit web application
- CrewAI multi-agent system
- Enterprise-grade security (XSS protection, rate limiting, authentication)
- DOCX and XLSX document generation
- Comprehensive testing and deployment scripts"

# 2. Add remote repository (replace with your username)
git remote add origin https://github.com/akig1410/ai-content-strategist.git

# 3. Push to main branch
git push -u origin main
```

### If You Get Errors

**Error: "remote origin already exists"**
```bash
git remote remove origin
git remote add origin https://github.com/akig1410/ai-content-strategist.git
git push -u origin main
```

**Error: "branch 'main' does not exist"**
```bash
git branch -M main
git push -u origin main
```

**Error: "Authentication failed"**
- Use a Personal Access Token instead of password
- Generate at: [github.com/settings/tokens](https://github.com/settings/tokens)
- Scopes needed: `repo` (full control)

---

## ☁️ Step 3: Deploy to Streamlit Cloud

### A. Sign Up / Login

1. Go to [share.streamlit.io](https://share.streamlit.io/)
2. Click **Sign in with GitHub**
3. Authorize Streamlit Cloud to access your repositories

### B. Create New App

1. Click **"New app"** button
2. Fill in the deployment form:

| Field | Value |
|-------|-------|
| **Repository** | `akig1410/ai-content-strategist` |
| **Branch** | `main` |
| **Main file path** | `src/streamlit_app.py` |
| **App URL** (optional) | `ai-content-strategist` (or your choice) |

3. Click **"Advanced settings"** (optional):
   - **Python version**: `3.11`
   - **Custom domain**: (if you have one)

4. Click **"Deploy!"**

### C. Configure Secrets

**CRITICAL**: You must add your API key before the app will work!

1. While your app is building, click **"Settings"** (⚙️ icon)
2. Navigate to **"Secrets"** section
3. Add your secrets in TOML format:

```toml
# REQUIRED: Your OpenRouter API key
OPENROUTER_API_KEY = "sk-or-v1-YOUR_ACTUAL_KEY_HERE"

# OPTIONAL: Enable password protection for beta testing
# BETA_PASSWORD = "your-secure-password-here"

# OPTIONAL: Force production mode (enables strict rate limiting)
# ENVIRONMENT = "production"

# OPTIONAL: Custom rate limiting (default: 5 requests per hour)
# MAX_REQUESTS = 10
# WINDOW_SECONDS = 3600
```

4. Click **"Save"**
5. The app will automatically restart with the new secrets

### D. Get Your OpenRouter API Key

If you don't have an API key yet:

1. Go to [OpenRouter Keys](https://openrouter.ai/keys)
2. Sign up or log in
3. Click **"Create Key"**
4. Copy your key (starts with `sk-or-v1-`)
5. Add credits to your account

**Estimated Cost:**
- ~$0.01-0.03 per strategy generation
- $5 credit lasts for 150-500 generations

---

## 🧪 Step 4: Test Your Deployment

### Wait for Build to Complete

1. Watch the build logs in Streamlit Cloud
2. Build typically takes **2-3 minutes**
3. Look for: `"You can now view your Streamlit app in your browser"`

### Test the Application

1. **Visit your app URL**: `https://share.streamlit.io/akig1410/ai-content-strategist/main/src/streamlit_app.py`
   - Or your custom domain if configured

2. **Test Authentication** (if enabled):
   - Enter your `BETA_PASSWORD`
   - Verify login works

3. **Test Full Workflow**:
   - Go through all 8 steps
   - Enter sample brand data
   - Generate strategies (Phase 1)
   - Select a strategy
   - Generate calendar (Phase 2)
   - Download all documents

4. **Test Rate Limiting**:
   - Try generating 6 strategies in a row
   - Should see rate limit message after 5th

5. **Test Security**:
   - Try entering `<script>alert('xss')</script>` in Brand Name
   - Should be rejected with validation error

### Verify Documents

Check that all downloads work:
- ✅ Strategy DOCX opens in Word
- ✅ Calendar DOCX has 20-25 content pieces
- ✅ Excel XLSX has 4 tabs
- ✅ All content is brand-specific (not generic)

---

## 🔄 Step 5: Update Your Deployment

### Make Changes Locally

```bash
# 1. Make your changes to the code
# Example: edit src/streamlit_app.py

# 2. Test locally
streamlit run src/streamlit_app.py

# 3. Commit changes
git add .
git commit -m "Description of your changes"

# 4. Push to GitHub
git push origin main
```

### Automatic Redeployment

- Streamlit Cloud **automatically redeploys** when you push to GitHub
- Watch the **"Manage app"** page for build status
- No manual intervention needed!

### Manual Reboot

If needed, you can manually reboot:

1. Go to **"Manage app"** page
2. Click **three dots** (⋮) menu
3. Select **"Reboot app"**

---

## 🛡️ Security Checklist

Before deploying, verify:

- [ ] ✅ `.env` file is NOT in git repository
- [ ] ✅ `.streamlit/secrets.toml` is NOT in git repository
- [ ] ✅ `.streamlit/secrets.toml.example` IS in git repository
- [ ] ✅ `.gitignore` properly configured
- [ ] ✅ No API keys in code
- [ ] ✅ No hardcoded passwords
- [ ] ✅ All security tests pass
- [ ] ✅ Secrets configured in Streamlit Cloud

### Run Security Check

```bash
./scripts/check_secrets.sh
```

**Must show:**
```
✅ All security checks passed!
Your repository is secure.
```

---

## 📊 Monitoring Your App

### Streamlit Cloud Dashboard

Monitor your app at: [share.streamlit.io](https://share.streamlit.io/)

**Key Metrics:**
- **Viewers**: Current active users
- **Uptime**: App availability
- **Errors**: Runtime errors
- **Logs**: Application logs

### View Logs

1. Go to **"Manage app"** page
2. Click **"Logs"** tab
3. See real-time application logs
4. Filter by log level (INFO, WARNING, ERROR)

### Check Resource Usage

- **Memory**: Streamlit Cloud provides 1GB RAM
- **CPU**: Shared CPU resources
- **Storage**: Temporary files only (auto-deleted)

---

## 🐛 Troubleshooting

### Build Fails

**Error: "ModuleNotFoundError"**
- Check `requirements.txt` is complete
- Verify all dependencies are listed

**Error: "No module named 'src'"**
- Verify entry point is `src/streamlit_app.py`
- Check all `__init__.py` files exist

### Runtime Errors

**Error: "OPENROUTER_API_KEY not found"**
- Add API key in Streamlit Cloud Secrets
- Format: `OPENROUTER_API_KEY = "sk-or-v1-..."`

**Error: "Rate limit exceeded"**
- Wait for rate limit window to reset
- Or increase `MAX_REQUESTS` in secrets

**Error: "Authentication failed"**
- Remove `BETA_PASSWORD` from secrets to disable auth
- Or verify password is correct

### App is Slow

- **Phase 1 takes 2-3 minutes**: Normal for AI generation
- **Phase 2 takes 3-4 minutes**: Normal for 20-25 content pieces
- **First load is slow**: Cold start (10-30 seconds)
- **Use caching**: Results are cached in session

### Clear Cache

Users can click **"Clear Cache & Start Fresh"** button in sidebar

---

## 🔐 Managing Secrets

### Update Secrets

1. Go to **"Manage app"** → **"Settings"** → **"Secrets"**
2. Edit the TOML file
3. Click **"Save"**
4. App automatically restarts

### Rotate API Keys

**Best Practice:** Rotate API keys every 90 days

1. Generate new key at [OpenRouter](https://openrouter.ai/keys)
2. Update secret in Streamlit Cloud
3. Test app still works
4. Delete old key from OpenRouter

### Multiple Environments

If you want dev/staging/prod environments:

```bash
# Create branches
git checkout -b staging
git push -u origin staging

git checkout -b production
git push -u origin production
```

Deploy each branch as separate Streamlit app with different secrets.

---

## 📈 Next Steps

### After Successful Deployment

1. **Share your app URL** with users
2. **Monitor usage** via Streamlit Cloud dashboard
3. **Collect feedback** from users
4. **Add analytics** (Google Analytics, etc.)
5. **Consider custom domain** for branding

### Enhancements

- Add user authentication (Auth0, Firebase)
- Implement usage analytics
- Add more export formats (PDF, PPT)
- Create API endpoints
- Add team collaboration features

### Scaling

If you need more resources:
- **Streamlit Cloud Teams**: More resources, custom domains
- **Self-hosted**: Deploy on AWS/GCP/Azure
- **Streamlit for Teams**: Enterprise features

---

## 📞 Support Resources

- **Streamlit Docs**: [docs.streamlit.io](https://docs.streamlit.io/)
- **Streamlit Cloud Docs**: [docs.streamlit.io/streamlit-cloud](https://docs.streamlit.io/streamlit-cloud)
- **Community Forum**: [discuss.streamlit.io](https://discuss.streamlit.io/)
- **GitHub Issues**: [github.com/streamlit/streamlit/issues](https://github.com/streamlit/streamlit/issues)

---

## ✅ Deployment Complete!

Your AI Content Marketing Strategist is now live! 🎉

**Share your app:**
```
https://share.streamlit.io/akig1410/ai-content-strategist/main/src/streamlit_app.py
```

Or use your custom URL if configured.

**Made with ❤️ using CrewAI and Claude**
