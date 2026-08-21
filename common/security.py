from fastapi import Header, HTTPException, status
from common.config import settings

def verify_api_key(x_api_key: str = Header(None)):
    """
    Optional API Key check for internal endpoints.
    Allows request if API_GATEWAY_KEY is set and matches, or if no key enforcement is configured.
    """
    if settings.API_GATEWAY_KEY and settings.API_GATEWAY_KEY != "jrai_gateway_default_key":
        if x_api_key != settings.API_GATEWAY_KEY:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing API Key"
            )
    return True
