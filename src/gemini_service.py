"""
Gemini API Service Wrapper
Provides functions to interact with Google's Gemini API for advanced NLP tasks
"""

import os
import google.generativeai as genai
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Try to import streamlit for secrets (only if in Streamlit environment)
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    st = None

# Load environment variables (for local development)
load_dotenv()


class GeminiService:
    """Wrapper class for Gemini API operations"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini Service
        
        Args:
            api_key: Gemini API key. If None, reads from Streamlit secrets or GEMINI_API_KEY env var
        """
        # Priority: 1) Provided key, 2) Streamlit secrets, 3) Environment variable
        if api_key:
            self.api_key = api_key
        elif STREAMLIT_AVAILABLE and st:
            # Try Streamlit secrets first (for Streamlit Cloud)
            try:
                if hasattr(st, 'secrets') and 'GEMINI_API_KEY' in st.secrets:
                    self.api_key = st.secrets['GEMINI_API_KEY']
                else:
                    self.api_key = os.getenv('GEMINI_API_KEY')
            except:
                self.api_key = os.getenv('GEMINI_API_KEY')
        else:
            self.api_key = os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            error_msg = (
                "Gemini API key not found!\n\n"
                "For LOCAL development: Create .env file with GEMINI_API_KEY=your_key\n"
                "For STREAMLIT CLOUD: Add secret in app settings:\n"
                "  1. Go to your app on share.streamlit.io\n"
                "  2. Click Settings → Secrets\n"
                "  3. Add: GEMINI_API_KEY = 'your_key'\n"
                "  4. Save and restart"
            )
            raise ValueError(error_msg)
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Use model from env or default to Gemini 2.5 Flash
        model_name = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
        try:
            self.model = genai.GenerativeModel(model_name)
        except Exception as e:
            # Fallback to alternative Flash models if main one not available
            print(f"Warning: Could not load {model_name}, trying alternatives...")
            try:
                # Try other 2.5 Flash variants
                for alt_model in ['gemini-2.5-flash-preview-05-20', 'gemini-1.5-flash', 'gemini-pro']:
                    try:
                        self.model = genai.GenerativeModel(alt_model)
                        print(f"Using alternative model: {alt_model}")
                        break
                    except:
                        continue
            except:
                raise ValueError(f"Could not initialize any Gemini model. Error: {e}")
    
    def analyze_sentiment(self, text: str, detailed: bool = True) -> Dict:
        """
        Analyze sentiment using Gemini
        
        Args:
            text: Review text to analyze
            detailed: If True, returns detailed emotion analysis
        
        Returns:
            Dictionary with sentiment analysis results
        """
        if detailed:
            prompt = f"""
            Analyze the sentiment of the following customer review in detail.
            
            Review: "{text}"
            
            You MUST respond with ONLY valid JSON format, no additional text or explanation.
            
            Provide the following as a JSON object:
            - "sentiment": Overall sentiment as "Positive", "Negative", or "Neutral"
            - "intensity": Sentiment intensity as a number between 0 and 1
            - "emotions": Array of detected emotions (e.g., ["Joy", "Satisfaction"] or ["Anger", "Frustration"])
            - "confidence": Confidence score as a number between 0 and 1
            - "key_phrases": Array of key phrases from the review (minimum 3-4 phrases)
            
            Example JSON format:
            {{
                "sentiment": "Positive",
                "intensity": 0.95,
                "emotions": ["Joy", "Satisfaction", "Approval"],
                "confidence": 0.98,
                "key_phrases": ["I love Amazon!", "Great service", "fast delivery", "worth it"]
            }}
            
            Now analyze this review and respond with ONLY the JSON object:
            """
        else:
            prompt = f"""
            Classify the sentiment of this review as Positive, Negative, or Neutral.
            
            Review: "{text}"
            
            Respond with only one word: Positive, Negative, or Neutral
            """
        
        response = self.model.generate_content(prompt)
        return {
            'text': text,
            'gemini_response': response.text,
            'raw_response': response
        }
    
    def extract_aspects(self, text: str) -> Dict:
        """
        Extract aspects and their sentiments from review
        
        Args:
            text: Review text
        
        Returns:
            Dictionary with aspect-based sentiment analysis
        """
        prompt = f"""
        Analyze this customer review and identify specific aspects mentioned.
        For each aspect, determine the sentiment.
        
        Review: "{text}"
        
        Extract aspects such as:
        - Delivery/Shipping
        - Product Quality
        - Customer Service
        - Pricing
        - Website/App Experience
        - Account Issues
        - Other relevant aspects
        
        For each aspect found, provide:
        1. Aspect name
        2. Sentiment (Positive/Negative/Neutral)
        3. Relevant quote from review
        
        Format as JSON list with keys: aspect, sentiment, quote
        """
        
        response = self.model.generate_content(prompt)
        return {
            'text': text,
            'aspects': response.text,
            'raw_response': response
        }
    
    def summarize_review(self, text: str, max_length: int = 100) -> Dict:
        """
        Summarize a review
        
        Args:
            text: Review text to summarize
            max_length: Maximum length of summary
        
        Returns:
            Dictionary with summary
        """
        prompt = f"""
        Summarize the following customer review in {max_length} words or less.
        Focus on the main points, issues, or praises mentioned.
        
        Review: "{text}"
        
        Provide a concise summary highlighting:
        - Main complaint or praise
        - Key details
        - Overall takeaway
        """
        
        response = self.model.generate_content(prompt)
        return {
            'original_length': len(text),
            'summary': response.text,
            'summary_length': len(response.text)
        }
    
    def extract_key_insights(self, reviews: List[str], top_n: int = 5) -> Dict:
        """
        Extract key insights from multiple reviews
        
        Args:
            reviews: List of review texts
            top_n: Number of top insights to extract
        
        Returns:
            Dictionary with key insights
        """
        reviews_text = "\n\n".join([f"Review {i+1}: {review}" for i, review in enumerate(reviews)])
        
        prompt = f"""
        Analyze the following {len(reviews)} customer reviews and extract the top {top_n} key insights.
        
        Reviews:
        {reviews_text}
        
        Identify:
        1. Most common complaints or praises
        2. Recurring themes
        3. Patterns or trends
        4. Actionable recommendations
        
        Format as structured insights with examples.
        """
        
        response = self.model.generate_content(prompt)
        return {
            'num_reviews': len(reviews),
            'insights': response.text,
            'raw_response': response
        }
    
    def detect_sarcasm(self, text: str) -> Dict:
        """
        Detect sarcasm or irony in text
        
        Args:
            text: Review text
        
        Returns:
            Dictionary with sarcasm detection results
        """
        prompt = f"""
        Analyze if this review contains sarcasm, irony, or is being facetious.
        
        Review: "{text}"
        
        Determine:
        1. Contains sarcasm/irony: Yes/No
        2. Confidence level (0-1)
        3. Explanation of why
        4. Adjusted sentiment if sarcasm is present
        
        Format as JSON with keys: has_sarcasm, confidence, explanation, adjusted_sentiment
        """
        
        response = self.model.generate_content(prompt)
        return {
            'text': text,
            'sarcasm_analysis': response.text,
            'raw_response': response
        }
    
    def categorize_review(self, text: str) -> Dict:
        """
        Categorize review into topics
        
        Args:
            text: Review text
        
        Returns:
            Dictionary with category information
        """
        prompt = f"""
        Categorize this customer review into one or more of these topics:
        
        Categories:
        - Delivery/Shipping Issues
        - Product Quality/Defect
        - Customer Service
        - Billing/Payment Issues
        - Account Problems
        - Website/Technical Issues
        - Pricing Concerns
        - Positive Experience
        - Other
        
        Review: "{text}"
        
        Provide:
        1. Primary category
        2. Secondary categories (if any)
        3. Confidence score
        
        Format as JSON with keys: primary_category, secondary_categories, confidence
        """
        
        response = self.model.generate_content(prompt)
        return {
            'text': text,
            'categories': response.text,
            'raw_response': response
        }


# Convenience functions for easy use
def get_gemini_service(api_key: Optional[str] = None) -> GeminiService:
    """Get initialized GeminiService instance"""
    return GeminiService(api_key=api_key)


def analyze_sentiment_batch(texts: List[str], api_key: Optional[str] = None) -> List[Dict]:
    """Analyze sentiment for multiple texts"""
    service = get_gemini_service(api_key)
    results = []
    for text in texts:
        results.append(service.analyze_sentiment(text, detailed=True))
    return results


if __name__ == "__main__":
    # Test connection
    print("Testing Gemini API connection...")
    try:
        service = get_gemini_service()
        test_result = service.analyze_sentiment(
            "I love Amazon! Great service and fast delivery.",
            detailed=False
        )
        print("✅ Gemini API connected successfully!")
        print(f"Test result: {test_result['gemini_response']}")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Please check your API key in .env file")

