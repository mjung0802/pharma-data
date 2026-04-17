"""
Phase 4b: Claims Utilization dashboard route.

Loads the three claims_utilization.sql queries, builds Plotly chart JSON,
and renders the claims.html template.
"""

from __future__ import annotations

from pathlib import Path

from flask import Blueprint, render_template

from src.reports.excel._utils import _load_queries

claims_bp = Blueprint("claims", __name__)

_SQL_FILE = (
    Path(__file__).resolve().parent.parent.parent / "sql" / "claims_utilization.sql"
)


@claims_bp.route("/claims")
def claims():
    try:
        # Import inside function to avoid circular imports at module load time
        from src.ingestion import run_query
        from flask import current_app

        queries = _load_queries(_SQL_FILE)

        df_status = run_query(queries["status_summary"])
        df_monthly = run_query(queries["monthly_trend"])
        df_plan = run_query(queries["plan_breakdown"])

        # ------------------------------------------------------------------
        # KPI values
        # ------------------------------------------------------------------
        paid_rate_series = df_status["paid_rate"].dropna()
        paid_rate = float(paid_rate_series.iloc[0]) if not paid_rate_series.empty else 0.0
        total_claims = int(df_monthly["claim_count"].sum())
        paid_claims = int(
            df_status.loc[df_status["claim_status"] == "Paid", "claim_count"].sum()
        )

        # ------------------------------------------------------------------
        # Chart 1 — Monthly Claim Trend (line chart)
        # ------------------------------------------------------------------
        chart1 = {
            "data": [
                {
                    "x": df_monthly["year_month"].tolist(),
                    "y": df_monthly["claim_count"].tolist(),
                    "type": "scatter",
                    "mode": "lines+markers",
                    "name": "Claims",
                    "line": {"color": "#1a2744", "width": 2},
                    "marker": {"color": "#1a2744", "size": 6},
                }
            ],
            "layout": {
                "title": {"text": "Monthly Claim Volume (2024)", "font": {"size": 16}},
                "xaxis": {"title": "Month"},
                "yaxis": {"title": "Claim Count"},
                "margin": {"l": 50, "r": 20, "t": 50, "b": 50},
                "plot_bgcolor": "#ffffff",
                "paper_bgcolor": "#ffffff",
            },
        }

        # ------------------------------------------------------------------
        # Chart 2 — Plan Status Breakdown (grouped bar chart)
        # ------------------------------------------------------------------
        plan_names = df_plan["plan_name"].tolist()

        chart2 = {
            "data": [
                {
                    "x": plan_names,
                    "y": df_plan["paid_count"].tolist(),
                    "type": "bar",
                    "name": "Paid",
                    "marker": {"color": "#2ecc71"},
                },
                {
                    "x": plan_names,
                    "y": df_plan["rejected_count"].tolist(),
                    "type": "bar",
                    "name": "Rejected",
                    "marker": {"color": "#e74c3c"},
                },
                {
                    "x": plan_names,
                    "y": df_plan["reversed_count"].tolist(),
                    "type": "bar",
                    "name": "Reversed",
                    "marker": {"color": "#f39c12"},
                },
            ],
            "layout": {
                "title": {"text": "Claim Status by Plan", "font": {"size": 16}},
                "barmode": "group",
                "xaxis": {"title": "Plan"},
                "yaxis": {"title": "Claim Count"},
                "margin": {"l": 50, "r": 20, "t": 50, "b": 80},
                "plot_bgcolor": "#ffffff",
                "paper_bgcolor": "#ffffff",
                "legend": {"orientation": "h", "y": -0.2},
            },
        }

        return render_template(
            "claims.html",
            paid_rate=paid_rate,
            total_claims=f"{total_claims:,}",
            paid_claims=f"{paid_claims:,}",
            chart1_json=chart1,
            chart2_json=chart2,
        )
    except Exception:
        from flask import current_app
        current_app.logger.exception("Claims dashboard failed")
        return "Dashboard temporarily unavailable. Check server logs.", 500
