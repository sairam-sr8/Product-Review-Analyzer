"""
Utility functions for NLP project
"""

import pandas as pd
import numpy as np
from typing import List, Dict
import json
import re


def parse_gemini_json_response(response_text: str) -> Dict:
    """
    Parse Gemini JSON response (may contain markdown code blocks)
    
    Args:
        response_text: Raw response from Gemini
    
    Returns:
        Parsed dictionary
    """
    # Remove markdown code blocks if present
    response_text = re.sub(r'```json\s*', '', response_text)
    response_text = re.sub(r'```\s*', '', response_text)
    response_text = response_text.strip()
    
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        # If JSON parsing fails, return as text
        return {'text': response_text, 'parsing_error': True}


def combine_sentiment_results(bilstm_prediction: str, bilstm_confidence: float,
                             gemini_result: Dict) -> Dict:
    """
    Combine BiLSTM and Gemini sentiment predictions
    
    Args:
        bilstm_prediction: Prediction from BiLSTM model
        bilstm_confidence: Confidence score from BiLSTM
        gemini_result: Result from Gemini API
    
    Returns:
        Combined result dictionary
    """
    return {
        'bilstm_prediction': bilstm_prediction,
        'bilstm_confidence': bilstm_confidence,
        'gemini_analysis': gemini_result,
        'combined_confidence': (bilstm_confidence + 0.7) / 2  # Weighted average
    }


def extract_insights_summary(gemini_insights: str) -> List[str]:
    """
    Extract bullet points from Gemini insights text
    
    Args:
        gemini_insights: Text response from Gemini
    
    Returns:
        List of insight strings
    """
    lines = gemini_insights.split('\n')
    insights = []
    
    for line in lines:
        line = line.strip()
        # Remove common bullet markers
        line = re.sub(r'^[-\*•]\s+', '', line)
        line = re.sub(r'^\d+\.\s+', '', line)
        
        if len(line) > 20:  # Filter out very short lines
            insights.append(line)
    
    return insights[:10]  # Return top 10


def validate_review_quality(text: str, min_length: int = 20) -> Dict:
    """
    Validate review quality
    
    Args:
        text: Review text
        min_length: Minimum character length
    
    Returns:
        Quality metrics dictionary
    """
    word_count = len(text.split())
    char_count = len(text)
    has_punctuation = bool(re.search(r'[.!?]', text))
    
    return {
        'is_valid': char_count >= min_length and word_count >= 5,
        'word_count': word_count,
        'char_count': char_count,
        'has_punctuation': has_punctuation,
        'quality_score': min(100, (word_count / 50) * 100)
    }


def format_sentiment_output(result: Dict) -> str:
    """
    Format sentiment analysis result for display
    
    Args:
        result: Result dictionary from Gemini
    
    Returns:
        Formatted string
    """
    output = f"""
## 🎯 Sentiment Analysis Result

**Sentiment:** {result.get('sentiment', 'Unknown')}
**Intensity:** {result.get('intensity', 'N/A')}
**Confidence:** {result.get('confidence', 'N/A')}

**Detected Emotions:** {', '.join(result.get('emotions', []))}

**Key Phrases:**
{result.get('key_phrases', 'None identified')}
"""
    return output

