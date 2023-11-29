
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from geopy.geocoders import Nominatim
from auth import init_app, login, signup, logout, login_required_decorator, get_username
from models import User, Asset,db
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash



app = Flask(__name__)
app.config.from_object(Config)
geolocator = Nominatim(user_agent="asset-management-app")  # Provide a user_agent for Geopy

# Set a secret key for the application
app.secret_key = 'Banana'  # Replace with a long, random string
db.init_app(app)
# Initialize the authentication
init_app(app)

# Context processor to make get_username available in all templates
@app.context_processor
def inject_user():
    return dict(get_username=get_username)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/assets')
def asset():
    assets = Asset.query.all()
    return render_template('assets.html', assets=assets, get_username=get_username)

@app.route('/track_asset', methods=['GET', 'POST'])
def track_asset():
    if request.method == 'POST':
        search_term = request.form['search_term']
        # Search for the asset by name or ID
        asset = Asset.query.filter((Asset.name == search_term) | (Asset.id == search_term)).first()
        if asset:
            return render_template('track_asset.html', asset=asset)
        else:
            error_message = "Asset not found."
            return render_template('track_asset.html', error_message=error_message, get_username=get_username)

    return render_template('track_asset.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')  # Use get method to handle missing key
        password = request.form.get('password')

        # Check if both 'username' and 'password' are provided
        if username is not None and password is not None:
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password, password):
                session['user_id'] = user.id
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password')
                return redirect(url_for('login'))

        flash('Username and password are required')
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists')
            return redirect(url_for('signup'))
        else:
            new_user = User(username=username, email=email,
                            password=generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully')
            return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/logout')
@login_required_decorator
def logout_route():
    logout()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required_decorator
def dashboard():
    username = get_username()
    return render_template('dashboard.html', get_username=get_username)


@app.route('/create_asset', methods=['GET', 'POST'])
def create_asset():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        latitude = float(request.form['latitude'])
        longitude = float(request.form['longitude'])
        owner = request.form['owner']
        purchase_date = datetime.strptime(request.form['purchase_date'], '%Y-%m-%d').date()

        new_asset = Asset(
            name=name,
            description=description,
            latitude=latitude,
            longitude=longitude,
            owner=owner,
            purchase_date=purchase_date
        )

        db.session.add(new_asset)
        db.session.commit()

        return redirect(url_for('asset'))

    return render_template('create_asset.html',get_username=get_username)



if __name__ == '__main__':
    with app.app_context():
        init_app(app)
        db.create_all()
    app.run(debug=True, port=8080)
