from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.notification import Notification

notification_bp = Blueprint("notification", __name__)

@notification_bp.route("/my", methods=["GET"])
@jwt_required()
def my_notifications():
    user_id = get_jwt_identity()

    notifications = Notification.query.filter_by(
        user_id=int(user_id)
    ).order_by(Notification.timestamp.desc()).all()

    return jsonify([
        {
            "id": n.id,
            "title": n.title,
            "message": n.message,
            "is_read": n.is_read,
            "timestamp": n.timestamp
        }
        for n in notifications
    ]), 200
