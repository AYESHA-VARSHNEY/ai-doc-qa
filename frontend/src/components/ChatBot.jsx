import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import MediaPlayer from "./MediaPlayer";

const API = process.env.REACT_APP_API_URL || "http://localhost:8000";

export default function ChatBot({ token, fileId, fileType }) {
  const [messages, setMessages] = useState([
    { role: "ai", text: "Hello! Ask me anything about your uploaded file 👋" }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [mediaTs, setMediaTs] = useState(null);
  const bottomRef = useRef(null);
  const apiKey = localStorage.getItem("openai_key") || "";

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMsg = input.trim();
    setInput("");
    setMessages(prev => [...prev, { role: "user", text: userMsg }]);
    setLoading(true);

    try {
      const res = await fetch(`${API}/chat/stream`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
          "X-OpenAI-Key": apiKey,
        },
        body: JSON.stringify({ file_id: fileId, question: userMsg }),
      });

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let aiText = "";
      setMessages(prev => [...prev, { role: "ai", text: "", streaming: true }]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const lines = decoder.decode(value).split("\n");
        for (const line of lines) {
          if (line.startsWith("data: ") && line !== "data: [DONE]") {
            try {
              const data = JSON.parse(line.slice(6));
              aiText += data.token;
              setMessages(prev => {
                const updated = [...prev];
                updated[updated.length - 1] = { role: "ai", text: aiText, streaming: true };
                return updated;
              });
            } catch (_) {}
          }
        }
      }

      setMessages(prev => {
        const updated = [...prev];
        updated[updated.length - 1] = { role: "ai", text: aiText };
        return updated;
      });

      if (["audio", "video"].includes(fileType)) {
        const tsRes = await axios.post(
          `${API}/chat/`,
          { file_id: fileId, question: userMsg },
          { headers: { Authorization: `Bearer ${token}`, "X-OpenAI-Key": apiKey } }
        );
        if (tsRes.data.timestamp != null) setMediaTs(tsRes.data.timestamp);
      }
    } catch (e) {
      setMessages(prev => [...prev, { role: "ai", text: "❌ Error getting response. Check your API key." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-container">
      {!apiKey && (
        <div className="key-warning">
          ⚠️ No API key found. Please logout and register again with your OpenAI key.
        </div>
      )}
      {mediaTs !== null && ["audio", "video"].includes(fileType) && (
        <MediaPlayer timestamp={mediaTs} fileType={fileType} />
      )}
      <div className="messages">
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            <div className="bubble">
              {msg.role === "ai"
                ? <ReactMarkdown>{msg.text || "▋"}</ReactMarkdown>
                : msg.text}
            </div>
          </div>
        ))}
        {loading && (
          <div className="message ai">
            <div className="bubble typing">⏳ Thinking...</div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>
      <div className="chat-input-bar">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === "Enter" && !loading && sendMessage()}
          placeholder="Ask a question about your file..."
        />
        <button onClick={sendMessage} disabled={loading}>Send</button>
      </div>
    </div>
  );
}
