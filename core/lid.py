from faster_whisper import WhisperModel
import os

# 'tiny' is ~75MB, faster and safer for free cloud tiers
# Using faster-whisper (CTranslate2) drastically reduces memory usage (INT8)
MODEL_SIZE = "tiny"
_model = None

class LanguageDetector:
    def __init__(self):
        global _model
        if _model is None:
            print(f"LID: Loading Faster-Whisper '{MODEL_SIZE}' model... (One-time setup)")
            try:
                # cpu_threads=1 to be nice to free tier
                # compute_type="int8" is the key for low RAM usage (<500MB)
                _model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8", cpu_threads=2)
                print("LID: Faster-Whisper model loaded.")
            except Exception as e:
                print(f"LID Error loading model: {e}")
                raise e

    def detect(self, audio_file_path: str):
        print(f"LID:Analyzing {audio_file_path} with Faster-Whisper...")
        
        try:
            # transcription returns segments generator and info object
            # beam_size=1 is faster, lower memory
            segments, info = _model.transcribe(audio_file_path, beam_size=1)
            
            code = info.language
            conf = info.language_probability
            
            # Map simplified codes to full names
            iso_map = {
                'ta': 'Tamil', 'en': 'English', 'hi': 'Hindi', 
                'ml': 'Malayalam', 'te': 'Telugu'
            }
            
            mapped = iso_map.get(code)
            
            print(f"LID: Detected '{code}' ({mapped}) with conf {conf:.2f}")

            if mapped and conf > 0.4:
                return mapped
            else:
                print(f"LID: Low confidence or unsupported language: {code}")
                return None
            
        except Exception as e:
            print(f"LID Critical Error: {e}")
            return None

_detector = None
def get_detector():
    global _detector
    if _detector is None:
        _detector = LanguageDetector()
    return _detector
