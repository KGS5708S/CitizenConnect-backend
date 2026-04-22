from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required,get_jwt_identity
from services.ai_service import simple_ai_response, analyze_sentiment
from services.chatbot_service import chatbot_response

ai_bp = Blueprint("ai", __name__)

@ai_bp.route("/ask", methods=["POST"])
@jwt_required()
def civic_chatbot(question: str):
    q = question.lower()

    if "status" in q:
        return "You can check your complaint status in the 'My Complaints' section."

    if "department" in q:
        return "Road, water, electricity, sanitation, and public safety complaints are handled by respective municipal departments."

    if "time" in q or "how long" in q:
        return "Most complaints are resolved within 3-7 working days depending on priority."

    return "Please describe your issue clearly. I can help guide you or route your complaint."


@ai_bp.route("/sentiment", methods=["POST"])
@jwt_required()
def sentiment():
    data = request.get_json()
    text = data.get("text")

    if not text:
        return jsonify({"error": "Text is required"}), 400

    result = analyze_sentiment(text)

    return jsonify(result), 200

@ai_bp.route("/chat", methods=["POST"])
@jwt_required()
def chat():
    data = request.get_json()
    question = data.get("question")

    if not question:
        return jsonify({"error": "Question is required"}), 400

    user_id = get_jwt_identity()

    response = chatbot_response(int(user_id), question)

    return jsonify({
        "response": response
    }), 200