import React from "react";

export default function MediaPlayer({ timestamp }) {
  const formatTime = (secs) => {
    const m = Math.floor(secs / 60).toString().padStart(2, "0");
    const s = Math.floor(secs % 60).toString().padStart(2, "0");
    return `${m}:${s}`;
  };

  return (
    <div className="media-player-banner">
      <span>🎯 Relevant section found at <strong>{formatTime(timestamp)}</strong></span>
      <button
        className="play-btn"
        onClick={() => alert(`Jump to ${formatTime(timestamp)} in your media player`)}
      >
        ▶ Play from here
      </button>
    </div>
  );
}
