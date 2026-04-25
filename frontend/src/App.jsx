import React, { useState } from "react";
import FileUpload from "./components/FileUpload";
import ChatBot from "./components/ChatBot";
import Summary from "./components/Summary";
import Auth from "./components/Auth";
import "./index.css";

export default function App() {
  const [token, setToken] = useState(localStorage.getItem("token") || "");
  const [fileId, setFileId] = useState(null);
  const [fileName, setFileName] = useState("");
  const [fileType, setFileType] = useState("");
  const [activeTab, setActiveTab] = useState("chat");

  const handleLogout = () => {
    localStorage.removeItem("token");
    setToken("");
  };

  if (!token) return <Auth onLogin={setToken} />;

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>🤖 AI Document & Media Q&A</h1>
        <button className="logout-btn" onClick={handleLogout}>Logout</button>
      </header>

      <div className="main-layout">
        <aside className="sidebar">
          <FileUpload
            token={token}
            onUpload={(id, name, type) => {
              setFileId(id);
              setFileName(name);
              setFileType(type);
            }}
          />
          {fileId && (
            <div className="file-badge">
              📄 <strong>{fileName}</strong>
              <span className="tag">{fileType}</span>
            </div>
          )}
        </aside>

        <main className="content">
          {fileId ? (
            <>
              <div className="tabs">
                <button
                  className={activeTab === "chat" ? "tab active" : "tab"}
                  onClick={() => setActiveTab("chat")}
                >
                  💬 Chat
                </button>
                <button
                  className={activeTab === "summary" ? "tab active" : "tab"}
                  onClick={() => setActiveTab("summary")}
                >
                  📝 Summary
                </button>
              </div>
              {activeTab === "chat" ? (
                <ChatBot token={token} fileId={fileId} fileType={fileType} />
              ) : (
                <Summary token={token} fileId={fileId} />
              )}
            </>
          ) : (
            <div className="empty-state">
              <div className="empty-icon">📂</div>
              <p>Upload a PDF, audio, or video file to get started</p>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
