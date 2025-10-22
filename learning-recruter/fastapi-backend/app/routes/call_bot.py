from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from app.core.call_bot import call_bot
from app.core.security import decode_token
from app.database.db import get_db
import logging

logger = logging.getLogger(__name__)
bearer_scheme = HTTPBearer()
router = APIRouter()

class CallRequest(BaseModel):
    phone_number: str

class CallStatusResponse(BaseModel):
    call_sid: str
    status: str
    duration: int = None

@router.post("/initiate")
async def initiate_call(
    request: CallRequest,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):
    """Initiate a call with accumulated learning context"""
    try:
        # Verify token and get user ID
        token = credentials.credentials
        user_id = decode_token(token)
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Initiate call with shared context
        result = call_bot.make_call(
            db=db,
            user_id=int(user_id),
            to_number=request.phone_number
        )
        
        if result["success"]:
            return {
                "message": "Call initiated successfully",
                "call_sid": result["call_sid"],
                "status": result["status"],
                "context_preview": result["context_preview"],
                "logs": result.get("logs", [])
            }
        else:
            raise HTTPException(status_code=500, detail=result["error"])
            
    except Exception as e:
        logger.error(f"Call initiation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to initiate call")

@router.get("/status/{call_sid}")
async def get_call_status(
    call_sid: str,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):
    """Get call status"""
    try:
        # Verify token
        token = credentials.credentials
        user_id = decode_token(token)
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        status = call_bot.get_call_status(call_sid)
        
        if "error" in status:
            raise HTTPException(status_code=500, detail=status["error"])
        
        return status
        
    except Exception as e:
        logger.error(f"Call status error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get call status")