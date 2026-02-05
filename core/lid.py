import whisper
import os
import torch

# Load model once at module level (Global Cache)
# 'base' model is ~140MB and good balance of speed/accuracy
# 'tiny' is ~75MB but less accurate
MODEL_SIZE = "base"
_model = None

class LanguageDetector:
    def __init__(self):
        global _model
        if _model is None:
            print(f"LID: Loading Whisper '{MODEL_SIZE}' model... (One-time setup)")
            try:
                device = "cuda" if torch.cuda.is_available() else "cpu"
                print(f"LID: Using device -> {device}")
                _model = whisper.load_model(MODEL_SIZE, device=device)
                print("LID: Whisper model loaded.")
            except Exception as e:
                print(f"LID Error loading model: {e}")
                raise e

    def detect(self, audio_file_path: str):
        print(f"LID:Analyzing {audio_file_path} with Whisper...")
        
        try:
            # Whisper supports MP3/WAV file paths directly!
            # It loads 30s chunks internally, so no manual chunking needed usually.
            
            # Load audio (entire file)
            audio_full = whisper.load_audio(audio_file_path)
            total_samples = len(audio_full)
            SAMPLE_RATE = 16000
            CHUNK_LENGTH = 30 * SAMPLE_RATE  # 30 seconds
            
            # Helper to detect on a specific audio slice
            def detect_chunk(audio_slice):
                audio_slice = whisper.pad_or_trim(audio_slice)
                mel = whisper.log_mel_spectrogram(audio_slice).to(_model.device)
                _, probs = _model.detect_language(mel)
                best_code = max(probs, key=probs.get)
                return best_code, probs[best_code]

            detected_langs = set()
            scan_points = [0] # Always check start
            
            # If long file, check middle and end
            if total_samples > CHUNK_LENGTH * 2:
                scan_points.append(total_samples // 2)
                scan_points.append(max(0, total_samples - CHUNK_LENGTH))
            
            iso_map = {
                'ta': 'Tamil', 'en': 'English', 'hi': 'Hindi', 
                'ml': 'Malayalam', 'te': 'Telugu'
            }

            print(f"LID: Scanning {len(scan_points)} segments...")

            for start in scan_points:
                segment = audio_full[start : start + CHUNK_LENGTH]
                code, conf = detect_chunk(segment)
                mapped = iso_map.get(code)
                
                if mapped and conf > 0.4: # Only include if confident
                    print(f"LID: Found '{mapped}' ({code}) with conf {conf:.2f}")
                    detected_langs.add(mapped)
            
            if not detected_langs:
                print("LID: No supported languages found.")
                return None
            
            # Sort for consistent output
            final_result = ", ".join(sorted(detected_langs))
            print(f"LID: Final Result -> {final_result}")
            return final_result

        except Exception as e:
            print(f"LID Critical Error: {e}")
            return None

_detector = None
def get_detector():
    global _detector
    if _detector is None:
        _detector = LanguageDetector()
    return _detector
