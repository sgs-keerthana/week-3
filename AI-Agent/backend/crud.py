from sqlalchemy.orm import Session

from db_models import Conversation, Message


# Create Conversation


def create_conversation(
    db: Session,
    title: str
):

    conversation = Conversation(
        title=title
    )

    db.add(conversation)

    db.commit()

    db.refresh(conversation)

    return conversation


# ==========================================
# Save Message
# ==========================================

def save_message(
    db: Session,
    conversation_id: int,
    sender: str,
    message: str
):

    chat = Message(

        conversation_id=conversation_id,

        sender=sender,

        message=message

    )

    db.add(chat)

    db.commit()

    db.refresh(chat)

    return chat


# ==========================================
# Get All Conversations
# ==========================================

def get_conversations(db: Session):

    return db.query(Conversation)\
             .order_by(
                 Conversation.created_at.desc()
             )\
             .all()


# ==========================================
# Get Messages
# ==========================================

def get_messages(
    db: Session,
    conversation_id: int
):

    return db.query(Message)\
             .filter(
                 Message.conversation_id == conversation_id
             )\
             .order_by(
                 Message.id
             )\
             .all()


# ==========================================
# Delete Conversation
# ==========================================

def delete_conversation(
    db: Session,
    conversation_id: int
):

    conversation = db.query(Conversation)\
                     .filter(
                         Conversation.id == conversation_id
                     )\
                     .first()

    if conversation:

        db.delete(conversation)

        db.commit()


# ==========================================
# Build Context for Ollama
# ==========================================

def get_conversation_context(
    db: Session,
    conversation_id: int
):

    messages = get_messages(
        db,
        conversation_id
    )

    context = []

    for msg in messages:

        if msg.sender.lower() == "user":

            role = "user"

        else:

            role = "assistant"

        context.append({

            "role": role,

            "content": msg.message

        })

    return context