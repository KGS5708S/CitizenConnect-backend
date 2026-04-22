from database import db
from datetime import datetime

class Complaint(db.Model):
    __tablename__ = "complaint"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)

    category = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200), nullable=False)

    status = db.Column(db.String(50), default="Submitted")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    blockchain_hash = db.Column(db.String(256))

    department = db.Column(db.String(100))
    priority = db.Column(db.String(20))

    image = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(200), nullable=True)
    
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    evidence_url = db.Column(db.String(255), nullable=True)
    resolved_remarks = db.Column(db.Text, nullable=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
