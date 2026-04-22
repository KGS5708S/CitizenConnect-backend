from database import db
from datetime import datetime
class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_user = db.Column(db.Boolean)  # True = user, False = bot
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)