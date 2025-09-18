import { useState } from "react";
import { motion } from "framer-motion";

function App() {
  const [messages, setMessages] = useState([
    { role: "assistant", text: "👋 Hi! Type something to start." },
  ]);
  const [input, setInput] = useState("");

  const sendMessage = async () => {
    if (!input.trim()) return;

    const newMessages = [...messages, { role: "user", text: input }];
    setMessages(newMessages);
    setInput("");

    try {
      const resp = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input }),
      });

      const data = await resp.json();

      setMessages([
        ...newMessages,
        { role: "assistant", text: data.reply || "⚠️ Response error" },
      ]);
    } catch (err) {
      setMessages([
        ...newMessages,
        { role: "assistant", text: "❌ Server error" },
      ]);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black text-white">
      {/* Chat box */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.map((msg, idx) => (
          <motion.div
            key={idx}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2 }}
            className={`max-w-lg p-4 rounded-2xl shadow-lg ${
              msg.role === "user"
                ? "bg-indigo-600 ml-auto text-white"
                : "bg-gray-800 text-gray-100"
            }`}
          >
            {msg.text}
          </motion.div>
        ))}
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-700 bg-black/60 backdrop-blur">
        <div className="flex gap-2">
          <input
            className="flex-1 px-4 py-2 rounded-xl bg-gray-900 text-white border border-gray-700 focus:ring-2 focus:ring-indigo-500 outline-none"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            placeholder="Type a message..."
          />
          <button
            onClick={sendMessage}
            className="px-6 py-2 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-semibold shadow-lg hover:from-indigo-600 hover:to-purple-700 transition"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;
