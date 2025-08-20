import whisper
import torch
from typing import Dict, Any, List
import logging
import os
import time
import functools

def timing_decorator(func):
    """Simple timing decorator"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logging.info(f"{func.__name__} executed in {end_time - start_time:.2f} seconds")
        return result
    return wrapper

class WhisperASR:
    """Whisper-based Automatic Speech Recognition"""
    
    def __init__(self, model_size: str = "base"):
        """
        Initialize Whisper ASR model
        
        Args:
            model_size: Model size ('tiny', 'base', 'small', 'medium', 'large')
        """
        self.model_size = model_size
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.load_model()
    
    def load_model(self):
        """Load Whisper model"""
        try:
            logging.info(f"Loading Whisper {self.model_size} model on {self.device}")
            self.model = whisper.load_model(self.model_size, device=self.device)
            logging.info(f"Successfully loaded Whisper {self.model_size} model")
        except Exception as e:
            logging.error(f"Failed to load Whisper model: {e}")
            raise
    
    @timing_decorator
    def transcribe(self, audio_path: str, language: str = None) -> Dict[str, Any]:
        """
        Transcribe audio file
        
        Args:
            audio_path: Path to audio file
            language: Force specific language (optional)
            
        Returns:
            Dict with transcription results
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        try:
            # Transcribe with options
            options = {
                "fp16": False,  # Use FP32 for better compatibility
                "language": language,
                "task": "transcribe"
            }
            
            result = self.model.transcribe(audio_path, **{k: v for k, v in options.items() if v is not None})
            
            return {
                "text": result["text"].strip(),
                "segments": result["segments"],
                "language": result["language"],
                "duration": max([seg["end"] for seg in result["segments"]]) if result["segments"] else 0
            }
            
        except Exception as e:
            logging.error(f"Transcription failed for {audio_path}: {e}")
            raise
    
    def transcribe_batch(self, audio_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Transcribe multiple audio files efficiently
        
        Args:
            audio_paths: List of paths to audio files
            
        Returns:
            List of transcription results
        """
        results = []
        for audio_path in audio_paths:
            try:
                result = self.transcribe(audio_path)
                results.append({
                    "file": audio_path,
                    "success": True,
                    **result
                })
            except Exception as e:
                results.append({
                    "file": audio_path,
                    "success": False,
                    "error": str(e)
                })
                logging.error(f"Failed to transcribe {audio_path}: {e}")
        
        return results
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages"""
        return list(whisper.tokenizer.LANGUAGES.values())

# Example usage and testing
if __name__ == "__main__":
    import tempfile
    import numpy as np
    from pydub import AudioSegment
    from pydub.generators import Sine
    
    # Create a simple test audio file
    logging.basicConfig(level=logging.INFO)
    
    # Generate a test tone
    tone = Sine(440).to_audio_segment(duration=3000)  # 3 seconds of 440Hz tone
    
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
        tone.export(tmp_file.name, format="wav")
        
        # Test ASR
        asr = WhisperASR(model_size="tiny")  # Use tiny for testing
        print(f"Supported languages: {len(asr.get_supported_languages())} languages")
        
        try:
            result = asr.transcribe(tmp_file.name)
            print(f"Transcription result: {result}")
        except Exception as e:
            print(f"Test failed (expected for tone): {e}")
        finally:
            os.unlink(tmp_file.name)
