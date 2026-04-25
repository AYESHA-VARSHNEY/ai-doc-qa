import React, { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import axios from "axios";

const API = process.env.REACT_APP_API_URL || "http://localhost:8000";

export default function FileUpload({ token, onUpload }) {
  const [status, setStatus] = useState("");
  const [uploading, setUploading] = useState(false);
  const apiKey = localStorage.getItem("openai_key") || "";

  const onDrop = useCallback(async (accepted) => {
    if (!accepted.length) return;
    const file = accepted[0];
    setUploading(true);
    setStatus("Uploading & processing...");
    const form = new FormData();
    form.append("file", file);

    try {
      const res = await axios.post(`${API}/upload/`, form, {
        headers: {
          Authorization: `Bearer ${token}`,
          "X-OpenAI-Key": apiKey,
          "Content-Type": "multipart/form-data",
        },
      });
      const { file_id, file_name, file_type } = res.data;
      setStatus(`✅ Uploaded: ${file_name}`);
      onUpload(file_id, file_name, file_type);
    } catch (e) {
      setStatus("❌ " + (e.response?.data?.detail || "Upload failed"));
    } finally {
      setUploading(false);
    }
  }, [token, onUpload, apiKey]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "audio/*": [".mp3", ".wav", ".m4a", ".ogg"],
      "video/*": [".mp4", ".webm"],
    },
    multiple: false,
  });

  return (
    <div className="upload-section">
      <h3>📤 Upload File</h3>
      <div {...getRootProps()} className={`dropzone ${isDragActive ? "active" : ""}`}>
        <input {...getInputProps()} />
        {uploading ? (
          <div className="spinner">⏳ Processing...</div>
        ) : (
          <>
            <div className="drop-icon">🗂️</div>
            <p>{isDragActive ? "Drop it here!" : "Drag & drop or click to upload"}</p>
            <small>PDF • MP3 • WAV • MP4 • WebM</small>
          </>
        )}
      </div>
      {status && <p className="upload-status">{status}</p>}
    </div>
  );
}
