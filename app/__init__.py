from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
#from config import basedir
from config import config,basedir
import os

app = Flask(__name__)
app.config.from_object(config)

db = SQLAlchemy()
lm = LoginManager()

db.init_app(app)
lm.init_app(app)

lm.login_view = 'login'#视图允许用户登录

from . import views,models