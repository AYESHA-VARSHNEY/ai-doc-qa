import os
import openai

def transcribe_audio(file_path: str, api_key: str = "") -> dict:
    # Agar Groq key hai toh Groq ka endpoint use karega
    if api_key.startswith("gsk_"):
        client = openai.OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=api_key
        )
    else:
        client = openai.OpenAI(api_key=api_key)

    with open(file_path, "rb") as f:
        response = client.audio.transcriptions.create(
            model="whisper-large-v3" if api_key.startswith("gsk_") else "whisper-1",
            file=f,
            response_format="verbose_json"
        )
    
    segments = [{"start": seg.get("start"), "end": seg.get("end"), "text": seg.get("text")} for seg in response.segments]
    return {"full_text": response.text, "segments": segments}

def find_timestamp_for_answer(answer: str, segments: list) -> float:
    answer_words = set(answer.lower().split())
    best_score, best_ts = 0, 0.0
    for seg in segments:
        overlap = len(answer_words & set(seg["text"].lower().split()))
        if overlap > best_score:
            best_score = overlap
            best_ts = seg["start"]
    return best_ts