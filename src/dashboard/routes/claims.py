from flask import Blueprint

claims_bp = Blueprint("claims", __name__)


@claims_bp.route("/claims")
def claims():
    return "Claims dashboard — coming soon", 200
