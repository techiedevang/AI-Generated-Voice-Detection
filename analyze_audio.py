from pydub import AudioSegment
import os

FILE = "Hindi_voice.mp3"

def analyze():
    print(f"--- Analyzing {FILE} ---")
    if not os.path.exists(FILE):
        print("File not found.")
        return

    try:
        audio = AudioSegment.from_file(FILE)
        print(f"Duration: {len(audio)/1000.0} seconds")
        print(f"Channels: {audio.channels}")
        print(f"Frame Rate: {audio.frame_rate} Hz")
        print(f"Volume (dBFS): {audio.dBFS:.2f}")
        print(f"Max Amplitude: {audio.max_dBFS:.2f}")
        
        if audio.dBFS < -40:
            print("WARNING: Audio is VERY quiet.")
        elif len(audio) < 1000:
            print("WARNING: Audio is very short (<1s).")
        else:
            print("Audio seems technically okay.")
            
    except Exception as e:
        print(f"Error analyzing audio: {e}")

if __name__ == "__main__":
    analyze()
