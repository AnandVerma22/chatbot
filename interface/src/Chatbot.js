import React, { useState } from "react";
import axios from "axios";

function Chatbot() {
    const [messages, setMessages] = useState([]); // Stores chat history
    const [input, setInput] = useState(""); // User input
    const [loading, setLoading] = useState(false); // Loading state

    // Function to send user message to FastAPI backend
    const sendMessage = async () => {
        if (!input.trim()) return; // Ignore empty messages
        setLoading(true);

        const newMessages = [...messages, { sender: "user", text: input }];
        setMessages(newMessages);

        try {
            const response = await axios.post("http://127.0.0.1:8000/chat", { query: input });
            setMessages([...newMessages, { sender: "bot", text: response.data.reply || "No response" }]);
        } catch (error) {
            setMessages([...newMessages, { sender: "bot", text: "⚠️ Error: Unable to connect to chatbot." }]);
            console.error("Chatbot API error:", error);
        }

        setInput(""); // Clear input field
        setLoading(false);
    };

    return (
        <div style={styles.container}>
            <h1 style={styles.title}>AI Chatbot</h1>

            <div style={styles.chatbox}>
                {messages.map((msg, index) => (
                    <div key={index} style={msg.sender === "user" ? styles.userMessage : styles.botMessage}>
                        <strong>{msg.sender === "user" ? "You" : "Bot"}:</strong> {msg.text}
                    </div>
                ))}
                {loading && <p style={styles.loading}>⏳ Thinking...</p>}
            </div>

            <div style={styles.inputContainer}>
                <input
                    type="text"
                    style={styles.input}
                    placeholder="Type a message..."
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={(e) => e.key === "Enter" && sendMessage()}
                />
                <button style={styles.button} onClick={sendMessage} disabled={loading}>
                    {loading ? "⏳ Sending..." : "Send"}
                </button>
            </div>
        </div>
    );
}

// CSS styles
const styles = {
    container: {
        width: "400px",
        margin: "20px auto",
        padding: "20px",
        borderRadius: "10px",
        boxShadow: "0px 0px 10px rgba(0, 0, 0, 0.1)",
        fontFamily: "Arial, sans-serif",
        backgroundColor: "#f9f9f9",
    },
    title: {
        textAlign: "center",
        marginBottom: "10px",
        color: "#333",
    },
    chatbox: {
        height: "300px",
        overflowY: "auto",
        padding: "10px",
        backgroundColor: "#fff",
        border: "1px solid #ccc",
        borderRadius: "5px",
        marginBottom: "10px",
    },
    userMessage: {
        textAlign: "right",
        backgroundColor: "#d1e7ff",
        padding: "8px",
        borderRadius: "10px",
        margin: "5px 0",
    },
    botMessage: {
        textAlign: "left",
        backgroundColor: "#e9e9e9",
        padding: "8px",
        borderRadius: "10px",
        margin: "5px 0",
    },
    inputContainer: {
        display: "flex",
        alignItems: "center",
    },
    input: {
        flex: 1,
        padding: "8px",
        borderRadius: "5px",
        border: "1px solid #ccc",
        marginRight: "10px",
    },
    button: {
        padding: "8px 15px",
        borderRadius: "5px",
        border: "none",
        backgroundColor: "#007bff",
        color: "white",
        cursor: "pointer",
    },
    loading: {
        textAlign: "center",
        fontStyle: "italic",
        color: "#777",
    },
};

export default Chatbot;
