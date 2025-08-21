import time
import functools
import logging
import os
from typing import Callable, Any

def timing_decorator(func: Callable) -> Callable:
    """Decorator to measure function execution time"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        execution_time = end_time - start_time
        logging.info(f"{func.__name__} executed in {execution_time:.2f} seconds")
        
        return result
    return wrapper

class ModelManager:
    """Singleton pattern for managing model instances"""
    _instances = {}
    models = {}  # Add models attribute for storing model instances
    
    @classmethod
    def get_model(cls, model_type: str, **kwargs):
        """Get or create model instance"""
        if model_type not in cls._instances:
            if model_type == "asr":
                try:
                    from models.asr import WhisperASR
                except ImportError:
                    import sys
                    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
                    from models.asr import WhisperASR
                cls._instances[model_type] = WhisperASR(**kwargs)
            elif model_type == "nlp":
                try:
                    from models.nlp import NLPProcessor
                except ImportError:
                    import sys
                    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
                    from models.nlp import NLPProcessor
                cls._instances[model_type] = NLPProcessor(**kwargs)
            elif model_type == "search":
                try:
                    from models.search import MeetingSearchEngine
                except ImportError:
                    import sys
                    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
                    from models.search import MeetingSearchEngine
                cls._instances[model_type] = MeetingSearchEngine(**kwargs)
            else:
                raise ValueError(f"Unknown model type: {model_type}")
        
        return cls._instances[model_type]
    
    @classmethod
    def clear_cache(cls):
        """Clear all cached model instances"""
        cls._instances.clear()
