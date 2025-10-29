# 🎯 Product Review Analyzer

**An Interactive NLP-Powered Web Application for Analyzing Product Reviews**

[![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Gemini AI](https://img.shields.io/badge/Powered%20by-Gemini%202.5%20Flash-yellow.svg)](https://ai.google.dev/)

---

## ✨ Features

- 🤖 **AI-Powered Sentiment Analysis** using Gemini 2.5 Flash
- 🎯 **Aspect-Based Breakdown** (Delivery, Product Quality, Customer Service, etc.)
- 📊 **Visual Summaries** with word clouds and interactive charts
- 📈 **Dataset Comparison** with 21,000+ Amazon reviews
- 📝 **Descriptive Insights** with comprehensive AI-generated summaries
- 🎨 **Beautiful UI** built with Streamlit

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd product
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up Gemini API Key

Create a `.env` file in the project root:
```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

Get your API key from: [Google AI Studio](https://makersuite.google.com/app/apikey)

### 4. Run the Application
```bash
streamlit run app_streamlit.py
```

The app will open at `http://localhost:8501`

---

## 📋 Requirements

- Python 3.8 or higher
- Gemini API key (free tier available)
- See `requirements.txt` for all dependencies

---

## 📁 Project Structure

```
product/
├── app_streamlit.py          # Main Streamlit application
├── Amazon_Reviews.csv         # Dataset (21K+ reviews)
├── requirements.txt           # Python dependencies
├── .env                      # API keys (create from .env.example)
├── .env.example              # Template for API key
├── .gitignore                # Git ignore rules
│
├── src/                      # Source code
│   ├── __init__.py
│   ├── gemini_service.py     # Gemini API wrapper
│   └── utils.py              # Utility functions
│
├── config/                   # Configuration
│   └── config.yaml           # App settings
│
└── README.md                 # This file
```

---

## 🎯 Usage

1. **Enter Review**: Type or paste a product review in the text box
2. **Click Example**: Use sidebar examples (Positive/Negative/Neutral) to auto-fill
3. **Analyze**: Click "Analyze Review" button
4. **View Results**: Explore 5 tabs with comprehensive analysis

### Example Reviews

Click any example button in the sidebar:
- 🟢 **Example 1**: Positive reviews
- 🔴 **Example 2**: Negative reviews  
- 🟡 **Example 3**: Neutral reviews

---

## 📊 What You Get

### Summary Tab
- Overall sentiment (Positive/Negative/Neutral)
- AI-powered analysis with visual cards
- Key insights and metrics

### Detailed Analysis Tab
- Full text processing details
- Sentiment breakdown
- Emotion detection
- Key phrases extraction

### Dataset Comparison Tab
- Compare with 21,000+ reviews
- Sentiment distribution charts
- Statistical insights

### Aspects Tab
- Aspect-based sentiment (Delivery, Product, Service, etc.)
- Specific issue identification
- Detailed breakdown

### Visualizations Tab
- Word clouds
- Sentiment distribution charts
- Interactive pie charts

---

## 🔧 Configuration

### Environment Variables

Create `.env` file:
```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

### Dataset

Place `Amazon_Reviews.csv` in the project root. The app will load it automatically for comparison.

---

## 🌐 Deployment

### Streamlit Cloud Deployment

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Set main file: `app_streamlit.py`
   - Add secrets: `GEMINI_API_KEY` (your API key)

3. **Set Environment Variables**
   - In Streamlit Cloud dashboard
   - Go to "Settings" → "Secrets"
   - Add: `GEMINI_API_KEY = "your_key_here"`

### Local Deployment

```bash
streamlit run app_streamlit.py --server.port 8501
```

---

## 🛠️ Technologies Used

- **Streamlit** - Web interface
- **Google Gemini 2.5 Flash** - AI analysis
- **NLTK** - NLP processing
- **Plotly** - Interactive charts
- **WordCloud** - Text visualization
- **Pandas** - Data processing
- **NumPy** - Numerical computing

---

## 📝 Features Breakdown

### AI Analysis Features
- ✅ Multi-dimensional sentiment analysis
- ✅ Emotion detection (Joy, Anger, Satisfaction, etc.)
- ✅ Aspect extraction (Delivery, Product, Service)
- ✅ Review summarization
- ✅ Key phrase identification
- ✅ Confidence scoring

### Visualization Features
- ✅ Color-coded sentiment indicators
- ✅ Word clouds with sentiment-based colors
- ✅ Interactive Plotly charts
- ✅ Dataset comparison visualizations
- ✅ Progress bars for metrics

---

## 🔐 Security

- API keys stored in `.env` (gitignored)
- Never commit sensitive data
- Use Streamlit secrets for deployment

---

## 📚 How It Works

1. **Text Input**: User enters or selects a review
2. **NLP Processing**: Text is cleaned and preprocessed
3. **Gemini AI Analysis**: Advanced sentiment and aspect analysis
4. **Dataset Comparison**: Compares with 21K+ reviews
5. **Visualization**: Generates charts and word clouds
6. **Results Display**: Comprehensive analysis in 5 tabs

---

## 🐛 Troubleshooting

### Issue: Gemini API not working
- Check `.env` file has correct API key
- Verify API key is valid at [makersuite.google.com](https://makersuite.google.com/app/apikey)

### Issue: Dataset not loading
- Ensure `Amazon_Reviews.csv` is in project root
- Check file permissions

### Issue: Import errors
- Run: `pip install -r requirements.txt`
- Check Python version (3.8+)

---

## 📈 Dataset Information

- **Source**: Amazon Customer Reviews
- **Total Reviews**: 21,055
- **Date Range**: 2007-2024
- **Countries**: 149 countries represented
- **Sentiment Distribution**:
  - Negative: 68.15%
  - Positive: 27.64%
  - Neutral: 4.20%

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

This project is open source and available for educational purposes.

---

## 🎉 Acknowledgments

- Google Gemini AI for sentiment analysis
- Streamlit for the web framework
- Amazon for the review dataset

---

## 📞 Support

For issues or questions:
- Check the [Troubleshooting](#-troubleshooting) section
- Review the code comments
- Open an issue on GitHub

---

**Built with ❤️ using Gemini AI, NLP, and Streamlit**
