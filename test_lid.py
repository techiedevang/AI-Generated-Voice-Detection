import urllib.request
import json
import base64
import time

API_URL = "http://127.0.0.1:8000"
TINY_MP3_BASE64 = "SUQzBAAAAAAAI1ZhbGlkTVAz" # Dummy for structure check, real audio needed for real LID

def test_lid():
    print("Testing Auto-LID...")
    # Request WITHOUT language
    data_dict = {
        "audioFormat": "mp3",
        "audioBase64": TINY_MP3_BASE64
        # "language" OMITTED
    }
    
    req = urllib.request.Request(
        f"{API_URL}/api/voice-detection",
        data=json.dumps(data_dict).encode('utf-8'),
        headers={
            'Content-Type': 'application/json',
            'x-api-key': 'sk_test_123456789'
        }
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            resp_data = json.loads(response.read().decode())
            print(f"Response: {resp_data}")
            if resp_data['language'] == "English": # Default fallback for dummy audio
                print("LID Test PASSED (Fallback/Default works)")
            else:
                print(f"LID Result: {resp_data['language']}")
    except Exception as e:
        print(f"LID Test FAILED: {e}")

if __name__ == "__main__":
    # Give server a moment to reload
    time.sleep(2)
    test_lid()
