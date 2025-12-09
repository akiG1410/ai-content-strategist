# 🚀 Quick Deploy Commands

## ✅ Your Project is Ready!
- 39 files committed
- All security checks passed
- No secrets in repository

---

## 📤 Push to GitHub (3 commands)

```bash
# 1. Add remote repository
git remote add origin https://github.com/akig1410/ai-content-strategist.git

# 2. Push to GitHub
git push -u origin main

# 3. Done! View at: https://github.com/akig1410/ai-content-strategist
```

**⚠️ First create the repository on GitHub:**
- Go to: https://github.com/new
- Repository name: `ai-content-strategist`
- Click "Create repository" (DON'T initialize)

---

## ☁️ Deploy to Streamlit Cloud

### 1. Go to Streamlit Cloud
https://share.streamlit.io/

### 2. Fill in the Form

```
Repository:     akig1410/ai-content-strategist
Branch:         main
Main file path: src/streamlit_app.py
Python version: 3.11
```

### 3. Add Secrets

Click "Settings" → "Secrets" → Add:

```toml
OPENROUTER_API_KEY = "YOUR_REAL_KEY_HERE"
```

Get key at: https://openrouter.ai/keys

---

## ✅ That's It!

Your app will be live in 2-3 minutes at:
`https://share.streamlit.io/akig1410/ai-content-strategist`

---

For detailed instructions, see:
- **README.md** - Complete project documentation
- **DEPLOYMENT_SUMMARY.md** - Full deployment checklist
- **GITHUB_DEPLOYMENT_GUIDE.md** - Step-by-step guide

**Made with ❤️ using CrewAI and Claude**
