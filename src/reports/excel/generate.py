"""
CLI entry point for Excel report generation.

Accepts a --report argument and dispatches to individual report builders.

Usage:
    python -m src.reports.excel.generate --report [all | claims | drugs | formulary]
    python -m src.reports.excel.generate --help
"""

import argparse
import sys
from typing import Callable, Dict, Tuple


def main() -> int:
    """
    Parse CLI arguments and dispatch to report builders.

    Returns
    -------
    int
        Exit code: 0 if all reports succeeded, 1 if any failed.
    """
    parser = argparse.ArgumentParser(
        description="Generate Excel reports from pharma claims data.",
        prog="python -m src.reports.excel.generate",
    )
    parser.add_argument(
        "--report",
        choices=["all", "claims", "drugs", "formulary"],
        default="all",
        help="Which report(s) to generate (default: all)",
    )
    args = parser.parse_args()

    # Map report names to builder functions and display names
    builders: Dict[str, Tuple[Callable[[], str], str]] = {
        "claims": (None, "Claims Utilization"),  # Will be set below
        "drugs": (None, "Drug Cost"),
        "formulary": (None, "Formulary Compliance"),
    }

    # Import the builder functions
    try:
        from src.reports.excel.claims_utilization import build_claims_report
        from src.reports.excel.drug_cost import build_drug_report
        from src.reports.excel.formulary_compliance import build_formulary_report

        builders["claims"] = (build_claims_report, "Claims Utilization")
        builders["drugs"] = (build_drug_report, "Drug Cost")
        builders["formulary"] = (build_formulary_report, "Formulary Compliance")
    except ImportError as e:
        print(f"Error: Could not import report builders: {e}", file=sys.stderr)
        print(
            "Note: Builder modules are implemented in Phase 3b-3d.",
            file=sys.stderr,
        )
        return 1

    # Determine which reports to run
    if args.report == "all":
        reports_to_run = ["claims", "drugs", "formulary"]
    else:
        reports_to_run = [args.report]

    # Run the selected reports
    succeeded = 0
    failed = 0

    for report_key in reports_to_run:
        builder_func, display_name = builders[report_key]
        print(f"Generating {display_name} report...")

        try:
            output_path = builder_func()
            print(f"  → Saved: {output_path}")
            succeeded += 1
        except Exception as e:
            print(f"  Error: {e}")
            failed += 1

    # Print summary
    print()
    print(f"Summary: {succeeded} succeeded, {failed} failed")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
