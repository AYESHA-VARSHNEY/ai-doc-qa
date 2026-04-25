from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Header
from routers.auth import get_current_user
from services.transcription_service import transcribe_audio
from services.vector_service import save_file_metadata
from services.llm_service import index_text
import PyPDF2, uuid, os, aiofiles
from typing import Optional

router = APIRouter()
UPLOAD_DIR = "/tmp/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/")
async def upload_file(
    file: UploadFile = File(...), 
    user: str = Depends(get_current_user),
    x_openai_key: Optional[str] = Header(None)
):
    # Agar header missing hai toh hum user ke password (jo login ke waqt use kiya) ko key maan sakte hain
    # Lekin filhal security ke liye hum error ko thoda detail mein likhte hain
    api_key = x_openai_key
    if not api_key:
        raise HTTPException(400, "API Key missing in headers (X-OpenAI-Key)")

    file_id = str(uuid.uuid4())
    ext = file.filename.split(".")[-1].lower()
    file_path = f"{UPLOAD_DIR}/{file_id}.{ext}"

    # File save logic
    try:
        async with aiofiles.open(file_path, "wb") as f:
            content = await file.read()
            await f.write(content)
    except Exception as e:
        raise HTTPException(500, f"Could not save file: {str(e)}")

    text = ""
    segments = []

    # PDF Processing with Error Handling
    if ext == "pdf":
        try:
            reader = PyPDF2.PdfReader(file_path)
            pages_text = []
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    pages_text.append(extracted)
            text = " ".join(pages_text)
            
            if not text.strip():
                text = "This PDF seems to be an image or empty. No text could be extracted."
            
            file_type = "pdf"
        except Exception as e:
            raise HTTPException(400, f"Failed to read PDF: {str(e)}")

    # Audio/Video Processing
    elif ext in ["mp3", "wav", "m4a", "mp4", "webm", "ogg"]:
        try:
            result = transcribe_audio(file_path, api_key=api_key)
            text = result["full_text"]
            segments = result["segments"]
            file_type = "audio" if ext in ["mp3", "wav", "m4a", "ogg"] else "video"
        except Exception as e:
            raise HTTPException(400, f"Transcription failed: {str(e)}")
    else:
        raise HTTPException(400, f"Unsupported file type: {ext}")

    # Indexing
    try:
        index_text(file_id, text, api_key=api_key)
        await save_file_metadata(file_id, file.filename, file_type, text, segments)
    except Exception as e:
        raise HTTPException(500, f"Indexing failed: {str(e)}")

    return {
        "file_id": file_id,
        "file_name": file.filename,
        "file_type": file_type,
        "message": "File uploaded and indexed successfully"
    }