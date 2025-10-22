from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from app.database.db import get_db
from app.core.security import decode_token
from app.models.recruiter import Recruiter
from app.core.composio_client import ComposioClient
from app.routes.recruiter import _require_recruiter


router = APIRouter()
bearer = HTTPBearer()


def _composio() -> ComposioClient:
    # Could load API key from env if needed
    return ComposioClient()


@router.post("/recruit/gmail/ingest")
def recruit_gmail_ingest(data: Dict[str, Any], credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    _require_recruiter(credentials, db)
    # Parse resumes from Gmail using Composio
    client = _composio()
    query = data.get("query", "has:attachment resume")
    resumes = client.gmail_list_resumes(query)
    # Return stub until real Composio integration
    return {"count": len(resumes), "items": resumes}


@router.post("/recruit/enrich")
def recruit_enrich(data: Dict[str, Any], credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    _require_recruiter(credentials, db)
    client = _composio()
    name = data.get("name")
    email = data.get("email")
    if not name and not email:
        raise HTTPException(status_code=400, detail="name or email required")
    enriched = client.linkedin_enrich(name or "", email)
    return enriched


@router.post("/recruit/schedule")
def recruit_schedule(data: Dict[str, Any], credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    _require_recruiter(credentials, db)
    client = _composio()
    title = data.get("title", "Interview")
    attendee = data.get("attendee")
    when = data.get("when")
    if not attendee:
        raise HTTPException(status_code=400, detail="attendee required")
    result = client.calendar_create_event(title, attendee, when)
    return result


@router.post("/recruit/pipeline/update")
def recruit_pipeline_update(data: Dict[str, Any], credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    _require_recruiter(credentials, db)
    client = _composio()
    sheet = data.get("sheet", "RecruitmentPipeline")
    row = data.get("row", [])
    ok = client.sheets_update_row(sheet, row)
    return {"updated": ok}


@router.post("/recruit/notion/page")
def recruit_notion_page(data: Dict[str, Any], credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    _require_recruiter(credentials, db)
    client = _composio()
    title = data.get("title", "Candidate")
    props = data.get("properties", {})
    page_id = client.notion_create_page(title, props)
    return {"page_id": page_id}


