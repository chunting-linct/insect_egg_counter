from flask import Flask

def create_app():
    app = Flask(__name__)  # Flask auto-finds static/templates in the package

    # Import routes
    with app.app_context():
        from . import routes

    return app
