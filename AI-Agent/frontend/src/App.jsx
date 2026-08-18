import { useState, useEffect } from "react";
import Home from "./pages/Home";

function App() {

    const [messages, setMessages] = useState([]);
    const [conversations, setConversations] = useState([]);
    const [conversationId, setConversationId] = useState(null);

    useEffect(() => {
        loadConversations();
    }, []);

    const loadConversations = async () => {

        try {

            const response = await fetch(
                "http://127.0.0.1:8000/conversations"
            );

            const data = await response.json();

            setConversations(data);

        } catch (error) {

            console.error(error);

        }

    };

    return (

        <Home
            messages={messages}
            setMessages={setMessages}

            conversations={conversations}

            conversationId={conversationId}
            setConversationId={setConversationId}

            loadConversations={loadConversations}
        />

    );

}

export default App;