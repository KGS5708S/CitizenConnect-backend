from database import db
from datetime import datetime

class ComplaintStatusHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, nullable=False)
    old_status = db.Column(db.String(50))
    new_status = db.Column(db.String(50))
    updated_by = db.Column(db.Integer, nullable=False)  # authority/admin user id
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
