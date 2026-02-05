from core.lid import get_detector
import os
import shutil

FILE_TO_TEST = "Hindi_voice.mp3"

def debug_lid():
    print(f"--- Debugging LID for {FILE_TO_TEST} ---")
    
    if not os.path.exists(FILE_TO_TEST):
        print(f"ERROR: File {FILE_TO_TEST} not found!")
        return

    # 1. Check FFmpeg availability (crucial for pydub)
    if shutil.which("ffmpeg"):
        print("FFmpeg detected: OK")
    else:
        print("ERROR: FFmpeg NOT found in PATH. Pydub will fail to convert MP3.")
        return

    # 2. Run Detector
    try:
        detector = get_detector()
        print("Detector initialized.")
        
        result = detector.detect(FILE_TO_TEST)
        print(f"\nFINAL RESULT: {result}")
        
    except Exception as e:
        print(f"CRITICAL EXCEPTION: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_lid()
