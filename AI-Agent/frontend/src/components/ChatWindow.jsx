import "../styles/ChatWindow.css";

import { useEffect, useRef } from "react";

import ReactMarkdown from "react-markdown";

import remarkGfm from "remark-gfm";

function ChatWindow({ messages }) {

    const bottomRef = useRef(null);

    useEffect(() => {

        bottomRef.current?.scrollIntoView({

            behavior: "smooth"

        });

    }, [messages]);

    return (

        <div className="chat-window">

            {

                messages.map((message, index) => (

                    <div

                        key={index}

                        className={`message ${message.sender}`}

                    >

                        {

                            message.text === "" ?

                            (

                                <div className="typing">

                                    <span></span>

                                    <span></span>

                                    <span></span>

                                </div>

                            )

                            :

                            (

                                <ReactMarkdown
                                remarkPlugins={[remarkGfm]}
                            >
                                {message.text}
                            </ReactMarkdown>
                            )

                        }

                    </div>

                ))

            }

            <div ref={bottomRef}></div>

        </div>

    );

}

export default ChatWindow;