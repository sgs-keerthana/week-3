from pydantic import BaseModel
from typing import Optional


# ======================================
# Chat Request
# ======================================

class ChatRequest(BaseModel):

    conversation_id: Optional[int] = None

    message: str





    


# ======================================
# Conversation Response
# ======================================

class ConversationResponse(BaseModel):

    id: int

    title: str

    class Config:

        from_attributes = True


# ======================================
# Message Response
# ======================================

class MessageResponse(BaseModel):

    id: int

    sender: str

    message: str

    class Config:

        from_attributes = True