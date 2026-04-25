import React, { useState } from "react";
import axios from "axios";

const API = process.env.REACT_APP_API_URL || "http://localhost:8000";

function detectProvider(key) {
  if (!key) return "";
  if (key.startsWith("gsk_")) return "✅ Groq detected";
  if (key.startsWith("AIza")) return "✅ Google Gemini detected";
  if (key.startsWith("sk-ant")) return "✅ Anthropic detected";
  if (key.startsWith("sk-or-")) return "✅ OpenRouter detected";
  if (key.startsWith("sk-")) return "✅ OpenAI detected";
  return "⚠️ Unknown key format";
}

export default function Auth({ onLogin }) {
  const [mode, setMode] = useState("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const providerHint = detectProvider(apiKey);

  const handleSubmit = async () => {
    if (mode === "register" && !apiKey.trim()) {
      setError("API key is required.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      if (mode === "register") {
        await axios.post(`${API}/auth/register`, { username, password });
        localStorage.setItem("openai_key", apiKey.trim());
        setMode("login");
        setError("✅ Registered! Please login now.");
        return;
      }
      const res = await axios.post(`${API}/auth/login`, { username, password });
      localStorage.setItem("token", res.data.access_token);
      onLogin(res.data.access_token);
    } catch (e) {
      setError(e.response?.data?.detail || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>🤖 AI Doc Q&amp;A</h2>
        <p className="auth-subtitle">
          {mode === "login" ? "Sign in to continue" : "Create your account"}
        </p>
        <input
          placeholder="Username"
          value={username}
          onChange={e => setUsername(e.target.value)}
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          onKeyDown={e => e.key === "Enter" && handleSubmit()}
        />
        {mode === "register" && (
          <>
            <input
              type="password"
              placeholder="API Key (Groq / Gemini / OpenAI / Anthropic)"
              value={apiKey}
              onChange={e => setApiKey(e.target.value)}
            />
            {apiKey && <p className="provider-hint">{providerHint}</p>}
            <div className="key-note">
              <p>🔒 Key stored only in your browser — never on server</p>
              <p style={{marginTop:"6px", color:"#94a3b8"}}>Supported providers:</p>
              <div className="provider-list">
                <span>🟢 Groq (free)</span>
                <span>🔵 Gemini (free)</span>
                <span>🟣 OpenAI</span>
                <span>🟠 Anthropic</span>
              </div>
            </div>
          </>
        )}
        {error && <p className="error-text">{error}</p>}
        <button onClick={handleSubmit} disabled={loading}>
          {loading ? "Please wait..." : mode === "login" ? "Login" : "Register"}
        </button>
        <p className="switch-mode">
          {mode === "login" ? "Don't have an account?" : "Already have an account?"}
          <span onClick={() => { setMode(mode === "login" ? "register" : "login"); setError(""); }}>
            {mode === "login" ? " Register" : " Login"}
          </span>
        </p>
      </div>
    </div>
  );
}