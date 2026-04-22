from database import db
from datetime import datetime
class Evidence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, nullable=False)
    file_path = db.Column(db.String(300), nullable=False)
    uploaded_by = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)