"""
Language Detection Utilities for Polyglot Meeting Assistant

This module provides utilities for detecting languages in text and audio files.
"""

import logging
from typing import Dict, Any, Optional

try:
    from langdetect import detect, detect_langs
    from langdetect.lang_detect_exception import LangDetectException
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False
    logging.warning("langdetect not available. Install with: pip install langdetect")

# Language code mapping for better display
LANGUAGE_NAMES = {
    'en': 'English',
    'es': 'Spanish', 
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'zh': 'Chinese',
    'ja': 'Japanese',
    'ko': 'Korean',
    'ar': 'Arabic',
    'hi': 'Hindi',
    'nl': 'Dutch',
    'pl': 'Polish',
    'sv': 'Swedish',
    'da': 'Danish',
    'no': 'Norwegian',
    'fi': 'Finnish',
    'tr': 'Turkish',
    'cs': 'Czech',
    'hu': 'Hungarian',
    'ro': 'Romanian',
    'bg': 'Bulgarian',
    'hr': 'Croatian',
    'sk': 'Slovak',
    'sl': 'Slovenian',
    'et': 'Estonian',
    'lv': 'Latvian',
    'lt': 'Lithuanian',
    'uk': 'Ukrainian',
    'be': 'Belarusian',
    'mk': 'Macedonian',
    'sq': 'Albanian',
    'mt': 'Maltese',
    'ga': 'Irish',
    'cy': 'Welsh',
    'eu': 'Basque',
    'ca': 'Catalan',
    'gl': 'Galician',
    'eo': 'Esperanto',
    'la': 'Latin',
    'sw': 'Swahili',
    'af': 'Afrikaans',
    'ta': 'Tamil',
    'te': 'Telugu',
    'bn': 'Bengali',
    'ur': 'Urdu',
    'fa': 'Persian',
    'he': 'Hebrew',
    'th': 'Thai',
    'vi': 'Vietnamese',
    'id': 'Indonesian',
    'ms': 'Malay',
    'tl': 'Filipino'
}

def detect_text_language(text: str, min_confidence: float = 0.7) -> Dict[str, Any]:
    """
    Detect language from text content
    
    Args:
        text: Text content to analyze
        min_confidence: Minimum confidence threshold
        
    Returns:
        Dictionary with language detection results
    """
    if not LANGDETECT_AVAILABLE:
        return {
            'language': 'unknown',
            'language_name': 'Unknown',
            'confidence': 0.0,
            'method': 'text_detection',
            'error': 'langdetect not available'
        }
    
    if not text or len(text.strip()) < 20:
        return {
            'language': 'unknown',
            'language_name': 'Unknown',
            'confidence': 0.0,
            'method': 'text_detection'
        }
    
    try:
        # Get primary language
        primary_lang = detect(text)
        
        # Get all possible languages with probabilities
        all_langs = detect_langs(text)
        
        # Find confidence for primary language
        confidence = 0.0
        for lang_prob in all_langs:
            if lang_prob.lang == primary_lang:
                confidence = lang_prob.prob
                break
        
        # Check if confidence meets threshold
        if confidence < min_confidence:
            return {
                'language': 'uncertain',
                'language_name': 'Uncertain',
                'confidence': confidence,
                'method': 'text_detection'
            }
        
        return {
            'language': primary_lang,
            'language_name': LANGUAGE_NAMES.get(primary_lang, primary_lang.upper()),
            'confidence': confidence,
            'method': 'text_detection'
        }
        
    except LangDetectException as e:
        logging.warning(f"Language detection failed: {e}")
        return {
            'language': 'unknown',
            'language_name': 'Unknown',
            'confidence': 0.0,
            'method': 'text_detection',
            'error': str(e)
        }

def get_language_name(language_code: str) -> str:
    """
    Get language name from language code
    
    Args:
        language_code: ISO language code
        
    Returns:
        Human-readable language name
    """
    return LANGUAGE_NAMES.get(language_code, language_code.upper() if language_code else 'Unknown')
