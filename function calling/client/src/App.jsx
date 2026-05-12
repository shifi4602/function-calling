import { useState, useRef, useEffect } from "react";

const API_URL = "/chat";

export default function App() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      text: "שלום! אני כאן לעזור לך לנהל את המשימות שלך 😊\nספרי לי מה את צריכה – להוסיף משימה, לעדכן, למחוק, או פשוט לראות מה יש ברשימה.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const sendMessage = async () => {
    const text = input.trim();
    if (!text || loading) return;
    setMessages((prev) => [...prev, { role: "user", text }]);
    setInput("");
    setLoading(true);
    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
      });
      const data = await res.json();
      setMessages((prev) => [...prev, { role: "assistant", text: data.reply }]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: "אירעה שגיאה בתקשורת עם השרת. נסי שוב." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="chat-container">
      <header className="chat-header">
        <span className="chat-header-icon">🤖</span>
        <h1>מנהל המשימות החכם</h1>
      </header>
      <div className="messages">
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            <div className="bubble">
              {msg.text.split("\n").map((line, j) => (
                <span key={j}>{line}<br /></span>
              ))}
            </div>
          </div>
        ))}
        {loading && (
          <div className="message assistant">
            <div className="bubble typing">
              <span className="dot" /><span className="dot" /><span className="dot" />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>
      <div className="input-row">
        <textarea
          className="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="כתבי את הבקשה שלך כאן..."
          rows={2}
          disabled={loading}
        />
        <button className="send-btn" onClick={sendMessage} disabled={loading || !input.trim()}>
          שלח
        </button>
      </div>
    </div>
  );
}