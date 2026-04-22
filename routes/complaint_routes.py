from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from database import db
from models.complaint import Complaint
from models.complaint_history import ComplaintStatusHistory
from services.notification_service import create_notification
from services.ai_service import classify_complaint
import hashlib
import os
from models.user import User
import base64
from werkzeug.utils import secure_filename
from models.evidence import Evidence
from flask import current_app
from datetime import datetime

complaint_bp = Blueprint("complaint", __name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def generate_hash(data: str):
    return hashlib.sha256(data.encode()).hexdigest()

# --------------------------------------------------
# CREATE COMPLAINT (CITIZEN ONLY)
# --------------------------------------------------
@complaint_bp.route("/create", methods=["POST"])
@jwt_required()
def create_complaint():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    description = data.get("description")
    location = data.get("location")
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    image_base64 = data.get("image")

    if not description or not location:
        return jsonify({"error": "Missing required fields"}), 400

    # AI classification
    classification = classify_complaint(description)

    category = classification["category"]
    department = classification["department"]
    priority = classification["priority"]
    hash_data = f"{description}{location}{user_id}{datetime.utcnow()}"
    blockchain_hash = generate_hash(hash_data)
    complaint = Complaint(
        user_id=user_id,
        category=category,
        description=description,
        location=location,
        department=department,
        priority=priority,
        latitude=latitude,
        longitude=longitude,
        status="Submitted",
        blockchain_hash=blockchain_hash
    )

    db.session.add(complaint)
    db.session.commit()

    # ================= IMAGE SAVE =================
    if image_base64:
        image_path = os.path.join(UPLOAD_FOLDER, f"{complaint.id}.jpg")
        with open(image_path, "wb") as f:
            f.write(base64.b64decode(image_base64))

        complaint.image_url = f"/uploads/{complaint.id}.jpg"
        db.session.commit()
    # ==============================================

    return jsonify({
        "message": "Complaint created successfully",
        "complaint_id": complaint.id
    }), 201

# --------------------------------------------------
# VIEW MY COMPLAINTS (CITIZEN)
# --------------------------------------------------
@complaint_bp.route("/my", methods=["GET"])
@jwt_required()
def my_complaints():
    user_id = int(get_jwt_identity())

    complaints = Complaint.query.filter_by(user_id=user_id).all()

    return jsonify([
        {
            "id": c.id,
            "category": c.category,
            "description": c.description,
            "location": c.location,
            "status": c.status,
            "timestamp": c.timestamp,
            "hash": c.blockchain_hash
        }
        for c in complaints
    ]), 200


# --------------------------------------------------
# VIEW ALL COMPLAINTS (ADMIN / AUTHORITY)
# --------------------------------------------------
@complaint_bp.route("/all", methods=["GET"])
@jwt_required()
def all_complaints():
    role = get_jwt().get("role")

    if role not in ["authority", "admin"]:
        return jsonify({"error": "Access denied"}), 403

    complaints = Complaint.query.all()

    return jsonify([
        {
            "id": c.id,
            "user_id": c.user_id,
            "category": c.category,
            "status": c.status,
            "timestamp": c.timestamp
        }
        for c in complaints
    ]), 200


# --------------------------------------------------
# UPDATE COMPLAINT STATUS (ADMIN / AUTHORITY)
# --------------------------------------------------
@complaint_bp.route("/update-status", methods=["PUT"])
@jwt_required()
def update_status():
    role = get_jwt().get("role")

    if role not in ["authority", "admin"]:
        return jsonify({"error": "Access denied"}), 403

    data = request.get_json()
    complaint_id = data.get("complaint_id")
    new_status = data.get("status")

    if not complaint_id or not new_status:
        return jsonify({"error": "Missing fields"}), 400

    complaint = Complaint.query.get(int(complaint_id))
    if not complaint:
        return jsonify({"error": "Complaint not found"}), 404

    old_status = complaint.status
    complaint.status = new_status

    history = ComplaintStatusHistory(
        complaint_id=complaint.id,
        old_status=old_status,
        new_status=new_status,
        updated_by=int(get_jwt_identity())
    )

    db.session.add(history)
    db.session.commit()

    db.session.refresh(complaint)

    create_notification(
        user_id=complaint.user_id,
        title="Complaint Status Updated",
        message=f"Status changed from '{old_status}' to '{new_status}'."
    )

    response = make_response(jsonify({
        "success": True,
        "old_status": old_status,
        "new_status": new_status,
        "complaint": {
            "id": complaint.id,
            "category": complaint.category,
            "description": complaint.description,
            "location": complaint.location,
            "status": complaint.status,
            "priority": complaint.priority,
            "department": complaint.department,
            "timestamp": complaint.timestamp.isoformat()
        }
    }), 200)
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


# --------------------------------------------------
# COMPLAINT HISTORY (ADMIN / AUTHORITY)
# --------------------------------------------------
@complaint_bp.route("/history/<int:complaint_id>", methods=["GET"])
@jwt_required()
def complaint_history(complaint_id):
    role = get_jwt().get("role")

    if role not in ["authority", "admin"]:
        return jsonify({"error": "Access denied"}), 403

    history = ComplaintStatusHistory.query.filter_by(
        complaint_id=complaint_id
    ).order_by(ComplaintStatusHistory.timestamp).all()

    return jsonify([
        {
            "old_status": h.old_status,
            "new_status": h.new_status,
            "updated_by": h.updated_by,
            "timestamp": h.timestamp
        }
        for h in history
    ]), 200

@complaint_bp.route("/<int:complaint_id>", methods=["GET"])
@jwt_required()
def get_complaint(complaint_id):
    complaint = Complaint.query.get(complaint_id)

    if not complaint:
        return jsonify({"error": "Complaint not found"}), 404

    history = ComplaintStatusHistory.query.filter_by(
        complaint_id=complaint_id
    ).order_by(ComplaintStatusHistory.timestamp).all()

    timeline = [
        h.new_status for h in history
    ]

    return jsonify({
        "id": complaint.id,
        "status": complaint.status,
        "category": complaint.category,
        "location": complaint.location,
        "image_url": complaint.image_url,
        "description": complaint.description,
        "timeline": timeline
    }), 200

@complaint_bp.route("/department", methods=["GET"])
@jwt_required()
def get_department_complaints():
    claims = get_jwt()
    role = claims.get("role")

    if role != "authority":
        return jsonify({"error": "Access denied"}), 403

    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))

    complaints = Complaint.query.filter_by(
        department=user.department
    ).order_by(Complaint.timestamp.desc()).all()

    response = make_response(jsonify([
        {
            "id": c.id,
            "category": c.category,
            "description": c.description,
            "location": c.location,
            "status": c.status,
            "priority": c.priority,
            "department": c.department,
            "image": c.image,
            "timestamp": c.timestamp.isoformat()
        }
        for c in complaints
    ]), 200)
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@complaint_bp.route("/heatmap", methods=["GET"])
@jwt_required()
def heatmap_data():
    complaints = Complaint.query.filter(
        Complaint.latitude.isnot(None),
        Complaint.longitude.isnot(None)
    ).all()

    data = []
    for c in complaints:
        weight = 1
        if c.priority == "High":
            weight = 3
        elif c.priority == "Critical":
            weight = 5

        data.append({
            "lat": c.latitude,
            "lng": c.longitude,
            "weight": weight,
            "department": c.department,
            "priority": c.priority,
        })

    return jsonify([
    {
        "lat": float(c.latitude),
        "lng": float(c.longitude),
        "weight": 5 if c.priority == "Critical" else 3
    }
    for c in complaints
])


@complaint_bp.route("/heatmap/filter", methods=["GET"])
@jwt_required()
def filtered_heatmap():
    department = request.args.get("department")
    priority = request.args.get("priority")

    query = Complaint.query

    if department:
        query = query.filter_by(department=department)
    if priority:
        query = query.filter_by(priority=priority)

    complaints = query.all()

    return jsonify([
        {
            "lat": c.latitude,
            "lng": c.longitude,
            "weight": 5 if c.priority == "Critical" else 3,
        }
        for c in complaints
    ]), 200
    

@complaint_bp.route("/resolve-with-evidence", methods=["PUT"])
@jwt_required()
def resolve_with_evidence():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if user.role != "authority":
        return jsonify({"message": "Unauthorized"}), 403

    data = request.get_json()

    complaint_id = data.get("complaint_id")
    image_base64 = data.get("image")
    remarks = data.get("remarks")

    complaint = Complaint.query.get_or_404(complaint_id)

    if image_base64:
        filename = f"evidence_{complaint.id}.jpg"
        filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)

        with open(filepath, "wb") as f:
            f.write(base64.b64decode(image_base64))

        # ✅ STORE FULL URL (IMPORTANT)
        complaint.evidence_url = f"http://127.0.0.1:5000/uploads/{filename}"

    complaint.status = "Resolved"
    complaint.resolved_remarks = remarks
    complaint.resolved_at = datetime.utcnow()

    db.session.commit()

    return jsonify({"success": True})


# ================= MULTIPART UPLOAD =================

@complaint_bp.route("/upload-evidence/<int:complaint_id>", methods=["POST"])
@jwt_required()
def upload_evidence(complaint_id):
    claims = get_jwt()
    role = claims.get("role")

    if role not in ["authority", "admin"]:
        return jsonify({"error": "Access denied"}), 403

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    filename = secure_filename(file.filename)

    # ✅ DEFINE FILEPATH (FIXED)
    filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)

    # SAVE FILE
    file.save(filepath)

    # ✅ CREATE ACCESSIBLE URL
    file_url = f"http://127.0.0.1:5000/uploads/{filename}"

    evidence = Evidence(
        complaint_id=complaint_id,
        file_path=file_url,
        uploaded_by=int(get_jwt_identity())
    )

    db.session.add(evidence)
    db.session.commit()

    return jsonify({
        "message": "Evidence uploaded successfully",
        "file_path": file_url
    }), 201


# ================= FETCH EVIDENCE =================
@complaint_bp.route("/evidence/<int:complaint_id>", methods=["GET"])
@jwt_required()
def get_evidence(complaint_id):

    complaint = Complaint.query.get_or_404(complaint_id)

    evidence_list = Evidence.query.filter_by(
        complaint_id=complaint_id
    ).all()

    result = []

    if complaint.image_url:
        result.append({
            "file_path": f"http://127.0.0.1:5000{complaint.image_url}",
            "uploaded_by": complaint.user_id,
            "timestamp": complaint.timestamp,
            "type": "citizen"
        })

    if complaint.evidence_url:
        result.append({
            "file_path": complaint.evidence_url,
            "uploaded_by": complaint.user_id,
            "timestamp": complaint.resolved_at,
            "type": "authority_resolve"
        })

    for e in evidence_list:
        result.append({
            "file_path": e.file_path,
            "uploaded_by": e.uploaded_by,
            "timestamp": e.timestamp,
            "type": "authority_upload"
        })

    return jsonify(result), 200

@complaint_bp.route("/assign", methods=["PUT"])
@jwt_required()
def assign_complaint():
    claims = get_jwt()
    
    if claims.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()

    complaint_id = data.get("complaint_id")
    department = data.get("department")

    complaint = Complaint.query.get_or_404(complaint_id)

    complaint.department = department

    db.session.commit()

    return jsonify({
        "message": "Complaint assigned successfully",
        "department": department
    }), 200