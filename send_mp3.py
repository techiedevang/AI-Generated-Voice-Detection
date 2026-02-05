import base64
import json
import urllib.request
import urllib.error
import os

API_URL = "https://ai-generated-voice-detection-qb4f.onrender.com/api/voice-detection"
API_KEY = "sk_test_123456789"
FILE_PATH = "Tamil_voice.mp3"

def send_request():
    if not os.path.exists(FILE_PATH):
        print(f"Error: File '{FILE_PATH}' not found in current directory.")
        return

    print(f"Reading {FILE_PATH}...")
    try:
        with open(FILE_PATH, "rb") as audio_file:
            encoded_string = base64.b64encode(audio_file.read()).decode('utf-8')
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    # Prepare Payload (Auto-detect language)
    payload = {
        # "language": "English", # Commented out to test auto-detect
        "audioFormat": "mp3",
        "audioBase64": encoded_string
    }
    
    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }

    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode('utf-8'),
        headers=headers
    )

    print("Sending request to API...")
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            print("\n" + "="*30)
            print("CHECK RESULT")
            print("="*30)
            print(json.dumps(result, indent=2))
            print("="*30)
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code}")
        print(e.read().decode())
    except urllib.error.URLError as e:
        print(f"Connection Error: {e.reason}")
        print("Is the server running on port 8000?")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    send_request()