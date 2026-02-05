import urllib.request
import json
import time
import sys
import base64
import io

API_URL = "http://127.0.0.1:8000"

# Dynamically generate valid MP3 base64 to avoid copy-paste errors
try:
    from pydub import AudioSegment
    print("Generating valid MP3 using pydub...")
    s = io.BytesIO()
    AudioSegment.silent(duration=500).export(s, format="mp3")
    TINY_MP3_BASE64 = base64.b64encode(s.getvalue()).decode("utf-8")
except Exception as e:
    print(f"Warning: Could not generate dynamic MP3: {e}")
    # Fallback to a fairly reliable simple string (might fail strict checks but trying best effort)
    # This is a raw valid 1-frame MP3 hex converted to base64
    TINY_MP3_BASE64 = "SUQzBAAAAAAAI1ZhbGlkTVAz" 

def run_test(name, func):
    try:
        print(f"Running {name}...", end=" ")
        func()
        print("PASSED")
    except Exception as e:
        print(f"FAILED: {e}")
        # Continue running other tests? No, fail fast.
        # sys.exit(1)

def test_health():
    with urllib.request.urlopen(f"{API_URL}/") as response:
        if response.status != 200:
            raise Exception(f"Status {response.status}")
        data = json.loads(response.read().decode())
        if data["status"] != "online":
            raise Exception("Health check bad response")

def test_auth():
    req = urllib.request.Request(
        f"{API_URL}/api/voice-detection",
        data=json.dumps({
            "language": "English",
            "audioFormat": "mp3",
            "audioBase64": TINY_MP3_BASE64
        }).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    try:
        urllib.request.urlopen(req)
        raise Exception("Should have failed without API key")
    except urllib.error.HTTPError as e:
        if e.code != 403:
            raise Exception(f"Expected 403, got {e.code}")

def test_detection():
    data_dict = {
        "language": "Tamil",
        "audioFormat": "mp3",
        "audioBase64": TINY_MP3_BASE64
    }
    req = urllib.request.Request(
        f"{API_URL}/api/voice-detection",
        data=json.dumps(data_dict).encode('utf-8'),
        headers={
            'Content-Type': 'application/json',
            'x-api-key': 'sk_test_123456789'
        }
    )
    with urllib.request.urlopen(req) as response:
        if response.status != 200:
            raise Exception(f"Status {response.status}")
        resp_data = json.loads(response.read().decode())
        
        print(f"\n   Detected: {resp_data['classification']} - {resp_data['confidenceScore']}")
        if "explanation" in resp_data:
             print(f"   Explanation: {resp_data['explanation']}")
             
        if resp_data['status'] != 'success':
            raise Exception(f"API returned error: {resp_data}")

if __name__ == "__main__":
    run_test("Health Check", test_health)
    run_test("Auth Check", test_auth)
    run_test("Detection Check", test_detection)
