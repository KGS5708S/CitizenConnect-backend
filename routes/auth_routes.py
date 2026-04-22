from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token
from database import db
from models.user import User

auth_bp = Blueprint("auth", __name__)
bcrypt = Bcrypt()

@auth_bp.route("/register", methods=["POST", "OPTIONS"])
def register():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    data = request.get_json()
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()
    phone = data.get("phone", "").strip()


    if not all([name, email, password]):
        return jsonify({"success": False, "message": "Missing fields"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"success": False, "message": "User already exists"}), 409

    hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")

    user = User(
        name=name,
        email=email,
        phone=phone,
        password=hashed_pw,
        role="citizen"
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"success": True, "message": "User registered successfully"}), 201


@auth_bp.route("/login", methods=["POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    data = request.get_json()

    email = data.get("email", "").strip()
    password = data.get("password", "").strip()

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"success": False, "message": "User not found"}), 401

    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({"success": False, "message": "Invalid credentials"}), 401

    token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role,
                           "department": user.department}
    )
    return jsonify({
        "success": True,
        "access_token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "department": user.department
        }
    }), 200
    
@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json()
    email = data.get("email")

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"message": "Email not found"}), 404

    return jsonify({
        "message": "Password reset link sent to email"
    }), 200
