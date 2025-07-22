from flask import Flask
from flask_session import Session
import os

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev')
    app.config['SESSION_TYPE'] = 'filesystem'
    Session(app)
    
    from .routes import main
    app.register_blueprint(main)
    return app 