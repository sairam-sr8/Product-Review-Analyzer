# 🔐 How to Add API Key in Streamlit Cloud

## ⚠️ The Problem
Streamlit Cloud doesn't read `.env` files. You need to add secrets in the dashboard.

---

## ✅ Quick Fix (3 Steps)

### Step 1: Go to Your App Settings
1. Open https://share.streamlit.io
2. Sign in with GitHub
3. Click on your **Product-Review-Analyzer** app
4. Click **"⚙️ Settings"** (gear icon, top right)

### Step 2: Open Secrets Tab
1. Click **"Secrets"** in the left sidebar
2. You'll see a text editor

### Step 3: Add Your API Key
Copy and paste this **exactly**:

```toml
GEMINI_API_KEY = "AIzaSyDoJFyRrDpBz1km9h5pbvugOAUY-lWYYX4"
```

**Important:**
- ✅ Use TOML format (not JSON)
- ✅ No quotes around `GEMINI_API_KEY`
- ✅ Use quotes around the value
- ✅ No spaces before/after `=`

### Step 4: Save
1. Click **"Save"** button at the bottom
2. App will automatically restart
3. Wait 10-20 seconds
4. Refresh your browser

---

## ✅ Verify It Worked

After saving, you should see in your app:
- ✅ **"Gemini API: Connected"** (green box)
- ❌ **NOT** "Gemini API key not found" error

---

## 🔍 Screenshot Guide

**Where to find Secrets:**
```
Streamlit Cloud Dashboard
  → Your App
    → Settings (⚙️ icon)
      → Secrets (tab)
        → Text editor (add your key here)
```

---

## 📋 Your API Key

For reference, your Gemini API key:
```
AIzaSyDoJFyRrDpBz1km9h5pbvugOAUY-lWYYX4
```

**Paste this exact key in the secrets file!**

---

## 🐛 Troubleshooting

### Still seeing error?
1. **Check format**: Must be TOML, not JSON
2. **Check quotes**: Value needs quotes
3. **Check spelling**: `GEMINI_API_KEY` (all caps)
4. **Save again**: Click Save button
5. **Wait**: App takes 10-20 seconds to restart

### Wrong Format Examples:
```toml
❌ GEMINI_API_KEY=your_key          # Missing quotes
❌ "GEMINI_API_KEY" = "your_key"    # Quoted key name
❌ GEMINI_API_KEY: "your_key"       # Wrong separator
```

### Correct Format:
```toml
✅ GEMINI_API_KEY = "your_key"      # Perfect!
```

---

## ✅ Code Updated

The app now:
- ✅ Checks Streamlit secrets first (for deployment)
- ✅ Falls back to .env (for local development)
- ✅ Shows helpful error messages

**Just add the secret and you're done!** 🎉

