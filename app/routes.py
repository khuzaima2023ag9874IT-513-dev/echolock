from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import db
from .models import User, EncryptedFile, ActivityLog
from datetime import datetime

main_bp = Blueprint('main', __name__)

# ====================== AUTH ROUTES ======================

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Prevent logged-in users from accessing login page
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # 🔒 Validation
        if not username or not password:
            flash('Please fill all fields', 'warning')
            return redirect(url_for('main.login'))

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('main.home'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')


@main_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    # Prevent logged-in users from accessing signup page
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # 🔒 Validation
        if not username or not email or not password:
            flash('All fields are required!', 'warning')
            return redirect(url_for('main.signup'))

        if len(password) < 6:
            flash('Password must be at least 6 characters', 'warning')
            return redirect(url_for('main.signup'))

        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')

        elif User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')

        else:
            new_user = User(username=username, email=email)
            new_user.set_password(password)

            db.session.add(new_user)
            db.session.commit()

            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('main.login'))

    return render_template('signup.html')


@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('main.login'))


# ====================== MAIN ROUTES ======================

@main_bp.route('/')
@login_required
def home():
    return render_template('index.html', user=current_user)


@main_bp.route('/decrypt')
@login_required
def decrypt_page():
    return render_template('decrypt.html')
@main_bp.route('/clear_logs', methods=['POST'])
@login_required
def clear_logs():
    try:
        ActivityLog.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


# ====================== ENCRYPTION + LOGGING ======================

@main_bp.route('/save_file', methods=['POST'])
@login_required
def save_file():
    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({"status": "error", "message": "No data received"}), 400

        # 🔒 Extra safety validation
        required_fields = ['filename', 'target_lat', 'target_long', 'radius', 'salt', 'iv']
        for field in required_fields:
            if field not in data:
                return jsonify({"status": "error", "message": f"{field} missing"}), 400

        new_file = EncryptedFile(
            user_id=current_user.id,
            filename=data['filename'],
            encrypted_path=data.get('encrypted_path', data['filename'] + '.echolock'),
            target_lat=float(data['target_lat']),
            target_long=float(data['target_long']),
            radius=int(data['radius']),
            salt=data['salt'],
            iv=data['iv']
        )

        db.session.add(new_file)
        db.session.commit()

        # 🔐 Log Encryption
        log = ActivityLog(
            user_id=current_user.id,
            file_id=new_file.id,
            action='encrypt',
            status='success',
            location_info=f"{float(data['target_lat']):.4f}, {float(data['target_long']):.4f}",
            details=f"Encrypted file: {data['filename']}",
            timestamp=datetime.utcnow()
        )

        db.session.add(log)
        db.session.commit()

        return jsonify({"status": "success"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ====================== DECRYPT LOGGING ======================

@main_bp.route('/log_decrypt', methods=['POST'])
@login_required
def log_decrypt():
    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({"status": "error", "message": "No data"}), 400

        log = ActivityLog(
            user_id=current_user.id,
            file_id=data.get('file_id'),
            action='decrypt',
            status=data.get('status', 'failed'),
            location_info=data.get('location_info'),
            details=data.get('details'),
            timestamp=datetime.utcnow()
        )

        db.session.add(log)
        db.session.commit()

        return jsonify({"status": "success"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ====================== ACTIVITY LOGS PAGE ======================

@main_bp.route('/logs')
@login_required
def activity_logs():
    logs = ActivityLog.query.filter_by(user_id=current_user.id) \
        .order_by(ActivityLog.timestamp.desc()) \
        .all()

    return render_template('logs.html', logs=logs)