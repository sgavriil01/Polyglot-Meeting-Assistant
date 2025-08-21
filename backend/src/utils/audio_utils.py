"""
Audio Processing Utilities for Polyglot Meeting Assistant

This module provides utilities for processing audio and video files,
converting them to text using the ASR processor.
"""

import os
import asyncio
import logging
from typing import Optional
from pathlib import Path

try:
    from pydub import AudioSegment
except ImportError:
    AudioSegment = None
    logging.warning("pydub not available - audio processing limited")

async def process_audio_file(file_path: str, asr_processor) -> str:
    """
    Process an audio or video file and convert it to text
    
    Args:
        file_path: Path to the audio/video file
        asr_processor: ASR processor instance
        
    Returns:
        Transcribed text from the audio/video file
    """
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Get file extension
        file_ext = Path(file_path).suffix.lower()
        
        # Handle different file types
        if file_ext in ['.mp3', '.wav', '.m4a', '.flac', '.ogg']:
            # Direct audio file - can be processed by Whisper
            transcript = await transcribe_audio(file_path, asr_processor)
            
        elif file_ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm']:
            # Video file - extract audio first
            audio_path = await extract_audio_from_video(file_path)
            try:
                transcript = await transcribe_audio(audio_path, asr_processor)
            finally:
                # Clean up extracted audio file
                if os.path.exists(audio_path):
                    os.remove(audio_path)
                    
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
        
        return transcript
        
    except Exception as e:
        logging.error(f"Error processing audio file {file_path}: {e}")
        raise

async def transcribe_audio(audio_path: str, asr_processor) -> str:
    """
    Transcribe audio file using ASR processor
    
    Args:
        audio_path: Path to audio file
        asr_processor: ASR processor instance
        
    Returns:
        Transcribed text
    """
    try:
        if asr_processor is None:
            raise RuntimeError("ASR processor not available")
        
        # Run transcription in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        transcript = await loop.run_in_executor(
            None, 
            asr_processor.transcribe, 
            audio_path
        )
        
        return transcript
        
    except Exception as e:
        logging.error(f"Error transcribing audio {audio_path}: {e}")
        raise

async def extract_audio_from_video(video_path: str) -> str:
    """
    Extract audio from video file
    
    Args:
        video_path: Path to video file
        
    Returns:
        Path to extracted audio file
    """
    try:
        # Use ffmpeg to extract audio
        import subprocess
        
        output_path = video_path.rsplit('.', 1)[0] + '_audio.wav'
        
        # Run ffmpeg command
        cmd = [
            'ffmpeg', '-i', video_path,
            '-vn',  # No video
            '-acodec', 'pcm_s16le',  # PCM audio codec
            '-ar', '16000',  # Sample rate
            '-ac', '1',  # Mono
            '-y',  # Overwrite output
            output_path
        ]
        
        # Run command
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise RuntimeError(f"FFmpeg failed: {stderr.decode()}")
        
        return output_path
        
    except ImportError:
        raise RuntimeError("FFmpeg not available - cannot extract audio from video")
    except Exception as e:
        logging.error(f"Error extracting audio from video {video_path}: {e}")
        raise

def convert_audio_format(input_path: str, output_path: str, target_format: str = 'wav') -> str:
    """
    Convert audio file to different format using pydub
    
    Args:
        input_path: Input audio file path
        output_path: Output audio file path
        target_format: Target format (wav, mp3, etc.)
        
    Returns:
        Path to converted audio file
    """
    try:
        if AudioSegment is None:
            raise RuntimeError("pydub not available")
        
        # Load audio file
        audio = AudioSegment.from_file(input_path)
        
        # Export to target format
        audio.export(output_path, format=target_format)
        
        return output_path
        
    except Exception as e:
        logging.error(f"Error converting audio format: {e}")
        raise

def get_audio_duration(file_path: str) -> float:
    """
    Get duration of audio file in seconds
    
    Args:
        file_path: Path to audio file
        
    Returns:
        Duration in seconds
    """
    try:
        if AudioSegment is None:
            raise RuntimeError("pydub not available")
        
        audio = AudioSegment.from_file(file_path)
        return len(audio) / 1000.0  # Convert milliseconds to seconds
        
    except Exception as e:
        logging.error(f"Error getting audio duration: {e}")
        return 0.0

def is_audio_file(file_path: str) -> bool:
    """
    Check if file is an audio file
    
    Args:
        file_path: Path to file
        
    Returns:
        True if audio file, False otherwise
    """
    audio_extensions = {'.mp3', '.wav', '.m4a', '.flac', '.ogg', '.aac'}
    return Path(file_path).suffix.lower() in audio_extensions

def is_video_file(file_path: str) -> bool:
    """
    Check if file is a video file
    
    Args:
        file_path: Path to file
        
    Returns:
        True if video file, False otherwise
    """
    video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv'}
    return Path(file_path).suffix.lower() in video_extensions

def get_supported_formats() -> dict:
    """
    Get list of supported audio and video formats
    
    Returns:
        Dictionary with supported formats
    """
    return {
        'audio': ['.mp3', '.wav', '.m4a', '.flac', '.ogg', '.aac'],
        'video': ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv']
    }
