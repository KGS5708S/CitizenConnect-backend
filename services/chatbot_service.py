from models.conversation import Conversation
from database import db
def detect_intent(question: str):
    q = question.lower()

    intents = {
        "complaint_status": ["status", "track", "progress"],
        "complaint_process": ["how to complain", "register", "submit"],
        "department_info": ["department", "who handles", "responsible"],
        "resolution_time": ["how long", "time", "days"],
        "priority_info": ["priority", "urgent", "emergency"],
        "greeting": ["hello", "hi", "help"],
        "gratitude": ["thank", "thanks"]
    }

    for intent, keywords in intents.items():
        if any(word in q for word in keywords):
            return intent

    return "fallback"


def generate_llm_style_response(intent: str, question: str):
    responses = {
        "greeting": (
            "Hello! I’m your CitizenConnect assistant. "
            "I can help you submit complaints, track their status, "
            "and answer questions about government services."
        ),

        "complaint_process": (
            "To register a complaint, go to the complaint section and describe your issue clearly. "
            "Our system will automatically classify it and forward it to the responsible department."
        ),

        "complaint_status": (
            "You can track the status of your complaint from the 'My Complaints' section. "
            "Each update is recorded transparently and you will also receive email notifications."
        ),

        "department_info": (
            "Complaints are handled by specialized departments such as Roads & Infrastructure, "
            "Water Supply, Electricity Board, Sanitation, Police, and Health Services. "
            "The system automatically routes your complaint to the correct authority."
        ),

        "resolution_time": (
            "Resolution time depends on the complaint priority. "
            "High-priority issues are typically addressed within 24–72 hours, "
            "while normal complaints may take 3–7 working days."
        ),

        "priority_info": (
            "Complaint priority is automatically assigned based on urgency and impact. "
            "Critical issues like public safety and medical emergencies are prioritized immediately."
        ),

        "gratitude": (
            "You’re welcome! If you have any other questions or need assistance, "
            "feel free to ask."
        ),

        "fallback": (
            "I’m here to help with complaint registration, tracking, and general civic queries. "
            "Please describe your concern or question clearly so I can assist you better."
        )
    }

    return responses.get(intent, responses["fallback"])

def get_conversation_context(user_id, limit=5):
    history = (
        Conversation.query
        .filter_by(user_id=user_id)
        .order_by(Conversation.timestamp.desc())
        .limit(limit)
        .all()
    )
    # reverse to maintain order
    history = list(reversed(history))
    context = ""
    for msg in history:
        role = "User" if msg.is_user else "Bot"
        context += f"{role}: {msg.message}\n"
    return context

def chatbot_response(user_id: int, question: str):
    context = get_conversation_context(user_id)
    combined_input = context + f"User: {question}"
    intent = detect_intent(combined_input)
    response = generate_llm_style_response(intent, combined_input)
    # Save conversation
    db.session.add(Conversation(
        user_id=user_id,
        message=question,
        is_user=True
    ))
    db.session.add(Conversation(
        user_id=user_id,
        message=response,
        is_user=False
    ))
    db.session.commit()
    return response