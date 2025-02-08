import { useState, useEffect, useRef } from "react";
import axios from "axios";
import "./Chatbot.css"; // Ensure this is imported

export default function Chatbot() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { text: input, sender: "user" };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    try {
      const response = await axios.post("http://127.0.0.1:8000/chat", { query: input });

      if (response.data.products) {
        setMessages((prev) => [...prev, { text: JSON.stringify(response.data.products, null, 2), sender: "bot" }]);
      } else if (response.data.suppliers) {
        setMessages((prev) => [...prev, { text: JSON.stringify(response.data.suppliers, null, 2), sender: "bot" }]);
      } else {
        setMessages((prev) => [...prev, { text: response.data.reply, sender: "bot" }]);
      }
    } catch (error) {
      console.error("Error fetching chatbot response:", error);
      setMessages((prev) => [...prev, { text: "Sorry, an error occurred!", sender: "bot" }]);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-box">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`chat-message ${msg.sender === "user" ? "user-message" : "bot-message"}`}
          >
            {msg.text}
          </div>
        ))}
        <div ref={chatEndRef} />
      </div>
      <div className="chat-input">
        <input
          type="text"
          placeholder="Type your message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === "Enter" && sendMessage()}
        />
        <button onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
}
