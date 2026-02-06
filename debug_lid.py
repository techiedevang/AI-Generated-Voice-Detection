from faster_whisper import WhisperModel
import os

# Use the same model size as the app
MODEL_SIZE = "base"
FILE_PATH = "Malyalam_voice.mp3"

def debug_lid():
    if not os.path.exists(FILE_PATH):
        print(f"Error: File '{FILE_PATH}' not found.")
        return

    print(f"Loading Faster-Whisper '{MODEL_SIZE}' model...")
    # cpu_threads=4 for faster local debugging
    model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8", cpu_threads=4)
    
    print(f"Analyzing {FILE_PATH}...")
    
    # Transcribe with language probability access
    segments, info = model.transcribe(FILE_PATH, beam_size=5)
    
    print("\n" + "="*40)
    print("TOP DETECTION RESULT")
    print("="*40)
    print(f"Detected Language Code: {info.language}")
    print(f"Confidence Score:       {info.language_probability:.4f}")
    
    print("\n" + "="*40)
    print("DIAGNOSTICS")
    print("="*40)
    
    # Check if it matches our expected Dravidian languages
    iso_map = {
        'ta': 'Tamil', 'en': 'English', 'hi': 'Hindi', 
        'ml': 'Malayalam', 'te': 'Telugu'
    }
    
    readable = iso_map.get(info.language, "Unknown")
    print(f"Mapped Name: {readable}")
    
    if info.language_probability < 0.4:
        print("⚠️ WARNING: Confidence is below 0.4 threshold!")
        print("This is why the API might reject it.")
    else:
        print("✅ Confidence is acceptable (> 0.4).")

if __name__ == "__main__":
    debug_lid()
