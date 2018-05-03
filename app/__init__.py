# flake8: noqa
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

from .models import AnonymousUser

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
fh = logging.FileHandler('log.log')
formatter = logging.Formatter('[%(asctime)s] %(name)s - %(levelname)s: %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

app = Flask(__name__)

bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.anonymous_user = AnonymousUser

app.config.from_object('config')

from app import views
