from fastapi import FastAPI, Depends
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import time

from agent import agent
import db_models
import settings

from database import engine, SessionLocal

from crud import (
    create_conversation,
    save_message,
    get_conversations,
    get_messages,
    delete_conversation,
    get_conversation_context
)

from schemas import ChatRequest


# -----------------------------
# Create Database Tables
# -----------------------------
db_models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# -----------------------------
# Database Connection
# -----------------------------
def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# -----------------------------
# CORS
# -----------------------------
app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5175",
        "http://127.0.0.1:5175",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],

    expose_headers=["X-Conversation-Id"],
)


# -----------------------------
# Home
# -----------------------------
@app.get("/")
def home():

    return {
        "message": "Workspace AI Backend Running"
    }


# ==================================================
# Get Recent Conversations
# ==================================================
@app.get("/conversations")
def conversations(
    db: Session = Depends(get_db)
):

    return get_conversations(db)


# ==================================================
# Load One Conversation
# ==================================================
@app.get("/conversation/{conversation_id}")
def conversation_history(
    conversation_id: int,
    db: Session = Depends(get_db)
):

    return get_messages(
        db,
        conversation_id
    )


# ==================================================
# Delete Conversation
# ==================================================
@app.delete("/conversation/{conversation_id}")
def delete_chat(
    conversation_id: int,
    db: Session = Depends(get_db)
):

    delete_conversation(
        db,
        conversation_id
    )

    return {
        "message": "Conversation Deleted"
    }


# ==================================================
# Chat
# ==================================================
@app.post("/chat")
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):

    conversation_id = request.conversation_id


    # --------------------------------------------------
    # Create New Conversation
    # --------------------------------------------------

    if conversation_id is None:

        conversation = create_conversation(
            db,
            request.message[:40]
        )

        conversation_id = conversation.id


    # --------------------------------------------------
    # Save User Message
    # --------------------------------------------------

    save_message(
        db,
        conversation_id,
        "User",
        request.message
    )


    # ==================================================
    # Generate Response
    # ==================================================

    def generate():

        # --------------------------------------------------
        # Get Previous Conversation Messages
        # --------------------------------------------------

        conversation_history = get_conversation_context(
            db,
            conversation_id
        )


        # --------------------------------------------------
        # Add System Prompt
        # --------------------------------------------------

        conversation_history = [

            {
                "role": "system",
                "content": settings.SYSTEM_PROMPT
            }

        ] + conversation_history


        # --------------------------------------------------
        # Response Variables
        # --------------------------------------------------

        full_response = ""

        # Stores execution information
        execution_logs = []

        # Keeps track of tool order
        execution_order = 0

        # Stores start time and arguments
        tool_start_times = {}


        # ==================================================
        # Stream Agent
        # ==================================================

        for token, metadata in agent.stream(

            {
                "messages": conversation_history
            },

            config={
                "recursion_limit": 10
            },

            stream_mode="messages"

        ):


            # ==================================================
            # 1. MODEL TOOL CALL
            # ==================================================

            if metadata.get(
                "langgraph_node"
            ) == "model":

                tool_calls = getattr(
                    token,
                    "tool_calls",
                    []
                )

                if tool_calls:

                    for tool_call in tool_calls:

                        # Execution order
                        execution_order += 1


                        # Tool name
                        tool_name = tool_call.get(
                            "name",
                            "Unknown"
                        )


                        # Tool arguments
                        arguments = tool_call.get(
                            "args",
                            {}
                        )


                        # Store start time
                        tool_start_times[tool_name] = {

                            "start": time.time(),

                            "order": execution_order,

                            "arguments": arguments

                        }


            # ==================================================
            # 2. TOOL RESULT
            # ==================================================

            if metadata.get(
                "langgraph_node"
            ) == "tools":

                # Get tool name
                tool_name = getattr(
                    token,
                    "name",
                    "Unknown"
                )


                # Get tool result
                tool_result = token.content


                # Find tool start information
                tool_info = tool_start_times.get(
                    tool_name
                )


                if tool_info:

                    # Calculate duration
                    duration = (
                        time.time()
                        - tool_info["start"]
                    )


                    # Create execution log
                    log_entry = {

                        "order":
                            tool_info["order"],

                        "tool":
                            tool_name,

                        "arguments":
                            tool_info["arguments"],

                        "result":
                            tool_result,

                        "duration":
                            round(
                                duration,2
                            )
                    }


                    # Store execution log
                    execution_logs.append(
                        log_entry
                    )


            # ==================================================
            # 3. MODEL RESPONSE
            # ==================================================

            if (

                metadata.get(
                    "langgraph_node"
                ) == "model"

                and token.content

            ):

                full_response += token.content

                yield token.content


        # ==================================================
        # 4. EXECUTION LOG SUMMARY
        # ==================================================

        print(
            "\n========== EXECUTION LOG SUMMARY =========="
        )


        if not execution_logs:

            print(
                "No tools were executed."
            )

        else:

            for log in execution_logs:
                result=log["result"]
                #keep long tool results out of execution
                if len(result)>100:
                    result="Tool executed successfully"

                print(
                    f"\n[{log['order']}] "
                    f"{log['tool']}"
                )

                print(
                    f"Arguments : "
                    f"{log['arguments']}"
                )
                
                print(
                    f"Result    : "
                    f"{result}"
                )

                print(
                    f"Duration  : "
                    f"{log['duration']} seconds"
                )


        print(
            "\n============================================"
        )


        # ==================================================
        # 5. Save AI Message
        # ==================================================

        save_message(

            db,

            conversation_id,

            "AI",

            full_response

        )


    # ==================================================
    # Streaming Response
    # ==================================================

    return StreamingResponse(

        generate(),

        media_type="text/plain",

        headers={
            "X-Conversation-Id":
                str(conversation_id)
        }

    )