# 🚀 Deployment Guide

## Streamlit Cloud Deployment

### Step 1: Prepare Your Repository

1. Ensure all files are committed:
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. Verify required files are present:
   - ✅ `app_streamlit.py`
   - ✅ `requirements.txt`
   - ✅ `README.md`
   - ✅ `.streamlit/config.toml`
   - ✅ `.env.example`

### Step 2: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click **"New app"**
4. Fill in:
   - **Repository**: Your GitHub repo
   - **Branch**: `main` (or `master`)
   - **Main file**: `app_streamlit.py`
5. Click **"Deploy"**

### Step 3: Add Secrets (API Keys)

1. In Streamlit Cloud dashboard, go to **"Settings"** → **"Secrets"**
2. Add your Gemini API key:
   ```toml
   GEMINI_API_KEY = "your_actual_api_key_here"
   ```
3. Save and the app will restart automatically

### Step 4: Optional - Add Dataset

If you want to include the dataset:
- Upload `Amazon_Reviews.csv` to your repo (if < 100MB)
- Or host it elsewhere and update the code to fetch it

---

## Local Deployment

### Option 1: Standard Run
```bash
streamlit run app_streamlit.py
```

### Option 2: Custom Port
```bash
streamlit run app_streamlit.py --server.port 8501
```

### Option 3: Production Mode
```bash
streamlit run app_streamlit.py --server.headless true --server.port 8501
```

---

## Environment Setup for Production

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables:**
   ```bash
   export GEMINI_API_KEY="your_key_here"
   ```
   
   Or use `.env` file (not recommended for production)

3. **Run:**
   ```bash
   streamlit run app_streamlit.py
   ```

---

## Docker Deployment (Optional)

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app_streamlit.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:
```bash
docker build -t review-analyzer .
docker run -p 8501:8501 -e GEMINI_API_KEY=your_key review-analyzer
```

---

## Requirements for Deployment

- ✅ Python 3.8+
- ✅ All packages in `requirements.txt`
- ✅ Gemini API key
- ✅ `Amazon_Reviews.csv` (optional, for comparison features)

---

## Troubleshooting Deployment

### Issue: App won't start on Streamlit Cloud
- Check `requirements.txt` has all dependencies
- Verify `app_streamlit.py` is the main file
- Check logs in Streamlit Cloud dashboard

### Issue: API key not working
- Verify secrets are set correctly
- Check API key is valid
- Ensure no extra quotes or spaces

### Issue: Dataset not loading
- Verify file is in repository or accessible
- Check file permissions
- App works without dataset (comparison features disabled)

---

**Your app is deployment-ready! 🚀**

