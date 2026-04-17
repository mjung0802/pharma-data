"""
Phase 4d: Formulary & Tier Compliance dashboard route.

Loads the four formulary_compliance.sql queries, builds Plotly chart JSON,
and renders the formulary.html template.
"""

from __future__ import annotations

from pathlib import Path

from flask import Blueprint, render_template

from src.reports.excel._utils import _load_queries

formulary_bp = Blueprint("formulary", __name__)

_SQL_FILE = (
    Path(__file__).resolve().parent.parent.parent / "sql" / "formulary_compliance.sql"
)


@formulary_bp.route("/formulary")
def formulary():
    try:
        # Import inside function to avoid circular imports at module load time
        from src.ingestion import run_query
        from flask import current_app

        queries = _load_queries(_SQL_FILE)

        df_tier = run_query(queries["tier_distribution"])
        df_gfr = run_query(queries["generic_fill_rate"])
        df_ofr = run_query(queries["on_formulary_rate"])
        df_cpt = run_query(queries["cost_per_tier"])

        # ------------------------------------------------------------------
        # KPI values
        # ------------------------------------------------------------------
        generic_fill_rate = float(df_gfr["generic_fill_rate"].iloc[0])
        on_formulary_rate = float(df_ofr["on_formulary_rate"].iloc[0])
        total_paid_claims = int(df_ofr["total_paid_claims"].iloc[0])

        # ------------------------------------------------------------------
        # Chart 1 — Gross Cost by Formulary Tier (bar chart)
        # ------------------------------------------------------------------
        tier_labels = [str(t) for t in df_tier["formulary_tier"].tolist()]
        tier_costs = df_tier["total_gross_cost"].tolist()

        chart1 = {
            "data": [
                {
                    "x": tier_labels,
                    "y": tier_costs,
                    "type": "bar",
                    "marker": {"color": ["#2ecc71", "#e74c3c"]},
                }
            ],
            "layout": {
                "title": {
                    "text": "Gross Cost by Formulary Tier (Paid Claims)",
                    "font": {"size": 16},
                },
                "xaxis": {"title": "Formulary Tier"},
                "yaxis": {"title": "Total Gross Cost ($)"},
                "margin": {"l": 60, "r": 20, "t": 50, "b": 50},
                "plot_bgcolor": "#ffffff",
                "paper_bgcolor": "#ffffff",
            },
        }

        # ------------------------------------------------------------------
        # Chart 2 — Generic vs. Brand Fill Rate (donut)
        # ------------------------------------------------------------------
        generic_claims = int(df_gfr["generic_claims"].iloc[0])
        brand_claims = int(df_gfr["brand_claims"].iloc[0])

        chart2 = {
            "data": [
                {
                    "labels": ["Generic", "Brand"],
                    "values": [generic_claims, brand_claims],
                    "type": "pie",
                    "hole": 0.4,
                    "marker": {"colors": ["#2ecc71", "#e74c3c"]},
                }
            ],
            "layout": {
                "title": {
                    "text": "Generic vs. Brand Fill Rate",
                    "font": {"size": 16},
                },
                "margin": {"l": 20, "r": 20, "t": 50, "b": 20},
                "plot_bgcolor": "#ffffff",
                "paper_bgcolor": "#ffffff",
            },
        }

        # ------------------------------------------------------------------
        # Chart 3 — Avg Member Copay by Tier and Drug Type (grouped bar)
        # ------------------------------------------------------------------
        # Build one series per drug type across all tiers
        drug_types = df_cpt["drug_type"].unique().tolist()
        type_colors = {"Generic": "#2ecc71", "Brand": "#e74c3c"}

        chart3_data = []
        for drug_type in drug_types:
            subset = df_cpt[df_cpt["drug_type"] == drug_type]
            tier_x = [str(t) for t in subset["formulary_tier"].tolist()]
            copay_y = subset["avg_member_copay"].tolist()
            chart3_data.append(
                {
                    "x": tier_x,
                    "y": copay_y,
                    "type": "bar",
                    "name": drug_type,
                    "marker": {"color": type_colors.get(drug_type, "#1a2744")},
                }
            )

        chart3 = {
            "data": chart3_data,
            "layout": {
                "title": {
                    "text": "Avg Member Copay by Tier and Drug Type",
                    "font": {"size": 16},
                },
                "barmode": "group",
                "xaxis": {"title": "Formulary Tier"},
                "yaxis": {"title": "Avg Member Copay ($)"},
                "margin": {"l": 60, "r": 20, "t": 50, "b": 80},
                "plot_bgcolor": "#ffffff",
                "paper_bgcolor": "#ffffff",
                "legend": {"orientation": "h", "y": -0.2},
            },
        }

        return render_template(
            "formulary.html",
            generic_fill_rate=generic_fill_rate,
            on_formulary_rate=on_formulary_rate,
            total_paid_claims=f"{total_paid_claims:,}",
            chart1_json=chart1,
            chart2_json=chart2,
            chart3_json=chart3,
        )
    except Exception:
        from flask import current_app
        current_app.logger.exception("Formulary dashboard failed")
        return "Dashboard temporarily unavailable. Check server logs.", 500
