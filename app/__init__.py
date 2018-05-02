# flake8: noqa
from flask import Flask
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from .models import AnonymousUser

app = Flask(__name__)

bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.anonymous_user = AnonymousUser

app.config.from_object('config')

from app import views
