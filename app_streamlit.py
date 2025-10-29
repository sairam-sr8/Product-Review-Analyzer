"""
Interactive Review Analyzer Frontend - Streamlit Version
A comprehensive NLP-powered web application for analyzing product reviews
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re
import pickle
import os
from typing import Dict, List, Tuple
import time
import io
from PIL import Image

# Import Gemini service
from src.gemini_service import get_gemini_service
from src.utils import parse_gemini_json_response, combine_sentiment_results

# NLP processing
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Download NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet', quiet=True)

# Page config
st.set_page_config(
    page_title="Product Review Analyzer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #6366f1;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #64748b;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sentiment-positive {
        color: #10b981;
        font-weight: bold;
        font-size: 1.5rem;
    }
    .sentiment-negative {
        color: #ef4444;
        font-weight: bold;
        font-size: 1.5rem;
    }
    .sentiment-neutral {
        color: #f59e0b;
        font-weight: bold;
        font-size: 1.5rem;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f1f5f9;
        border-left: 4px solid #6366f1;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'gemini_service' not in st.session_state:
    try:
        st.session_state.gemini_service = get_gemini_service()
        st.session_state.gemini_available = True
    except Exception as e:
        st.session_state.gemini_service = None
        st.session_state.gemini_available = False
        st.session_state.gemini_error = str(e)

if 'dataset' not in st.session_state:
    st.session_state.dataset = None
    st.session_state.dataset_stats = None
    st.session_state.dataset_loaded = False

# Text preprocessing functions
def clean_text(text):
    """Clean text for analysis"""
    if pd.isna(text) or not text:
        return ""
    text = str(text).lower()
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\S+@\S+', '', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

def preprocess_text(text):
    """Advanced text preprocessing"""
    if not text:
        return ""
    tokens = word_tokenize(text)
    processed = [
        lemmatizer.lemmatize(token) 
        for token in tokens 
        if token not in stop_words and len(token) > 2
    ]
    return ' '.join(processed)

# Load dataset function
@st.cache_data
def load_dataset():
    """Load the Amazon reviews dataset"""
    try:
        dataset = pd.read_csv('Amazon_Reviews.csv')
        
        def extract_rating(rating_text):
            if pd.isna(rating_text):
                return np.nan
            match = re.search(r'Rated (\d+)', str(rating_text))
            if match:
                return int(match.group(1))
            return np.nan
        
        dataset['Rating_Numeric'] = dataset['Rating'].apply(extract_rating)
        dataset = dataset.dropna(subset=['Review Text', 'Rating_Numeric'])
        dataset['Sentiment'] = dataset['Rating_Numeric'].apply(
            lambda x: 'Negative' if x <= 2 else ('Neutral' if x == 3 else 'Positive')
        )
        
        stats = {
            'total_reviews': len(dataset),
            'avg_rating': dataset['Rating_Numeric'].mean(),
            'sentiment_dist': dataset['Sentiment'].value_counts().to_dict()
        }
        
        return dataset, stats
    except Exception as e:
        st.error(f"Error loading dataset: {e}")
        return None, None

# Main analysis function
def analyze_review(review_text: str) -> Dict:
    """Comprehensive review analysis"""
    if not review_text or len(review_text.strip()) < 10:
        return {'error': 'Please enter a review with at least 10 characters.'}
    
    results = {
        'review_text': review_text,
        'gemini_analysis': None,
        'sentiment': None,
        'aspects': None,
        'summary': None,
        'wordcloud_fig': None,
        'dataset_comparison': None
    }
    
    cleaned_text = clean_text(review_text)
    processed_text = preprocess_text(cleaned_text)
    
    # Gemini Analysis
    if st.session_state.gemini_available and st.session_state.gemini_service:
        try:
            with st.spinner("🤖 Analyzing with Gemini AI..."):
                gemini_sentiment = st.session_state.gemini_service.analyze_sentiment(
                    review_text, detailed=True
                )
                results['gemini_analysis'] = gemini_sentiment['gemini_response']
                
                gemini_aspects = st.session_state.gemini_service.extract_aspects(review_text)
                results['aspects'] = gemini_aspects['aspects']
                
                gemini_summary = st.session_state.gemini_service.summarize_review(
                    review_text, max_length=100
                )
                results['summary'] = gemini_summary['summary']
        except Exception as e:
            st.error(f"Gemini API error: {e}")
            results['gemini_error'] = str(e)
    
    # Basic sentiment analysis (fallback)
    word_count = len(review_text.split())
    positive_words = ['good', 'great', 'excellent', 'amazing', 'love', 'perfect', 'wonderful', 'awesome', 'best']
    negative_words = ['bad', 'terrible', 'awful', 'hate', 'worst', 'poor', 'horrible', 'disappointed', 'failed']
    
    pos_count = sum(1 for word in positive_words if word in cleaned_text.lower())
    neg_count = sum(1 for word in negative_words if word in cleaned_text.lower())
    
    if not results['sentiment']:
        if pos_count > neg_count:
            results['sentiment'] = 'Positive'
        elif neg_count > pos_count:
            results['sentiment'] = 'Negative'
        else:
            results['sentiment'] = 'Neutral'
    
    # Parse Gemini response for sentiment if available
    if results.get('gemini_analysis'):
        gemini_text = results['gemini_analysis'].lower()
        if 'positive' in gemini_text and 'negative' not in gemini_text:
            results['sentiment'] = 'Positive'
        elif 'negative' in gemini_text:
            results['sentiment'] = 'Negative'
        else:
            results['sentiment'] = 'Neutral'
    
    # Create word cloud
    if len(processed_text) > 10:
        try:
            color_map = {
                'Positive': 'Greens',
                'Negative': 'Reds',
                'Neutral': 'Blues'
            }.get(results['sentiment'], 'viridis')
            
            wordcloud = WordCloud(
                width=1200, 
                height=600,
                background_color='white',
                colormap=color_map,
                max_words=100,
                relative_scaling=0.5,
                collocations=False
            ).generate(processed_text)
            
            fig, ax = plt.subplots(figsize=(14, 7))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            ax.set_title(f'Review Word Cloud - {results["sentiment"]} Sentiment', 
                        fontsize=18, fontweight='bold', pad=20)
            plt.tight_layout()
            results['wordcloud_fig'] = fig
            plt.close()
        except Exception as e:
            st.warning(f"Word cloud error: {e}")
    
    # Dataset comparison
    if not st.session_state.dataset_loaded:
        st.session_state.dataset, st.session_state.dataset_stats = load_dataset()
        if st.session_state.dataset is not None:
            st.session_state.dataset_loaded = True
    
    if st.session_state.dataset_stats:
        results['dataset_comparison'] = st.session_state.dataset_stats
    
    return results

# Streamlit UI
def main():
    st.markdown('<div class="main-header">🎯 Product Review Analyzer</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Powered by Gemini 2.5 Flash AI + NLP Algorithms</div>', unsafe_allow_html=True)
    
    # Status indicator
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.session_state.gemini_available:
            st.success("✅ Gemini API: Connected")
        else:
            st.error(f"❌ Gemini API: {st.session_state.get('gemini_error', 'Not available')}")
    
    # Sidebar
    with st.sidebar:
        st.header("📚 Example Reviews")
        st.markdown("Click any example to auto-fill text (then click Analyze):")
        
        # Example reviews with random variations
        positive_examples = [
            "I love Amazon! Great service and fast delivery. The prime membership is worth it as you can receive free 2-day shipping on most purchases. Highly recommend!",
            "Excellent shopping experience! Amazon delivered my order quickly and the product quality exceeded my expectations. Customer support was helpful when I had questions.",
            "Amazing service! Fast shipping, great prices, and easy returns. Amazon Prime is definitely worth the subscription. I shop here regularly and always have positive experiences.",
            "Outstanding platform! The vast selection, competitive prices, and reliable delivery make Amazon my go-to for online shopping. Highly satisfied customer here!"
        ]
        
        negative_examples = [
            "Terrible experience. My package was lost and customer service was unhelpful. They refused to help and were rude. Worst service ever. I will never shop here again.",
            "Very disappointed. Ordered three items, only received one. When I contacted support, they were unresponsive. Poor quality product and worse customer service.",
            "Awful experience. Package arrived damaged and they refused to accept return. Customer service hung up on me twice. Never ordering from here again.",
            "Extremely poor service. Delivery was delayed by 3 weeks, product was wrong item, and refund process is a nightmare. Would not recommend to anyone."
        ]
        
        neutral_examples = [
            "Product was okay, nothing special. Delivery was on time but quality could be better. Service is average, not great but not terrible either. It works as expected.",
            "The item arrived as described. Nothing exceptional, but it does the job. Delivery was standard, could have been faster. Overall acceptable purchase.",
            "Average experience overall. The product meets basic needs, delivery was fine, nothing to complain about but nothing outstanding either.",
            "It's alright. Does what it's supposed to do. Price is reasonable, delivery was acceptable. Not amazing but not bad. Just average."
        ]
        
        import random
        
        # Example 1: Positive
        if st.button("🟢 Example 1: Positive Review", key="example_pos", use_container_width=True):
            example = random.choice(positive_examples)
            st.session_state.review_text = example
            st.session_state.review_input = example  # Update the widget key
            st.rerun()
        
        # Example 2: Negative
        if st.button("🔴 Example 2: Negative Review", key="example_neg", use_container_width=True):
            example = random.choice(negative_examples)
            st.session_state.review_text = example
            st.session_state.review_input = example  # Update the widget key
            st.rerun()
        
        # Example 3: Neutral
        if st.button("🟡 Example 3: Neutral Review", key="example_neut", use_container_width=True):
            example = random.choice(neutral_examples)
            st.session_state.review_text = example
            st.session_state.review_input = example  # Update the widget key
            st.rerun()
        
        # Additional examples
        st.markdown("---")
        st.markdown("**More Examples:**")
        
        example_reviews = [
            ("Amazing product quality! However, delivery took longer than expected. Overall satisfied with the purchase.", "Mixed Positive"),
            ("The worst shopping experience. Charged me twice, refused refund. Customer service is terrible and unprofessional.", "Very Negative")
        ]
        
        for i, (example, label) in enumerate(example_reviews, start=4):
            if st.button(f"Example {i}: {label}", key=f"example_{i}", use_container_width=True):
                st.session_state.review_text = example
                st.session_state.review_input = example  # Update the widget key
                st.rerun()
    
    # Main input area
    st.header("📝 Enter Product Review")
    
    # Initialize session state keys if not exists
    if 'review_text' not in st.session_state:
        st.session_state.review_text = ''
    
    # Get the value - from review_input if example was clicked, otherwise from review_text
    # When example buttons are clicked, they set st.session_state.review_input
    # When user types, the widget updates st.session_state.review_input automatically
    current_value = st.session_state.get('review_input', st.session_state.get('review_text', ''))
    
    # Text area - widget with key will control its own session_state value
    review_text = st.text_area(
        "Type or paste your product review here:",
        value=current_value,
        height=150,
        key="review_input",
        placeholder="Enter your product review here..."
    )
    
    # Update review_text from widget value (but don't modify review_input - widget controls it)
    if review_text:
        st.session_state.review_text = review_text
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        analyze_button = st.button("🔍 Analyze Review", type="primary", use_container_width=True)
    
    if analyze_button:
        if not review_text or len(review_text.strip()) < 10:
            st.warning("⚠️ Please enter a review with at least 10 characters.")
        else:
            with st.spinner("🔄 Analyzing review..."):
                results = analyze_review(review_text)
            
            if 'error' in results:
                st.error(results['error'])
            else:
                # Display results in tabs
                tab1, tab2, tab3, tab4, tab5 = st.tabs([
                    "📊 Summary", 
                    "🔍 Detailed Analysis", 
                    "📈 Dataset Comparison",
                    "🎯 Aspects",
                    "🖼️ Visualizations"
                ])
                
                with tab1:
                    st.markdown("## 📊 Review Analysis Summary")
                    
                    # Sentiment indicator
                    sentiment = results.get('sentiment', 'Unknown')
                    sentiment_emoji = {
                        'Positive': '🟢',
                        'Negative': '🔴',
                        'Neutral': '🟡'
                    }.get(sentiment, '⚪')
                    
                    st.markdown(f"### {sentiment_emoji} Overall Sentiment: **{sentiment}**")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Length", f"{len(review_text)} chars")
                    with col2:
                        st.metric("Word Count", len(review_text.split()))
                    with col3:
                        st.metric("Sentiment", sentiment)
                    
                    st.markdown("### 🤖 Gemini AI Analysis")
                    if results.get('gemini_analysis'):
                        # Try to parse and display JSON beautifully
                        gemini_text = results['gemini_analysis']
                        
                        # Try to extract JSON from response
                        import json
                        json_data = None
                        
                        # Remove markdown code blocks if present
                        gemini_clean = re.sub(r'```json\s*', '', gemini_text)
                        gemini_clean = re.sub(r'```\s*', '', gemini_clean)
                        gemini_clean = gemini_clean.strip()
                        
                        # Try direct JSON parse first
                        try:
                            json_data = json.loads(gemini_clean)
                        except:
                            # Look for JSON in the response
                            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', gemini_clean, re.DOTALL)
                            if json_match:
                                try:
                                    json_data = json.loads(json_match.group())
                                except:
                                    pass
                        
                        if json_data:
                            # Beautiful visual representation
                            st.markdown("#### 📊 Sentiment Analysis Results")
                            
                            # Sentiment card
                            sent = json_data.get('sentiment', 'Unknown')
                            intensity = json_data.get('intensity', 0)
                            confidence = json_data.get('confidence', 0)
                            
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.markdown(f"""
                                <div style='padding: 15px; border-radius: 10px; background: {'#10b981' if sent == 'Positive' else ('#ef4444' if sent == 'Negative' else '#f59e0b')}; color: white; text-align: center;'>
                                    <h3 style='margin: 0; color: white;'>{sent}</h3>
                                    <p style='margin: 5px 0 0 0; font-size: 0.9em;'>Sentiment</p>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            with col2:
                                st.markdown(f"""
                                <div style='padding: 15px; border-radius: 10px; background: #6366f1; color: white; text-align: center;'>
                                    <h3 style='margin: 0; color: white;'>{intensity:.2f}</h3>
                                    <p style='margin: 5px 0 0 0; font-size: 0.9em;'>Intensity</p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Progress bar for intensity
                                st.progress(intensity)
                            
                            with col3:
                                st.markdown(f"""
                                <div style='padding: 15px; border-radius: 10px; background: #8b5cf6; color: white; text-align: center;'>
                                    <h3 style='margin: 0; color: white;'>{confidence:.2f}</h3>
                                    <p style='margin: 5px 0 0 0; font-size: 0.9em;'>Confidence</p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Progress bar for confidence
                                st.progress(confidence)
                            
                            st.markdown("---")
                            
                            # Emotions
                            emotions = json_data.get('emotions', [])
                            if emotions:
                                st.markdown("#### 😊 Detected Emotions")
                                emotion_cols = st.columns(len(emotions) if len(emotions) <= 5 else 5)
                                for i, emotion in enumerate(emotions[:5]):
                                    with emotion_cols[i % len(emotion_cols)]:
                                        st.markdown(f"""
                                        <div style='padding: 10px; border-radius: 8px; background: #1e293b; text-align: center; border: 2px solid #6366f1; color: white;'>
                                            <strong style='color: white;'>{emotion}</strong>
                                        </div>
                                        """, unsafe_allow_html=True)
                            
                            # Key Phrases
                            key_phrases = json_data.get('key_phrases', [])
                            if key_phrases:
                                st.markdown("#### 🔑 Key Phrases")
                                phrases_html = ""
                                for phrase in key_phrases[:8]:
                                    phrases_html += f'<span style="display: inline-block; padding: 8px 15px; margin: 5px; border-radius: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; font-size: 0.9em; font-weight: bold;">{phrase}</span>'
                                st.markdown(f"<div style='margin: 10px 0;'>{phrases_html}</div>", unsafe_allow_html=True)
                            
                            # Show raw JSON in expander with explanation
                            with st.expander("📄 What is JSON? Why show it?", expanded=False):
                                st.markdown("""
                                ### What is JSON?
                                **JSON** stands for JavaScript Object Notation. It's a format for storing data.
                                
                                **Why show it?**
                                - For **developers/technical users** who want to see the raw data
                                - To **verify** the AI analysis is correct
                                - For **exporting** the data to other tools
                                - To understand the **exact structure** of the analysis
                                
                                **Most users don't need to see this** - the visual cards above show everything!
                                """)
                                st.json(json_data)
                        else:
                            # Fallback: show text response
                            st.info(gemini_text)
                    else:
                        st.warning("Gemini analysis not available. Check your API key in .env file.")
                    
                    st.markdown("### 📋 Key Summary")
                    if results.get('summary'):
                        st.success(results['summary'])
                    else:
                        st.info("Summary generation in progress...")
                
                with tab2:
                    st.markdown("## 🔍 Detailed Analysis")
                    
                    with st.expander("📄 Original Review", expanded=False):
                        st.write(review_text)
                    
                    st.markdown("### 📊 Processing Details")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Cleaned Length", len(clean_text(review_text)))
                    with col2:
                        st.metric("Processed Tokens", len(preprocess_text(clean_text(review_text)).split()))
                    
                    st.markdown("### 🎯 Sentiment Breakdown")
                    st.write(f"**Primary Sentiment:** {sentiment}")
                    
                    st.markdown("### 💡 Insights")
                    if results.get('gemini_analysis'):
                        gemini_text = results['gemini_analysis']
                        
                        # Try to parse JSON
                        import json
                        
                        # Remove markdown code blocks if present
                        gemini_clean = re.sub(r'```json\s*', '', gemini_text)
                        gemini_clean = re.sub(r'```\s*', '', gemini_clean)
                        gemini_clean = gemini_clean.strip()
                        
                        json_data = None
                        # Try direct JSON parse first
                        try:
                            json_data = json.loads(gemini_clean)
                        except:
                            # Look for JSON in the response
                            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', gemini_clean, re.DOTALL)
                            if json_match:
                                try:
                                    json_data = json.loads(json_match.group())
                                except:
                                    json_data = None
                        
                        # Visual representation if JSON was successfully parsed
                        if json_data:
                            st.markdown("#### Sentiment Breakdown")
                            
                            # Create visual cards
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown("**Emotions Detected:**")
                                emotions = json_data.get('emotions', [])
                                for emotion in emotions:
                                    st.markdown(f"- 😊 {emotion}")
                            
                            with col2:
                                st.markdown("**Analysis Metrics:**")
                                intensity = json_data.get('intensity', 0)
                                confidence = json_data.get('confidence', 0)
                                st.markdown(f"- 📊 Intensity: **{intensity:.0%}**")
                                st.progress(intensity)
                                st.markdown(f"- ✅ Confidence: **{confidence:.0%}**")
                                st.progress(confidence)
                            
                            # Key phrases as badges
                            key_phrases = json_data.get('key_phrases', [])
                            if key_phrases:
                                st.markdown("**Key Phrases:**")
                                cols = st.columns(min(4, len(key_phrases)))
                                for i, phrase in enumerate(key_phrases[:4]):
                                    with cols[i % len(cols)]:
                                        st.markdown(f'<div style="padding: 8px; margin: 5px; border-radius: 5px; background: #1e293b; text-align: center; font-size: 0.85em; color: white; border: 2px solid #6366f1;"><b style="color: white;">{phrase}</b></div>', unsafe_allow_html=True)
                        else:
                            st.write(gemini_text)
                    else:
                        st.info("Detailed analysis from Gemini API...")
                
                with tab3:
                    st.markdown("## 📈 Dataset Comparison")
                    
                    if results.get('dataset_comparison'):
                        comp = results['dataset_comparison']
                        dist = comp['sentiment_dist']
                        
                        st.markdown("### Dataset Statistics")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total Reviews", f"{comp['total_reviews']:,}")
                        with col2:
                            st.metric("Avg Rating", f"{comp['avg_rating']:.2f}/5.0")
                        with col3:
                            user_sent = dist.get(sentiment, 0)
                            st.metric(f"{sentiment} Reviews", f"{user_sent:,}")
                        
                        # Sentiment distribution chart
                        fig = go.Figure(data=[
                            go.Bar(
                                x=list(dist.keys()),
                                y=list(dist.values()),
                                marker_color=['red', 'orange', 'green'],
                                text=[f"{v:,}" for v in dist.values()],
                                textposition='auto'
                            )
                        ])
                        fig.update_layout(
                            title='Dataset Sentiment Distribution',
                            xaxis_title='Sentiment',
                            yaxis_title='Number of Reviews',
                            height=400,
                            template='plotly_white'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        st.markdown("### Your Review in Context")
                        total = comp['total_reviews']
                        your_count = dist.get(sentiment, 0)
                        percentage = (your_count / total * 100) if total > 0 else 0
                        st.info(f"Your review is classified as **{sentiment}**, which represents {your_count:,} reviews ({percentage:.1f}%) in the dataset.")
                    else:
                        st.warning("Dataset not loaded. Ensure 'Amazon_Reviews.csv' is in the project folder.")
                
                with tab4:
                    st.markdown("## 🎯 Aspect Breakdown")
                    
                    st.markdown("""
                    ### What are Aspects?
                    **Aspects** are the specific areas or topics mentioned in the review. Instead of just saying 
                    "the review is positive," we break it down into specific parts:
                    
                    - 📦 **Delivery/Shipping**: How fast was delivery? Was it on time?
                    - 🛍️ **Product Quality**: Was the product good quality? Did it meet expectations?
                    - 👨‍💼 **Customer Service**: How was the support? Were they helpful?
                    - 💰 **Pricing**: Was it good value for money?
                    - 🌐 **Website/App**: How easy was the ordering process?
                    - 💳 **Billing/Payment**: Any payment issues?
                    
                    This helps you understand **exactly what** the customer is happy or unhappy about!
                    """)
                    
                    if results.get('aspects'):
                        st.markdown("### 📊 Extracted Aspects from Your Review")
                        st.info(results['aspects'])
                    else:
                        st.info("Aspect extraction using Gemini API...")
                        st.write("**Example:** If someone says 'Delivery was great BUT product quality was poor', "
                                "you'll see: Delivery = Positive, Product Quality = Negative")
                
                with tab5:
                    st.markdown("## 🖼️ Visualizations")
                    
                    # Word Cloud
                    if results.get('wordcloud_fig'):
                        st.markdown("### Word Cloud")
                        try:
                            fig = results['wordcloud_fig']
                            st.pyplot(fig, use_container_width=True, clear_figure=True)
                        except Exception as e:
                            st.error(f"Error displaying word cloud: {e}")
                            st.info("Word cloud generation encountered an issue")
                    else:
                        st.info("Word cloud will appear here for longer reviews")
                    
                    # Additional charts if dataset available
                    if results.get('dataset_comparison'):
                        st.markdown("### Sentiment Comparison")
                        dist = results['dataset_comparison']['sentiment_dist']
                        
                        # Pie chart with explanation
                        st.markdown("""
                        ### 📊 Why This Pie Chart?
                        This chart shows how your review compares to **21,000+ Amazon reviews** in the dataset:
                        - See the **overall sentiment distribution** (what % are positive/negative/neutral)
                        - Understand where **your review fits** in the bigger picture
                        - Helps identify if your review matches **common patterns**
                        
                        **Example:** If 68% of reviews are negative, and yours is also negative, 
                        it shows you're part of a larger trend (maybe there's a real problem to address).
                        """)
                        
                        fig_pie = go.Figure(data=[
                            go.Pie(
                                labels=list(dist.keys()),
                                values=list(dist.values()),
                                marker_colors=['red', 'orange', 'green'],
                                hole=0.4
                            )
                        ])
                        fig_pie.update_layout(
                            title='Dataset Sentiment Distribution (21K+ Reviews)',
                            height=400
                        )
                        st.plotly_chart(fig_pie, use_container_width=True)

if __name__ == "__main__":
    main()

