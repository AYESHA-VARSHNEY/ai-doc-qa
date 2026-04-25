from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.responses import StreamingResponse
from models.schemas import ChatRequest, ChatResponse
from services.llm_service import query_document, vector_stores, get_model_and_provider
from services.vector_service import get_file_metadata
from services.transcription_service import find_timestamp_for_answer
from routers.auth import get_current_user
from typing import Optional
import json
import litellm

router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def chat(req: ChatRequest, user: str = Depends(get_current_user), x_openai_key: Optional[str] = Header(None)):
    if not x_openai_key:
        raise HTTPException(400, "API key missing.")
    meta = await get_file_metadata(req.file_id)
    if not meta:
         raise HTTPException(404, "File not found")
    answer = query_document(req.file_id, req.question, api_key=x_openai_key)
    timestamp = None
    if meta and meta.get("segments"):
        timestamp = find_timestamp_for_answer(answer, meta["segments"])
    return ChatResponse(answer=answer, timestamp=timestamp, source=meta["file_name"] if meta else "Unknown")

@router.post("/stream")
async def chat_stream(req: ChatRequest, user: str = Depends(get_current_user), x_openai_key: Optional[str] = Header(None)):
    if not x_openai_key:
        raise HTTPException(400, "API key missing.")
    
    model, key = get_model_and_provider(x_openai_key)
    vs = vector_stores.get(req.file_id)
    if not vs:
        raise HTTPException(400, "Document not indexed")

    docs = vs.similarity_search(req.question, k=3)
    context = "\n".join([d.page_content for d in docs])
    prompt = f"Context:\n{context}\n\nQuestion: {req.question}\nAnswer:"

    async def generate():
        response = litellm.completion(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            api_key=key,
            stream=True
        )
        for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                yield f"data: {json.dumps({'token': content})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")