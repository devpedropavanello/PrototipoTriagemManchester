import os
import secrets
from flask import Flask

def create_app():
    base_dir = os.path.abspath(os.path.dirname(__file__))

    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, "../templates"),
    )

    app.secret_key = os.getenv("SECRET_KEY") or secrets.token_hex(32)

    from .routes import main
    app.register_blueprint(main)

    return app