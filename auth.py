from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask import redirect, url_for, render_template
from models import User, db
from functools import wraps

login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def init_app(app):
    # Check if the db instance is already initialized
    if not hasattr(app, 'extensions'):
        db.init_app(app)

    login_manager.init_app(app)

def login(username, password):
    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password, password):
        login_user(user)
        return True

    return False

def signup(username, password):
    new_user = User(username=username, password=generate_password_hash(password, method='sha256'))

    db.session.add(new_user)
    db.session.commit()

def logout():
    logout_user()

def login_required_decorator(func):
    """
    Custom decorator to enforce login requirement.
    Redirects to login page if user is not authenticated.
    """
    @wraps(func)  # Add this line to preserve the original function's metadata
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        return func(*args, **kwargs)

    return wrapper

def get_username():
    return current_user.username if current_user.is_authenticated else None
