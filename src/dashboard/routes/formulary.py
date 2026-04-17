from flask import Blueprint

formulary_bp = Blueprint("formulary", __name__)


@formulary_bp.route("/formulary")
def formulary():
    return "Formulary dashboard — coming soon", 200
