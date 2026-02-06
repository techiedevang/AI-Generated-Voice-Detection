from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import VoiceDetectionRequest, VoiceDetectionResponse, ClassificationEnum
from auth import get_api_key
from core.detector import classify_voice 
# from core.audio_utils import decode_base64_to_file

app = FastAPI(title="AI Voice Detection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# 11. Error Response Handler
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "message": str(exc.detail)},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"status": "error", "message": "Invalid API key or malformed request"},
    )

from core.lid import get_detector
import os
import base64

# Preload model on startup to prevent 502 Timeouts on first request
@app.on_event("startup")
async def startup_event():
    print("Startup: Pre-loading Whisper Model...")
    get_detector() # Triggers download/load
    print("Startup: Model loaded. Ready for requests.")

@app.post("/api/voice-detection", response_model=VoiceDetectionResponse)
def detect_voice(request: VoiceDetectionRequest, api_key: str = Depends(get_api_key)):
    try:
        # 1. Handle Language Detection (if missing)
        final_language = request.language
        
        # Save temp file for processing (needed for LID and clean librosa loading)
        temp_filename = "temp_request_audio.mp3"
        with open(temp_filename, "wb") as f:
            f.write(base64.b64decode(request.audioBase64))
            
        if not final_language:
            print("Language not provided. Auto-detecting...")
            detector = get_detector()
            final_language = detector.detect(temp_filename)
            print(f"Auto-detected Language: {final_language}")
            
            if final_language is None:
                raise HTTPException(status_code=400, detail="Audio is not detectable")

        # 2. Classify Voice
        result = classify_voice(
            base64_audio=request.audioBase64,
            language=final_language
        )
        
        # Cleanup
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
        
        return VoiceDetectionResponse(
            status="success",
            language=final_language,
            classification=result["classification"],
            confidenceScore=result["confidenceScore"],
            explanation=result["explanation"]
        )

    except ValueError as ve:
        # Client side error (bad base64 etc)
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        # Internal processing error
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.get("/")
def health_check():
    return {"status": "online", "message": "Voice Detection API is running"}
