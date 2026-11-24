import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from routes.dashboard import bp as dashboard_bp
from routes.patrol import bp as patrol_bp
from routes.prediction import bp as prediction_bp
from routes.recommendation import bp as recommendation_bp

load_dotenv()


def create_app():
    app = Flask(__name__)
    CORS(app, resources={r'/api/*': {'origins': '*'}})
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(patrol_bp)
    app.register_blueprint(prediction_bp)
    app.register_blueprint(recommendation_bp)

    @app.get('/api/health')
    def health():
        return jsonify({'status': 'ok', 'service': 'SIPP Karhutla API'})

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({'error': 'Endpoint tidak ditemukan.'}), 404

    @app.errorhandler(405)
    def method_not_allowed(_error):
        return jsonify({'error': 'Method tidak diizinkan.'}), 405

    return app


app = create_app()

if __name__ == '__main__':
    app.run(host=os.getenv('FLASK_HOST', '127.0.0.1'), port=int(os.getenv('FLASK_PORT', '5000')), debug=os.getenv('FLASK_ENV') == 'development')
