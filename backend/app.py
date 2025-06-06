from flask import Flask
from flask_cors import CORS
from .config import Config
from .routes.api import api_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    app.register_blueprint(api_bp)

    @app.route('/')
    def index():
        return "Welcome to the MiniTrip Backend! API is at /api"

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5001, debug=Config.FLASK_DEBUG)