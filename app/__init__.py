from pathlib import Path

from flask import Flask, send_from_directory


def create_app():
    app = Flask(__name__, static_folder='static', static_url_path='')
    app.config['SECRET_KEY'] = 'change-me'

    from .views import api_bp

    app.register_blueprint(api_bp, url_prefix='/api')

    static_folder = Path(app.static_folder)

    @app.route('/')
    def index():
        return send_from_directory(str(static_folder), 'index.html')

    return app
