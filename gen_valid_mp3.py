from pydub import AudioSegment
import io
import base64

# Create 1 second of silence
silence = AudioSegment.silent(duration=1000)
wav_io = io.BytesIO()
silence.export(wav_io, format="mp3")
print(base64.b64encode(wav_io.getvalue()).decode("utf-8"))
