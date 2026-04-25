from motor.motor_asyncio import AsyncIOMotorClient
import os

client = AsyncIOMotorClient(os.getenv("MONGO_URL", "mongodb://mongo:27017"))
db = client["ai_doc_qa"]
files_collection = db["files"]

async def save_file_metadata(file_id: str, file_name: str, file_type: str, text: str, segments: list = None):
    doc = {
        "_id": file_id,
        "file_name": file_name,
        "file_type": file_type,
        "text": text,
        "segments": segments or []
    }
    await files_collection.replace_one({"_id": file_id}, doc, upsert=True)

async def get_file_metadata(file_id: str):
    return await files_collection.find_one({"_id": file_id})
