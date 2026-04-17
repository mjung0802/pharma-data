"""
Phase 4c: Drug Cost Analysis dashboard route.

Loads the three drug_cost.sql queries, builds Plotly chart JSON,
and renders the drugs.html template.
"""

from __future__ import annotations

from pathlib import Path

from flask import Blueprint, render_template

from src.reports.excel._utils import _load_queries

drugs_bp = Blueprint("drugs", __name__)

_SQL_FILE = (
    Path(__file__).resolve().parent.parent.parent / "sql" / "drug_cost.sql"
)


@drugs_bp.route("/drugs")
def drugs():
    try:
        # Import inside function to avoid circular imports at module load time
        from src.ingestion import run_query
        from flask import current_app

        queries = _load_queries(_SQL_FILE)

        df_bvg = run_query(queries["brand_vs_generic"])
        df_top = run_query(queries["top_10_drugs"])
        df_tc = run_query(queries["therapeutic_class_spend"])

        # ------------------------------------------------------------------
        # KPI values
        # ------------------------------------------------------------------
        total_paid_cost = float(df_bvg["total_gross_cost"].sum())
        top_drug_name = str(df_top["brand_name"].iloc[0])
        top_drug_cost_raw = float(df_top["total_gross_cost"].iloc[0])
        top_drug_cost = f"${top_drug_cost_raw:,.2f}"

        # ------------------------------------------------------------------
        # Chart 1 — Top 10 Drugs Horizontal Bar
        # ------------------------------------------------------------------
        # Reverse so highest cost appears at the top of the horizontal bar chart
        top_costs = df_top["total_gross_cost"].tolist()[::-1]
        top_names = df_top["brand_name"].tolist()[::-1]

        chart1 = {
            "data": [
                {
                    "x": top_costs,
                    "y": top_names,
                    "type": "bar",
                    "orientation": "h",
                    "marker": {"color": "#1a2744"},
                }
            ],
            "layout": {
                "title": {
                    "text": "Top 10 Drugs by Gross Cost (Paid Claims)",
                    "font": {"size": 16},
                },
                "xaxis": {"title": "Total Gross Cost ($)"},
                "yaxis": {"title": "Drug Name", "automargin": True},
                "margin": {"l": 160, "r": 20, "t": 50, "b": 60},
                "plot_bgcolor": "#ffffff",
                "paper_bgcolor": "#ffffff",
            },
        }

        # ------------------------------------------------------------------
        # Chart 2 — Brand vs. Generic Donut
        # ------------------------------------------------------------------
        chart2 = {
            "data": [
                {
                    "labels": df_bvg["drug_type"].tolist(),
                    "values": df_bvg["total_gross_cost"].tolist(),
                    "type": "pie",
                    "hole": 0.4,
                    "marker": {"colors": ["#1a2744", "#3b82f6"]},
                }
            ],
            "layout": {
                "title": {
                    "text": "Brand vs. Generic Cost Split",
                    "font": {"size": 16},
                },
                "margin": {"l": 20, "r": 20, "t": 50, "b": 20},
                "plot_bgcolor": "#ffffff",
                "paper_bgcolor": "#ffffff",
            },
        }

        # ------------------------------------------------------------------
        # Chart 3 — Therapeutic Class Spend Grouped Bar
        # ------------------------------------------------------------------
        tc_names = df_tc["therapeutic_class"].tolist()

        chart3 = {
            "data": [
                {
                    "x": tc_names,
                    "y": df_tc["brand_cost"].tolist(),
                    "type": "bar",
                    "name": "Brand Cost",
                    "marker": {"color": "#1a2744"},
                },
                {
                    "x": tc_names,
                    "y": df_tc["generic_cost"].tolist(),
                    "type": "bar",
                    "name": "Generic Cost",
                    "marker": {"color": "#3b82f6"},
                },
            ],
            "layout": {
                "title": {
                    "text": "Spend by Therapeutic Class",
                    "font": {"size": 16},
                },
                "barmode": "group",
                "xaxis": {"title": "Therapeutic Class", "automargin": True},
                "yaxis": {"title": "Cost ($)"},
                "margin": {"l": 60, "r": 20, "t": 50, "b": 100},
                "plot_bgcolor": "#ffffff",
                "paper_bgcolor": "#ffffff",
                "legend": {"orientation": "h", "y": -0.25},
            },
        }

        return render_template(
            "drugs.html",
            total_paid_cost=f"${total_paid_cost:,.0f}",
            top_drug_name=top_drug_name,
            top_drug_cost=top_drug_cost,
            chart1_json=chart1,
            chart2_json=chart2,
            chart3_json=chart3,
        )
    except Exception:
        from flask import current_app
        current_app.logger.exception("Drugs dashboard failed")
        return "Dashboard temporarily unavailable. Check server logs.", 500
