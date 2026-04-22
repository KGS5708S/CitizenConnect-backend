from models.notification import Notification
from models.user import User
from database import db
from services.email_service import send_email


def create_notification(user_id: int, title: str, message: str):
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message
    )
    db.session.add(notification)
    db.session.commit()

    # Fetch user email
    user = User.query.get(user_id)
    if user and user.email:
        send_email(
            to_email=user.email,
            subject=title,
            body=message
        )
