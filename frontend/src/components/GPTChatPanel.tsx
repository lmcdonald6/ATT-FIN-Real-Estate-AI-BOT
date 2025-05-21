import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { askApi } from "../utils/apiClient"; // Using the existing API client

interface GPTChatPanelProps {
  initialPrompt?: string;
}

export default function GPTChatPanel({ initialPrompt = "" }: GPTChatPanelProps) {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Array<{role: string, content: string}>>([]);
  const [loading, setLoading] = useState(false);
  
  // Handle initial prompt if provided
  useEffect(() => {
    if (initialPrompt && initialPrompt.trim() !== "") {
      handleInitialPrompt(initialPrompt);
    }
  }, [initialPrompt]);
  
  const handleInitialPrompt = async (prompt: string) => {
    // Only process the initial prompt if we don't have any messages yet
    if (messages.length === 0) {
      const userMessage = { role: "user", content: prompt };
      setMessages([userMessage]);
      setLoading(true);
      
      try {
        // Call the API using the existing askApi client
        const response = await askApi.askQuestion(prompt);
        
        // Add bot response to the chat
        const botMessage = { 
          role: "bot", 
          content: response.answer || "I couldn't find an answer to that question."
        };
        
        setMessages([userMessage, botMessage]);
      } catch (error) {
        console.error("Error fetching GPT response:", error);
        const errorMessage = { 
          role: "bot", 
          content: "Sorry, I encountered an error while processing your request."
        };
        setMessages([userMessage, errorMessage]);
      } finally {
        setLoading(false);
      }
    }
  };

  const handleSend = async () => {
    if (!input.trim()) return;
    
    // Add user message to the chat
    const userMessage = { role: "user", content: input };
    setMessages(prev => [...prev, userMessage]);
    setLoading(true);
    
    try {
      // Call the API using the existing askApi client
      const response = await askApi.askQuestion(input);
      
      // Add bot response to the chat
      const botMessage = { 
        role: "bot", 
        content: response.answer || "I couldn't find an answer to that question."
      };
      
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error("Error fetching GPT response:", error);
      const errorMessage = { 
        role: "bot", 
        content: "Sorry, I encountered an error while processing your request."
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setInput("");
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-xl mx-auto bg-white rounded-2xl shadow-lg p-6">
      <div className="h-60 overflow-y-auto mb-4 flex flex-col gap-2">
        {messages.length === 0 && (
          <div className="text-gray-400 text-center py-10">
            Ask me anything about real estate, neighborhoods, or market trends!
          </div>
        )}
        
        {messages.map((msg, idx) => (
          <motion.div
            key={idx}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className={`p-3 rounded-lg max-w-[80%] ${msg.role === "user" 
              ? "bg-blue-100 text-right ml-auto" 
              : "bg-gray-100 text-left mr-auto"}`}
          >
            {msg.content}
          </motion.div>
        ))}
        
        {loading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ 
              opacity: [0.4, 0.7, 0.4],
              transition: { 
                repeat: Infinity, 
                duration: 1.5 
              }
            }}
            className="bg-gray-100 p-3 rounded-lg text-gray-500 mr-auto flex items-center gap-1"
          >
            <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></span>
            <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></span>
            <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: "0.4s" }}></span>
          </motion.div>
        )}
      </div>
      
      <div className="flex gap-2">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => { if (e.key === "Enter") handleSend(); }}
          className="flex-1 border rounded-lg p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Ask about any ZIP, trend, or persona fit..."
        />
        <button
          onClick={handleSend}
          disabled={loading || !input.trim()}
          className="px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700 transition-colors disabled:bg-blue-300"
        >
          Send
        </button>
      </div>
    </div>
  );
}
