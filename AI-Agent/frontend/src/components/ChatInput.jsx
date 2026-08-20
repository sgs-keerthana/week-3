import { useState } from "react";
import "../styles/ChatInput.css";

function ChatInput({
    setMessages,
    conversationId,
    setConversationId,
    loadConversations
}) {
    const [message, setMessage] = useState("");
    const [loading, setLoading] = useState(false);

    const handleSend = async () => {
        if (message.trim() === "" || loading) return;

        const currentMessage = message;

        // Add user message and temporary AI message
        setMessages(prev => [
            ...prev,
            {
                sender: "user",
                text: currentMessage
            },
            {
                sender: "ai",
                text: "Thinking...",
            
            }
        ]);

        setMessage("");
        setLoading(true);

        try {
            const response = await fetch(
                "http://127.0.0.1:8000/chat",
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        conversation_id: conversationId,
                        message: currentMessage
                    })
                }
            );

            // Check HTTP errors
            if (!response.ok) {
                let errorMessage;

                switch (response.status) {
                    case 400:
                        errorMessage =
                            "⚠ Invalid request. Please check your message and try again.";
                        break;

                    case 408:
                        errorMessage =
                            "⚠ Request timed out. Please try again.";
                        break;

                    case 422:
                        errorMessage =
                            "⚠ Invalid input. Please check your message and try again.";
                        break;

                    case 500:
                        errorMessage =
                            "⚠ Something went wrong on the server. Please try again.";
                        break;

                    case 502:
                    case 503:
                    case 504:
                        errorMessage =
                            "⚠ Workspace AI is temporarily unavailable. Please try again later.";
                        break;

                    default:
                        errorMessage =
                            `⚠ Unable to process your request. Error code: ${response.status}`;
                }

                setMessages(prev => {
                    const updated = [...prev];

                    updated[updated.length - 1] = {
                        sender: "ai",
                        text: errorMessage
                    };

                    return updated;
                });

                return;
            }

            // Get conversation ID from response header
            const newConversationId =
                response.headers.get("X-Conversation-Id");

            if (conversationId == null && newConversationId) {
                const id = Number(newConversationId);

                setConversationId(id);

                await loadConversations();
            }

            // Check if response body exists
            if (!response.body) {
                throw new Error("EMPTY_RESPONSE");
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            let aiResponse = "";

            // Read streaming response
            while (true) {
                const { done, value } = await reader.read();

                if (done) break;

                aiResponse += decoder.decode(value, {
                    stream: true
                });

                setMessages(prev => {
                    const updated = [...prev];

                    updated[updated.length - 1] = {
                        sender: "ai",
                        text: aiResponse
                    };

                    return updated;
                });
            }

            // Check if AI returned an empty response
            if (aiResponse.trim() === "") {
                setMessages(prev => {
                    const updated = [...prev];

                    updated[updated.length - 1] = {
                        sender: "ai",
                        text: "⚠ No response was received from Workspace AI. Please try again."
                    };

                    return updated;
                });
            }

        } catch (error) {
            let errorMessage;

            // Backend/network connection failure
            if (error instanceof TypeError) {
                errorMessage =
                    "⚠ Unable to connect to Workspace AI. Please check that the backend is running.";
            }

            // Empty response from backend
            else if (error.message === "EMPTY_RESPONSE") {
                errorMessage =
                    "⚠ Workspace AI returned an empty response. Please try again.";
            }

            // Any unexpected error
            else {
                errorMessage =
                    "⚠ Something went wrong while processing your request. Please try again.";
            }

            setMessages(prev => {
                const updated = [...prev];

                updated[updated.length - 1] = {
                    sender: "ai",
                    text: errorMessage
                };

                return updated;
            });

        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="chat-input">

            <input
                value={message}
                placeholder="Ask Workspace AI..."
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                        e.preventDefault();
                        handleSend();
                    }
                }}
            />

            <button
                onClick={handleSend}
                disabled={loading}
            >
                {loading ? "Sending..." : "Send"}
            </button>

        </div>
    );
}

export default ChatInput;