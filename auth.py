from fastapi import HTTPException, Security, Request
from fastapi.security import APIKeyHeader
import os

API_KEY_NAME = "x-api-key"
# Start with the default test key
ALLOWED_API_KEYS = {"sk_test_123456789"}

# Add environment variable key if present (Secure for Render)
env_key = os.getenv("API_KEY")
if env_key:
    ALLOWED_API_KEYS.add(env_key)

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key: str = Security(api_key_header)):
    if not api_key:
        raise HTTPException(
            status_code=403,
            detail="Missing API Key headers"
        )
    if api_key not in ALLOWED_API_KEYS:
         raise HTTPException(
            status_code=403,
            detail="Invalid API Key"
        )
    return api_key
