from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = 'echo-lock-super-secret-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///echolock.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('app', 'static', 'uploads')

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Use the db from __init__.py
from app import db
db.init_app(app)

# Flask-Login Setup
login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))

# Register blueprint
from app.routes import main_bp
app.register_blueprint(main_bp)

if __name__ == '__main__':
    print("🚀 EchoLock Server is Starting...")
    print("Open: http://127.0.0.1:5000")
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)