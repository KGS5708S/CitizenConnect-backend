from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from database import db
from models.complaint import Complaint
from sqlalchemy import func
from flask import Blueprint, jsonify,request
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from models.complaint import Complaint
from models.user import User



admin_bp = Blueprint("admin", __name__)


def is_admin_or_authority():
    claims = get_jwt()
    return claims.get("role") in ["admin", "authority"]


@admin_bp.route("/overview", methods=["GET"])
@jwt_required()
def overview():
    if not is_admin_or_authority():
        return jsonify({"error": "Access denied"}), 403

    total = Complaint.query.count()
    resolved = Complaint.query.filter_by(status="Resolved").count()
    pending = Complaint.query.filter_by(status="Submitted").count()

    return jsonify({
        "total_complaints": total,
        "resolved": resolved,
        "pending": pending
    }), 200


@admin_bp.route("/by-status", methods=["GET"])
@jwt_required()
def complaints_by_status():
    if not is_admin_or_authority():
        return jsonify({"error": "Access denied"}), 403

    results = (
        db.session.query(Complaint.status, func.count(Complaint.id))
        .group_by(Complaint.status)
        .all()
    )

    return jsonify([
        {"status": status, "count": count}
        for status, count in results
    ]), 200


@admin_bp.route("/by-category", methods=["GET"])
@jwt_required()
def complaints_by_category():
    if not is_admin_or_authority():
        return jsonify({"error": "Access denied"}), 403

    results = (
        db.session.query(Complaint.category, func.count(Complaint.id))
        .group_by(Complaint.category)
        .all()
    )

    return jsonify([
        {"category": category, "count": count}
        for category, count in results
    ]), 200


@admin_bp.route("/by-date", methods=["GET"])
@jwt_required()
def complaints_by_date():
    if not is_admin_or_authority():
        return jsonify({"error": "Access denied"}), 403

    results = (
        db.session.query(
            func.date(Complaint.timestamp),
            func.count(Complaint.id)
        )
        .group_by(func.date(Complaint.timestamp))
        .order_by(func.date(Complaint.timestamp))
        .all()
    )

    return jsonify([
        {"date": str(date), "count": count}
        for date, count in results
    ]), 200


@admin_bp.route("/by-location", methods=["GET"])
@jwt_required()
def complaints_by_location():
    if not is_admin_or_authority():
        return jsonify({"error": "Access denied"}), 403

    results = (
        db.session.query(Complaint.location, func.count(Complaint.id))
        .group_by(Complaint.location)
        .all()
    )

    return jsonify([
        {"location": location, "count": count}
        for location, count in results
    ]), 200

@admin_bp.route("/dashboard-metrics", methods=["GET"])
@jwt_required()
def dashboard_metrics():
    claims = get_jwt()
    if claims.get("role") not in ["authority", "admin"]:
        return jsonify({"error": "Access denied"}), 403

    total = Complaint.query.count()
    pending = Complaint.query.filter_by(status="Submitted").count()
    resolved = Complaint.query.filter_by(status="Resolved").count()

    return jsonify({
        "total": total,
        "pending": pending,
        "resolved": resolved,
        "avg_resolution": "2.4 days"  # placeholder (can compute later)
    }), 200

@admin_bp.route("/my-department-complaints", methods=["GET"])
@jwt_required()
def my_department_complaints():
    claims = get_jwt()
    role = claims.get("role")

    if role != "authority":
        return jsonify({"error": "Access denied"}), 403

    user_id = int(get_jwt_identity())
    authority = User.query.get(user_id)

    # authority.department MUST exist in DB
    department = authority.department

    complaints = Complaint.query.filter_by(
        department=department
    ).order_by(Complaint.timestamp.desc()).all()

    return jsonify([
        {
            "id": c.id,
            "category": c.category,
            "status": c.status,
            "priority": c.priority,
            "department": c.department,
            "timestamp": c.timestamp.isoformat(),
        }
        for c in complaints
    ]), 200
    
@admin_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def admin_dashboard():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Access denied"}), 403

    total = Complaint.query.count()
    pending = Complaint.query.filter(Complaint.status != "Resolved").count()
    resolved = Complaint.query.filter(Complaint.status == "Resolved").count()

    return jsonify({
        "total": total,
        "pending": pending,
        "resolved": resolved
    }), 200


@admin_bp.route("/complaints", methods=["GET"])
@jwt_required()
def all_complaints():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Access denied"}), 403

    complaints = Complaint.query.order_by(
        Complaint.timestamp.desc()
    ).all()

    return jsonify([
        {
            "id": c.id,
            "category": c.category,
            "department": c.department,
            "priority": c.priority,
            "status": c.status,
            "timestamp": c.timestamp.isoformat(),
            "description": c.description, 
            "location": c.location  
        }
        for c in complaints
    ]), 200
    
@admin_bp.route("/analytics", methods=["GET"])
@jwt_required()
def admin_analytics():
    # TOTAL COUNTS
    total = Complaint.query.count()
    resolved = Complaint.query.filter_by(status="Resolved").count()
    pending = Complaint.query.filter(Complaint.status != "Resolved").count()

    # DEPARTMENT WISE COUNT
    department_stats = (
        Complaint.query
        .with_entities(Complaint.department, func.count(Complaint.id))
        .group_by(Complaint.department)
        .all()
    )

    department_data = [
        {"department": d, "count": c}
        for d, c in department_stats
    ]

    # PRIORITY WISE COUNT
    priority_stats = (
        Complaint.query
        .with_entities(Complaint.priority, func.count(Complaint.id))
        .group_by(Complaint.priority)
        .all()
    )

    priority_data = [
        {"priority": p, "count": c}
        for p, c in priority_stats
    ]

    return jsonify({
        "success": True,
        "metrics": {
            "total": total,
            "pending": pending,
            "resolved": resolved,
        },
        "by_department": department_data,
        "by_priority": priority_data,
    }), 200
@admin_bp.route("/analytics/timeline", methods=["GET"])
@jwt_required()
def complaints_timeline():
    days = int(request.args.get("days", 7))

    from datetime import datetime, timedelta
    start_date = datetime.utcnow() - timedelta(days=days)

    data = (
        db.session.query(
            func.date(Complaint.timestamp),
            func.count(Complaint.id)
        )
        .filter(Complaint.timestamp >= start_date)
        .group_by(func.date(Complaint.timestamp))
        .order_by(func.date(Complaint.timestamp))
        .all()
    )

    return jsonify([
        {
            "date": d[0].isoformat(),
            "count": d[1]
        }
        for d in data
    ])
