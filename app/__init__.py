from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret-key' # clé secrète pour sécuriser les cookies et les sessions
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@db:5432/ma_base' # URI de la base de données
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['BASE_URL'] = 'http://127.0.0.1:5001' # URL de base de l'application
app.config['MAIL_SERVER'] = 'smtp.gmail.com' # serveur SMTP de Gmail
app.config['MAIL_PORT'] = 465 # port SMTP
app.config['MAIL_USE_TLS'] = False # utiliser TLS
app.config['MAIL_USE_SSL'] = True # utiliser SSL
app.config['MAIL_USERNAME'] = '' # votre adresse gmail
app.config['MAIL_PASSWORD'] = '' # votre mot de passe gmail
app.config['MAIL_DEFAULT_SENDER'] = '' # votre adresse gmail

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['REPORT_FOLDER'], exist_ok=True)
mail = Mail(app)

db = SQLAlchemy(app)

# Initialize Flask-Migrate for database migrations
migrate = Migrate(app, db)

# Initialize Flask-Login for user authentication
login_manager = LoginManager(app)
# Set the login view for Flask-Login
login_manager.login_view = 'auth.login'

    
# Importing models, auth, routes and backform from the app package
from app import models
from app import auth
from app import routes
from app import backform

