from . import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# 👤 User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# 🔒 Encrypted File Model
class EncryptedFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    encrypted_path = db.Column(db.String(300), nullable=False)
    target_lat = db.Column(db.Float, nullable=False)
    target_long = db.Column(db.Float, nullable=False)
    radius = db.Column(db.Integer, nullable=False)
    salt = db.Column(db.String(100), nullable=False)
    iv = db.Column(db.String(100), nullable=False)
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)

# 📊 Activity Log Model (Very Important)
class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    file_id = db.Column(db.Integer, db.ForeignKey('encrypted_file.id'), nullable=True)
    action = db.Column(db.String(50), nullable=False)          # upload, decrypt_attempt, decrypt_success, decrypt_fail
    status = db.Column(db.String(20), nullable=False)          # success / failed
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(50), nullable=True)
    location_info = db.Column(db.String(100), nullable=True)   # e.g. "31.4365, 73.0751"
    details = db.Column(db.Text, nullable=True)