from pydub import AudioSegment
import os

# Create a 2-second silent MP3
print("Generating sample my_voice.mp3...")
silence = AudioSegment.silent(duration=2000)
silence.export("my_voice.mp3", format="mp3")
print("Done.")
