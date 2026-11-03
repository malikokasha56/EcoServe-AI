from datetime import datetime

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from extensions import db, bcrypt
from models import User, Restaurant
from helpers import json_object

auth_bp = Blueprint("auth", __name__)


def _ensure_default_restaurant():
    restaurant = Restaurant.query.first()
    if restaurant is None:
        restaurant = Restaurant(name="EcoServe Restaurant", restaurant_type="Casual Dining")
        db.session.add(restaurant)
        db.session.commit()
    return restaurant


@auth_bp.route("/register", methods=["POST"])
def register():
    data = json_object()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify(message="Email and password are required"), 400
    if len(password) < 8:
        return jsonify(message="Password must be at least 8 characters"), 400
    if User.query.filter_by(email=email).first():
        return jsonify(message="An account with this email already exists"), 409

    first = data.get("firstName") or ""
    last = data.get("lastName") or ""
    username = (data.get("username") or f"{first} {last}".strip() or email.split("@")[0])
    restaurant = _ensure_default_restaurant()

    user = User(
        username=username,
        email=email,
        password_hash=bcrypt.generate_password_hash(password).decode("utf-8"),
        role="Manager",
        restaurant_id=restaurant.id,
    )
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify(token=token, user=user.to_dict()), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = json_object()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    user = User.query.filter_by(email=email).first()
    if user is None or not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify(message="Invalid email or password"), 401

    user.last_login = datetime.utcnow()
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify(token=token, user=user.to_dict())


@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    return jsonify(message="Logged out")


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user = db.session.get(User, int(get_jwt_identity()))
    if user is None:
        return jsonify(message="User not found"), 404
    return jsonify(user=user.to_dict())
