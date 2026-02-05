from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional

class LanguageEnum(str, Enum):
    Tamil = "Tamil"
    English = "English"
    Hindi = "Hindi"
    Malayalam = "Malayalam"
    Telugu = "Telugu"

class ClassificationEnum(str, Enum):
    AI_GENERATED = "AI_GENERATED"
    HUMAN = "HUMAN"

class VoiceDetectionRequest(BaseModel):
    language: Optional[LanguageEnum] = None
    audioFormat: str = Field(..., pattern="^mp3$")
    audioBase64: str

class VoiceDetectionResponse(BaseModel):
    status: str
    language: str
    classification: ClassificationEnum
    confidenceScore: float
    explanation: str
