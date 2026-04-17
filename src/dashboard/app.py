"""
Flask application factory for the Pharma Claims Analytics dashboard.

Run the dev server:
    flask --app "src.dashboard.app:create_app" run --port 5000
    # or from the project root:
    python -m src.dashboard.app
"""

from __future__ import annotations

import io
import os
from pathlib import Path

from flask import Flask, abort, render_template, send_file

# Resolve the directory that contains this file so Flask can find
# templates/ and static/ regardless of the working directory.
_HERE = Path(__file__).resolve().parent


def create_app() -> Flask:
    """
    Application factory.

    Creates and configures the Flask app, registers blueprints, and attaches
    the /download/<report_name> route.

    Returns
    -------
    Flask
        Configured Flask application instance.
    """
    app = Flask(
        __name__,
        template_folder=str(_HERE / "templates"),
        static_folder=str(_HERE / "static"),
    )

    # ------------------------------------------------------------------
    # Blueprints
    # ------------------------------------------------------------------
    from src.dashboard.routes.claims import claims_bp
    from src.dashboard.routes.drugs import drugs_bp
    from src.dashboard.routes.formulary import formulary_bp

    app.register_blueprint(claims_bp)
    app.register_blueprint(drugs_bp)
    app.register_blueprint(formulary_bp)

    # ------------------------------------------------------------------
    # Landing page
    # ------------------------------------------------------------------
    @app.route("/")
    def index():
        from src.ingestion import run_query

        try:
            total_claims = int(
                run_query("SELECT COUNT(*) AS n FROM claims")["n"].iloc[0]
            )
        except Exception:
            total_claims = "N/A"

        try:
            paid_claims = int(
                run_query(
                    "SELECT COUNT(*) AS n FROM claims WHERE claim_status = 'Paid'"
                )["n"].iloc[0]
            )
        except Exception:
            paid_claims = "N/A"

        try:
            raw = run_query(
                "SELECT ROUND(SUM(gross_cost), 2) AS total FROM claims"
                " WHERE claim_status = 'Paid'"
            )["total"].iloc[0]
            total_gross_cost = f"${float(raw):,.2f}"
        except Exception:
            total_gross_cost = "N/A"

        return render_template(
            "index.html",
            total_claims=total_claims,
            paid_claims=paid_claims,
            total_gross_cost=total_gross_cost,
        )

    # ------------------------------------------------------------------
    # Excel download route
    # ------------------------------------------------------------------
    _VALID_REPORTS = {"claims", "drugs", "formulary"}

    @app.route("/download/<report_name>")
    def download_report(report_name: str):
        if report_name not in _VALID_REPORTS:
            abort(404)

        try:
            if report_name == "claims":
                from src.reports.excel.claims_utilization import build_claims_report
                output_path = build_claims_report()
            elif report_name == "drugs":
                from src.reports.excel.drug_cost import build_drug_report
                output_path = build_drug_report()
            else:  # formulary
                from src.reports.excel.formulary_compliance import build_formulary_report
                output_path = build_formulary_report()
        except Exception as exc:
            return f"Report generation failed: {exc}", 500, {
                "Content-Type": "text/plain"
            }

        filename_map = {
            "claims": "claims_utilization.xlsx",
            "drugs": "drug_cost.xlsx",
            "formulary": "formulary_compliance.xlsx",
        }

        return send_file(
            output_path,
            as_attachment=True,
            download_name=filename_map[report_name],
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
