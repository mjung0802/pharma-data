from flask import Blueprint

drugs_bp = Blueprint("drugs", __name__)


@drugs_bp.route("/drugs")
def drugs():
    return "Drugs dashboard — coming soon", 200
