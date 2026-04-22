from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from database import db
from flask import send_from_directory
from routes.auth_routes import auth_bp
from routes.complaint_routes import complaint_bp
from routes.ai_routes import ai_bp
from routes.admin_routes import admin_bp
from routes.notification_routes import notification_bp
import os
from flask import Flask
from flask_cors import CORS
from blockchain_utils import generate_hash, store_on_blockchain
from routes.ai_routes import ai_bp
from flask import send_from_directory
app = Flask(__name__)

CORS(app, resources={
    r"/uploads/*": {"origins": "*"},
    r"/api/*": {"origins": "*"}
}, supports_credentials=True)

app.config.from_object(Config)
db.init_app(app)
JWTManager(app)

app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(complaint_bp, url_prefix="/api/complaints")
app.register_blueprint(ai_bp, url_prefix="/api/ai")
app.register_blueprint(admin_bp, url_prefix="/api/admin")
app.register_blueprint(notification_bp, url_prefix="/api/notifications")

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return {"message": "CitizenConnect Backend Running"}

UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/uploads/<path:filename>")
def uploaded_files(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
