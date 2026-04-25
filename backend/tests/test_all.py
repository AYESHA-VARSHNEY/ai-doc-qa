import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock, MagicMock
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from main import app

async def get_token(client: AsyncClient) -> str:
    await client.post("/auth/register", json={"username": "testuser", "password": "testpass"})
    r = await client.post("/auth/login", json={"username": "testuser", "password": "testpass"})
    return r.json()["access_token"]

@pytest.fixture
async def ac():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c

@pytest.mark.asyncio
async def test_register(ac):
    r = await ac.post("/auth/register", json={"username": "u1", "password": "p1"})
    assert r.status_code == 200

@pytest.mark.asyncio
async def test_register_duplicate(ac):
    await ac.post("/auth/register", json={"username": "dup", "password": "p"})
    r = await ac.post("/auth/register", json={"username": "dup", "password": "p"})
    assert r.status_code == 400

@pytest.mark.asyncio
async def test_login_success(ac):
    await ac.post("/auth/register", json={"username": "u2", "password": "p2"})
    r = await ac.post("/auth/login", json={"username": "u2", "password": "p2"})
    assert r.status_code == 200
    assert "access_token" in r.json()

@pytest.mark.asyncio
async def test_login_fail(ac):
    r = await ac.post("/auth/login", json={"username": "noone", "password": "wrong"})
    assert r.status_code == 401

@pytest.mark.asyncio
async def test_health(ac):
    r = await ac.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_upload_pdf(ac):
    token = await get_token(ac)
    headers = {"Authorization": f"Bearer {token}", "X-OpenAI-Key": "sk-test"}
    pdf_bytes = b"%PDF-1.4 1 0 obj<</Type/Catalog>>endobj\n%%EOF"
    with patch("routers.upload.PyPDF2.PdfReader") as mock_pdf, \
         patch("routers.upload.index_text", return_value=True), \
         patch("routers.upload.save_file_metadata", new_callable=AsyncMock):
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Sample text"
        mock_pdf.return_value.pages = [mock_page]
        r = await ac.post("/upload/", files={"file": ("test.pdf", pdf_bytes, "application/pdf")}, headers=headers)
    assert r.status_code == 200
    assert r.json()["file_type"] == "pdf"

@pytest.mark.asyncio
async def test_upload_unsupported(ac):
    token = await get_token(ac)
    headers = {"Authorization": f"Bearer {token}", "X-OpenAI-Key": "sk-test"}
    r = await ac.post("/upload/", files={"file": ("test.txt", b"hello", "text/plain")}, headers=headers)
    assert r.status_code == 400

@pytest.mark.asyncio
async def test_upload_no_key(ac):
    token = await get_token(ac)
    headers = {"Authorization": f"Bearer {token}"}
    r = await ac.post("/upload/", files={"file": ("test.pdf", b"%PDF", "application/pdf")}, headers=headers)
    assert r.status_code == 400

@pytest.mark.asyncio
async def test_upload_audio(ac):
    token = await get_token(ac)
    headers = {"Authorization": f"Bearer {token}", "X-OpenAI-Key": "sk-test"}
    with patch("routers.upload.transcribe_audio", return_value={"full_text": "hi", "segments": []}), \
         patch("routers.upload.index_text", return_value=True), \
         patch("routers.upload.save_file_metadata", new_callable=AsyncMock):
        r = await ac.post("/upload/", files={"file": ("audio.mp3", b"fake-mp3", "audio/mpeg")}, headers=headers)
    assert r.status_code == 200
    assert r.json()["file_type"] == "audio"

@pytest.mark.asyncio
async def test_chat_success(ac):
    token = await get_token(ac)
    headers = {"Authorization": f"Bearer {token}", "X-OpenAI-Key": "sk-test"}
    mock_meta = {"_id": "fid1", "file_name": "test.pdf", "file_type": "pdf", "text": "hello world", "segments": []}
    with patch("routers.chat.get_file_metadata", new_callable=AsyncMock, return_value=mock_meta), \
         patch("routers.chat.query_document", return_value="The answer is 42"):
        r = await ac.post("/chat/", json={"file_id": "fid1", "question": "What is the answer?"}, headers=headers)
    assert r.status_code == 200
    assert r.json()["answer"] == "The answer is 42"

@pytest.mark.asyncio
async def test_chat_not_found(ac):
    token = await get_token(ac)
    headers = {"Authorization": f"Bearer {token}", "X-OpenAI-Key": "sk-test"}
    with patch("routers.chat.get_file_metadata", new_callable=AsyncMock, return_value=None):
        r = await ac.post("/chat/", json={"file_id": "missing", "question": "?"}, headers=headers)
    assert r.status_code == 404

@pytest.mark.asyncio
async def test_chat_no_key(ac):
    token = await get_token(ac)
    headers = {"Authorization": f"Bearer {token}"}
    r = await ac.post("/chat/", json={"file_id": "fid1", "question": "?"}, headers=headers)
    assert r.status_code == 400

@pytest.mark.asyncio
async def test_chat_with_timestamp(ac):
    token = await get_token(ac)
    headers = {"Authorization": f"Bearer {token}", "X-OpenAI-Key": "sk-test"}
    segments = [{"start": 5.0, "end": 10.0, "text": "The answer is found here"}]
    mock_meta = {"_id": "fid2", "file_name": "vid.mp4", "file_type": "video",
                 "text": "The answer is found here", "segments": segments}
    with patch("routers.chat.get_file_metadata", new_callable=AsyncMock, return_value=mock_meta), \
         patch("routers.chat.query_document", return_value="The answer is found here"):
        r = await ac.post("/chat/", json={"file_id": "fid2", "question": "answer?"}, headers=headers)
    assert r.status_code == 200
    assert r.json()["timestamp"] is not None

@pytest.mark.asyncio
async def test_summary_success(ac):
    token = await get_token(ac)
    headers = {"Authorization": f"Bearer {token}", "X-OpenAI-Key": "sk-test"}
    mock_meta = {"_id": "fid3", "file_name": "doc.pdf", "file_type": "pdf",
                 "text": "Long content here", "segments": []}
    with patch("routers.summary.get_file_metadata", new_callable=AsyncMock, return_value=mock_meta), \
         patch("routers.summary.summarize_text", return_value="• Point 1\n• Point 2"):
        r = await ac.post("/summary/", json={"file_id": "fid3"}, headers=headers)
    assert r.status_code == 200
    assert "Point 1" in r.json()["summary"]

@pytest.mark.asyncio
async def test_summary_not_found(ac):
    token = await get_token(ac)
    headers = {"Authorization": f"Bearer {token}", "X-OpenAI-Key": "sk-test"}
    with patch("routers.summary.get_file_metadata", new_callable=AsyncMock, return_value=None):
        r = await ac.post("/summary/", json={"file_id": "missing"}, headers=headers)
    assert r.status_code == 404

@pytest.mark.asyncio
async def test_summary_no_key(ac):
    token = await get_token(ac)
    headers = {"Authorization": f"Bearer {token}"}
    r = await ac.post("/summary/", json={"file_id": "fid3"}, headers=headers)
    assert r.status_code == 400

# LLM Service tests — litellm mock
def test_index_text():
    with patch("services.llm_service.FAISS") as mock_faiss, \
         patch("services.llm_service.DeterministicFakeEmbedding"):
        mock_vs = MagicMock()
        mock_faiss.from_documents.return_value = mock_vs
        from services.llm_service import index_text, vector_stores
        index_text("tid1", "some sample text", api_key="gsk_test")
        assert "tid1" in vector_stores

def test_query_not_indexed():
    from services.llm_service import query_document
    result = query_document("nonexistent_id_xyz", "question?")
    assert "not indexed" in result.lower()

def test_query_document():
    with patch("services.llm_service.litellm.completion") as mock_completion, \
         patch("services.llm_service.FAISS") as mock_faiss, \
         patch("services.llm_service.DeterministicFakeEmbedding"):
        mock_vs = MagicMock()
        mock_vs.similarity_search.return_value = [MagicMock(page_content="context text")]
        mock_faiss.from_documents.return_value = mock_vs
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Test answer"))]
        )
        from services.llm_service import index_text, query_document
        index_text("tid2", "some text", api_key="sk-test")
        result = query_document("tid2", "what?", api_key="sk-test")
        assert result == "Test answer"

def test_summarize_text():
    with patch("services.llm_service.litellm.completion") as mock_completion:
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="• Summary point"))]
        )
        from services.llm_service import summarize_text
        result = summarize_text("Some long text", api_key="sk-test")
        assert "Summary" in result

def test_detect_provider():
    from services.llm_service import get_model_and_provider
    model, _ = get_model_and_provider("gsk_test")
    assert "groq" in model
    model2, _ = get_model_and_provider("AIzatest")
    assert "gemini" in model2
    model3, _ = get_model_and_provider("sk-test")
    assert "gpt" in model3

def test_find_timestamp():
    from services.transcription_service import find_timestamp_for_answer
    segments = [
        {"start": 0.0, "end": 5.0, "text": "Hello world"},
        {"start": 5.0, "end": 10.0, "text": "The answer is here"},
    ]
    ts = find_timestamp_for_answer("The answer is here in this segment", segments)
    assert ts == 5.0

def test_find_timestamp_no_match():
    from services.transcription_service import find_timestamp_for_answer
    result = find_timestamp_for_answer("xyz", [])
    assert result == 0.0