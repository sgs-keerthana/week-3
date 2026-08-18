import "../styles/Sidebar.css";

function Sidebar({

    conversations,

    setMessages,

    setConversationId,

    loadConversations

}) {

    // ===============================
    // Load Conversation
    // ===============================

    const loadConversation = async (id) => {

        try {

            const response = await fetch(
                `http://127.0.0.1:8000/conversation/${id}`
            );

            const data = await response.json();

            const formattedMessages = data.map(chat => ({

                sender: chat.sender.toLowerCase(),

                text: chat.message

            }));

            setMessages(formattedMessages);

            setConversationId(id);

        }

        catch (error) {

            console.error("Error loading conversation:", error);

        }

    };

    // ===============================
    // New Chat
    // ===============================

    const newChat = () => {

        setMessages([]);

        setConversationId(null);

    };

    // ===============================
    // Delete Conversation
    // ===============================

    const deleteConversation = async (id) => {

        const confirmDelete = window.confirm(

            "Are you sure you want to delete this conversation?"

        );

        if (!confirmDelete) {

            return;

        }

        try {

            await fetch(

                `http://127.0.0.1:8000/conversation/${id}`,

                {

                    method: "DELETE"

                }

            );

            // Clear current chat
            setMessages([]);

            setConversationId(null);

            // Refresh sidebar
            loadConversations();

        }

        catch (error) {

            console.error("Delete Failed:", error);

        }

    };

    return (

        <div className="sidebar">

            <button

                className="new-chat"

                onClick={newChat}

            >

                + New Chat

            </button>

            <h3>

                Recent Chats

            </h3>

            {

                conversations.length === 0 ?

                (

                    <p className="empty-chat">

                        No Conversations Yet

                    </p>

                )

                :

                (

                    conversations.map(chat => (

                        <div

                            key={chat.id}

                            className="chat-item"

                        >

                            <span

                                className="chat-title"

                                onClick={() => loadConversation(chat.id)}

                            >

                                {chat.title}

                            </span>

                            <button

                                className="delete-btn"

                                onClick={(e) => {

                                    e.stopPropagation();

                                    deleteConversation(chat.id);

                                }}

                            >

                                🗑

                            </button>

                        </div>

                    ))

                )

            }

        </div>

    );

}

export default Sidebar;