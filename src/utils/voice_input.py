#!/usr/bin/env python3
"""
Voice Input Module

This module provides functionality for voice-to-text transcription using
OpenAI's Whisper model or other speech recognition services.
"""

import os
import sys
import logging
import tempfile
from typing import Optional, Tuple
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ensure project directory is in path
sys_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if sys_path not in sys.path:
    sys.path.append(sys_path)

# Import required libraries with fallbacks
try:
    import openai
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    logger.warning("OpenAI package not installed. Using fallback speech recognition.")
    OPENAI_AVAILABLE = False

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    logger.warning("SpeechRecognition package not installed. Voice input may be limited.")
    SPEECH_RECOGNITION_AVAILABLE = False

try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    logger.warning("Pydub package not installed. Audio conversion may be limited.")
    PYDUB_AVAILABLE = False


def transcribe_audio_with_whisper(audio_file_path: str, client=None) -> Tuple[str, float]:
    """
    Transcribe audio file using OpenAI's Whisper model.
    
    Args:
        audio_file_path: Path to the audio file
        client: Optional OpenAI client instance
        
    Returns:
        Tuple of (transcription text, confidence score)
    """
    if not OPENAI_AVAILABLE:
        logger.warning("OpenAI package not available. Cannot use Whisper.")
        return "", 0.0
    
    try:
        # Initialize client if not provided
        if client is None:
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Open the audio file
        with open(audio_file_path, "rb") as audio_file:
            # Transcribe using Whisper
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        
        # Extract transcription and confidence
        transcription = response.text
        # Whisper doesn't provide confidence scores directly
        confidence = 1.0  # Placeholder
        
        logger.info(f"Whisper transcription: {transcription}")
        return transcription, confidence
    
    except Exception as e:
        logger.error(f"Error transcribing with Whisper: {e}")
        return "", 0.0


def transcribe_audio_with_speech_recognition(audio_file_path: str) -> Tuple[str, float]:
    """
    Transcribe audio file using the SpeechRecognition library.
    
    Args:
        audio_file_path: Path to the audio file
        
    Returns:
        Tuple of (transcription text, confidence score)
    """
    if not SPEECH_RECOGNITION_AVAILABLE:
        logger.warning("SpeechRecognition package not available.")
        return "", 0.0
    
    try:
        # Initialize recognizer
        recognizer = sr.Recognizer()
        
        # Convert audio file to proper format if needed
        if PYDUB_AVAILABLE and not audio_file_path.lower().endswith(".wav"):
            # Convert to WAV using pydub
            audio = AudioSegment.from_file(audio_file_path)
            temp_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            audio.export(temp_wav.name, format="wav")
            audio_file_path = temp_wav.name
        
        # Load audio file
        with sr.AudioFile(audio_file_path) as source:
            audio_data = recognizer.record(source)
        
        # Transcribe using Google Speech Recognition
        transcription = recognizer.recognize_google(audio_data)
        confidence = 0.8  # Placeholder, as Google doesn't provide confidence scores
        
        logger.info(f"Google Speech Recognition transcription: {transcription}")
        return transcription, confidence
    
    except Exception as e:
        logger.error(f"Error transcribing with Speech Recognition: {e}")
        return "", 0.0
    
    finally:
        # Clean up temporary file if created
        if PYDUB_AVAILABLE and 'temp_wav' in locals():
            try:
                os.unlink(temp_wav.name)
            except:
                pass


def transcribe_audio(audio_file_path: str, use_whisper: bool = True) -> Tuple[str, float]:
    """
    Transcribe audio file using the best available method.
    
    Args:
        audio_file_path: Path to the audio file
        use_whisper: Whether to prefer Whisper over other methods
        
    Returns:
        Tuple of (transcription text, confidence score)
    """
    # Try Whisper first if preferred
    if use_whisper and OPENAI_AVAILABLE:
        transcription, confidence = transcribe_audio_with_whisper(audio_file_path)
        if transcription:
            return transcription, confidence
    
    # Fall back to Speech Recognition
    if SPEECH_RECOGNITION_AVAILABLE:
        transcription, confidence = transcribe_audio_with_speech_recognition(audio_file_path)
        if transcription:
            return transcription, confidence
    
    # If all methods fail
    logger.error("All transcription methods failed.")
    return "", 0.0


def save_uploaded_audio(uploaded_file, directory: str = "temp") -> Optional[str]:
    """
    Save an uploaded audio file to disk.
    
    Args:
        uploaded_file: Streamlit uploaded file object
        directory: Directory to save the file in
        
    Returns:
        Path to the saved file, or None if saving failed
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)
        
        # Generate a unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = os.path.splitext(uploaded_file.name)[1]
        filename = f"audio_{timestamp}{file_extension}"
        file_path = os.path.join(directory, filename)
        
        # Save the file
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        logger.info(f"Saved uploaded audio to {file_path}")
        return file_path
    
    except Exception as e:
        logger.error(f"Error saving uploaded audio: {e}")
        return None


if __name__ == "__main__":
    # Test functionality
    print("Voice Input Module Test")
    print("=" * 30)
    
    # Check available methods
    print(f"OpenAI/Whisper available: {OPENAI_AVAILABLE}")
    print(f"SpeechRecognition available: {SPEECH_RECOGNITION_AVAILABLE}")
    print(f"Pydub available: {PYDUB_AVAILABLE}")
    
    # Test with a sample file if provided
    if len(sys.argv) > 1:
        test_file = sys.argv[1]
        print(f"\nTesting with file: {test_file}")
        
        # Test Whisper
        if OPENAI_AVAILABLE:
            print("\nTesting Whisper transcription:")
            text, conf = transcribe_audio_with_whisper(test_file)
            print(f"Transcription: {text}")
            print(f"Confidence: {conf}")
        
        # Test Speech Recognition
        if SPEECH_RECOGNITION_AVAILABLE:
            print("\nTesting Speech Recognition:")
            text, conf = transcribe_audio_with_speech_recognition(test_file)
            print(f"Transcription: {text}")
            print(f"Confidence: {conf}")
    else:
        print("\nNo test file provided. Pass an audio file path as an argument to test transcription.")
