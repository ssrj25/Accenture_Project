# app/__init__.py
from flask import Flask
from .routes import bp

def create_app():
    app = Flask(__name__)
    app.secret_key = 'your_secret_key_here'  # Change this to a secure secret key

    app.register_blueprint(bp)

    return app
