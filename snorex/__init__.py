# -*- coding: utf-8 -*-
"""
Created on Wed Dec 29 15:01:36 2021

@author: yuanq
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

login_manager = LoginManager()
app = Flask(__name__)

#basedir = os.path.abspath(os.path.dirname(__file__))
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://{uid}:{pw}@{host}:{port}/{db_name}'.format(
#                                             uid=os.getenv('DATABASE_UID'),
#                                             pw=os.getenv('DATABASE_PW'),
#                                             host=os.getenv('DATABASE_HOST'),
#                                             port=os.getenv('DATABASE_PORT'),
#                                             db_name=os.getenv('DATABASE_NAME'))
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL").replace("postgres://", "postgresql://", 1)
#'postgres://xlqnvydgbgpbao:1663b44a15c8d39a4b7b9ba3de4e15fe8b11134f7016ce3ec99c020e0a3b3231@ec2-34-192-210-139.compute-1.amazonaws.com:5432/d6osmmqphob640'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = bool(os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS'))

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

db = SQLAlchemy(app)
Migrate(app, db)
login_manager.init_app(app)
login_manager.login_view = 'login'

from snorex.analytics.views import analytics_blueprints
from snorex.views import main_blueprints

app.register_blueprint(analytics_blueprints, url_prefix='/analytics')
app.register_blueprint(main_blueprints, url_prefix='/')
