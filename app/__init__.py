import os
from pathlib import Path

from flask import Flask, send_from_directory


def create_app():
    app = Flask(__name__, static_folder='static', static_url_path='')
    app.config.update(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'change-me'),
        MYSQL_HOST=os.environ.get('MYSQL_HOST', 'localhost'),
        MYSQL_PORT=int(os.environ.get('MYSQL_PORT', '3306')),
        MYSQL_USER=os.environ.get('MYSQL_USER', 'root'),
        MYSQL_PASSWORD=os.environ.get('MYSQL_PASSWORD', ''),
        MYSQL_DB=os.environ.get('MYSQL_DB', 'hk_reception'),
    )

    from .views import api_bp

    app.register_blueprint(api_bp, url_prefix='/api')

    static_folder = Path(app.static_folder)

    @app.route('/')
    def index():
        return send_from_directory(str(static_folder), 'index.html')

    return app
