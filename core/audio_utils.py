import base64
import librosa
import numpy as np
from pydub import AudioSegment
import soundfile as sf
import tempfile
import os

def decode_base64_to_audio(audio_base64):
    """
    Decode base64 string to audio data.
    Returns: (y, sr) - audio samples and sample rate
    """
    try:
        # Check if it's already a path (legacy support)
        if hasattr(audio_base64, "read"):
             # It's a file-like object
             pass
        
        audio_bytes = base64.b64decode(audio_base64)
        
        # Use a temporary file for robust librosa loading (ffmpeg wrapper)
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name
        
        # Load with librosa
        try:
            y, sr = librosa.load(tmp_path, sr=22050)
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
                
        return y, sr
    except Exception as e:
        raise ValueError(f"Failed to decode audio: {str(e)}")

def load_audio_features(audio_base64):
    """
    Extract audio features needed for classification.
    """
    y, sr = decode_base64_to_audio(audio_base64)
    
    # Feature 1: Zero Crossing Rate
    zcr = np.mean(librosa.feature.zero_crossing_rate(y=y))
    
    # Feature 2: Spectral Flatness
    flatness = np.mean(librosa.feature.spectral_flatness(y=y))
    
    # Feature 3: Pitch Standard Deviation
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
    # Filter out noise (low magnitude)
    pitch_values = pitches[magnitudes > np.median(magnitudes)]
    pitch_std = np.std(pitch_values) if len(pitch_values) > 0 else 0
    
    # Feature 4: Silence Ratio
    non_silent = librosa.effects.split(y, top_db=20)
    non_silent_duration = sum([(e-s) for s,e in non_silent]) / sr
    total_duration = librosa.get_duration(y=y, sr=sr)
    silence_ratio = 1.0 - (non_silent_duration / total_duration) if total_duration > 0 else 0.0
    
    # Feature 5: Duration
    duration = total_duration
    
    return {
        "zero_crossing_rate": zcr,
        "spectral_flatness": flatness,
        "pitch_std": pitch_std,
        "silence_ratio": silence_ratio,
        "duration": duration
    }
