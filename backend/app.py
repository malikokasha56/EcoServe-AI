import os
from datetime import datetime, timedelta, timezone

from flask import Flask, jsonify, request, send_from_directory
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity
from sqlalchemy import event, text
from sqlalchemy.engine import Engine
from werkzeug.exceptions import HTTPException

from config import Config, FRONTEND_DIST
from extensions import db, jwt, bcrypt, cors


# SQLite: WAL mode lets the API keep reading while a retrain writes.
@event.listens_for(Engine, "connect")
def _sqlite_pragmas(dbapi_conn, _record):
    if dbapi_conn.__class__.__module__.startswith("sqlite3"):
        cur = dbapi_conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL")
        cur.execute("PRAGMA foreign_keys=ON")
        cur.close()


def create_app(config_class=Config):
    app = Flask(__name__, static_folder=None)
    app.config.from_object(config_class)

    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}}, expose_headers=["X-Refreshed-Token"])

    import models  # noqa: F401  ensures models are registered before create_all

    from routes.auth import auth_bp
    from routes.sales import sales_bp
    from routes.waste import waste_bp
    from routes.forecast import forecast_bp
    from routes.recommendations import recommendations_bp
    from routes.anomalies import anomalies_bp
    from routes.dashboard import dashboard_bp
    from routes.inventory import inventory_bp
    from routes.reports import reports_bp
    from routes.public import public_bp
    from routes.simulation import simulation_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(sales_bp, url_prefix="/api/sales")
    app.register_blueprint(waste_bp, url_prefix="/api/waste")
    app.register_blueprint(forecast_bp, url_prefix="/api/forecast")
    app.register_blueprint(recommendations_bp, url_prefix="/api/recommendations")
    app.register_blueprint(anomalies_bp, url_prefix="/api/anomalies")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")
    app.register_blueprint(inventory_bp, url_prefix="/api/inventory")
    app.register_blueprint(reports_bp, url_prefix="/api/reports")
    app.register_blueprint(public_bp, url_prefix="/api/public")
    app.register_blueprint(simulation_bp, url_prefix="/api/simulation")

    _register_auth_handlers()
    _register_error_handlers(app)

    @app.route("/api/health")
    def health():
        return jsonify(system_status())

    # Sliding session: a token close to expiry is replaced on any authenticated request.
    @app.after_request
    def refresh_expiring_token(response):
        try:
            exp = datetime.fromtimestamp(get_jwt()["exp"], timezone.utc)
            if exp - datetime.now(timezone.utc) < timedelta(minutes=15):
                response.headers["X-Refreshed-Token"] = create_access_token(identity=get_jwt_identity())
        except (RuntimeError, KeyError):
            pass
        return response

    @app.route("/api/<path:path>", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    def api_not_found(path):
        return jsonify(message="Endpoint not found"), 404

    # The built React app is served by Flask, so one process and one port run the whole system.
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def frontend(path):
        if path.startswith("api/"):
            return jsonify(message="Endpoint not found"), 404
        if path and os.path.isfile(os.path.join(FRONTEND_DIST, path)):
            return send_from_directory(FRONTEND_DIST, path)
        if os.path.isfile(os.path.join(FRONTEND_DIST, "index.html")):
            return send_from_directory(FRONTEND_DIST, "index.html")
        return ("Frontend not built. Run 'npm run build' in the project folder, "
                "or use 'npm run dev' during development."), 503

    with app.app_context():
        db.create_all()

    return app


def _register_auth_handlers():
    def unauthorized(message):
        return jsonify(message=message), 401

    jwt.expired_token_loader(lambda _h, _p: unauthorized("Session expired, please sign in again"))
    jwt.invalid_token_loader(lambda reason: unauthorized("Invalid session, please sign in again"))
    jwt.unauthorized_loader(lambda reason: unauthorized("Please sign in"))


def _register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def http_error(e):
        if request.path.startswith("/api/"):
            return jsonify(message=e.description), e.code
        return e

    from helpers import ValidationError

    @app.errorhandler(ValidationError)
    def validation_error(e):
        return jsonify(message=str(e)), 400

    @app.errorhandler(Exception)
    def server_error(e):
        app.logger.exception("Unhandled error")
        db.session.rollback()
        return jsonify(message="Internal server error"), 500


def system_status():
    from models import SalesRecord, User, ExperimentResult

    status = {"status": "ok", "checks": {}}
    try:
        db.session.execute(text("SELECT 1"))
        status["checks"]["database"] = {"ok": True, "engine": db.engine.dialect.name}
    except Exception as e:
        status["checks"]["database"] = {"ok": False, "error": str(e)}
        status["status"] = "error"
        return status

    sales = SalesRecord.query.count()
    users = User.query.count()
    results = ExperimentResult.query.count()
    status["checks"]["sales_data"] = {"ok": sales > 0, "records": sales}
    status["checks"]["demo_user"] = {"ok": users > 0, "users": users}
    status["checks"]["model_results"] = {"ok": results > 0, "results": results}
    status["checks"]["frontend"] = {"ok": os.path.isfile(os.path.join(FRONTEND_DIST, "index.html"))}
    if not all(c["ok"] for c in status["checks"].values()):
        status["status"] = "degraded"
    return status
