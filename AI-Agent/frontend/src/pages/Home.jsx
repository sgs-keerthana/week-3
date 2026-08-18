import "../styles/Home.css";

import Header from "../components/Header";
import Sidebar from "../components/Sidebar";
import ChatWindow from "../components/ChatWindow";
import ChatInput from "../components/ChatInput";

function Home({

    messages,
    setMessages,

    conversations,
    setConversations,

    conversationId,
    setConversationId,

    loadConversations

}) {

    return (

        <div className="home">

            <Sidebar

                conversations={conversations}

                setMessages={setMessages}

                setConversationId={setConversationId}
                 
                loadConversations={loadConversations}

            />

            <div className="workspace">

                <Header/>

                <ChatWindow

                    messages={messages}

                />

                <ChatInput

                    messages={messages}

                    setMessages={setMessages}

                    conversationId={conversationId}

                    setConversationId={setConversationId}

                    loadConversations={loadConversations}

                />

            </div>

        </div>

    );

}

export default Home;