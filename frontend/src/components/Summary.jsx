import React, { useState } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";

const API = process.env.REACT_APP_API_URL || "http://localhost:8000";

export default function Summary({ token, fileId }) {
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(false);
  const apiKey = localStorage.getItem("openai_key") || "";

  const fetchSummary = async () => {
    setLoading(true);
    try {
      const res = await axios.post(
        `${API}/summary/`,
        { file_id: fileId },
        { headers: { Authorization: `Bearer ${token}`, "X-OpenAI-Key": apiKey } }
      );
      setSummary(res.data.summary);
    } catch (e) {
      setSummary("❌ Failed to generate summary.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="summary-container">
      <button className="summary-btn" onClick={fetchSummary} disabled={loading}>
        {loading ? "⏳ Generating..." : "📝 Generate Summary"}
      </button>
      {summary && (
        <div className="summary-content">
          <ReactMarkdown>{summary}</ReactMarkdown>
        </div>
      )}
    </div>
  );
}
