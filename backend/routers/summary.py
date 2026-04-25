from fastapi import APIRouter, HTTPException, Depends, Header
from models.schemas import SummaryRequest, SummaryResponse
from services.vector_service import get_file_metadata
from services.llm_service import summarize_text
from routers.auth import get_current_user
from typing import Optional

router = APIRouter()

@router.post("/", response_model=SummaryResponse)
async def summarize(
    req: SummaryRequest,
    user: str = Depends(get_current_user),
    x_openai_key: Optional[str] = Header(None)
):
    if not x_openai_key:
        raise HTTPException(400, "OpenAI API key missing.")
    meta = await get_file_metadata(req.file_id)
    if not meta:
        raise HTTPException(404, "File not found")
    summary = summarize_text(meta["text"], api_key=x_openai_key)
    return SummaryResponse(summary=summary, file_name=meta["file_name"], file_type=meta["file_type"])
