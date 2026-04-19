import pytest
from openpyxl import load_workbook
from src.reports.excel.claims_utilization import build_claims_report
from src.reports.excel.drug_cost import build_drug_report
from src.reports.excel.formulary_compliance import build_formulary_report


# Claims Utilization tests
def test_claims_detail_sheet_currency_columns_right_aligned(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    path = build_claims_report()
    wb = load_workbook(path)
    ws = wb["Detail"]
    headers = [ws.cell(row=1, column=c).value for c in range(1, ws.max_column + 1)]
    gross_col = headers.index("gross_cost") + 1
    assert ws.cell(row=2, column=gross_col).alignment.horizontal == "right"


def test_claims_detail_sheet_quantity_column_right_aligned(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    path = build_claims_report()
    wb = load_workbook(path)
    ws = wb["Detail"]
    headers = [ws.cell(row=1, column=c).value for c in range(1, ws.max_column + 1)]
    qty_col = headers.index("quantity") + 1
    assert ws.cell(row=2, column=qty_col).alignment.horizontal == "right"


# Drug Cost tests
def test_drug_cost_detail_sheet_currency_columns_right_aligned(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    path = build_drug_report()
    wb = load_workbook(path)
    ws = wb["Detail"]
    headers = [ws.cell(row=1, column=c).value for c in range(1, ws.max_column + 1)]
    gross_col = headers.index("gross_cost") + 1
    assert ws.cell(row=2, column=gross_col).alignment.horizontal == "right"


def test_drug_cost_detail_sheet_quantity_column_right_aligned(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    path = build_drug_report()
    wb = load_workbook(path)
    ws = wb["Detail"]
    headers = [ws.cell(row=1, column=c).value for c in range(1, ws.max_column + 1)]
    qty_col = headers.index("quantity") + 1
    assert ws.cell(row=2, column=qty_col).alignment.horizontal == "right"


# Formulary Compliance tests
def test_formulary_detail_sheet_currency_columns_right_aligned(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    path = build_formulary_report()
    wb = load_workbook(path)
    ws = wb["Detail"]
    headers = [ws.cell(row=1, column=c).value for c in range(1, ws.max_column + 1)]
    gross_col = headers.index("gross_cost") + 1
    assert ws.cell(row=2, column=gross_col).alignment.horizontal == "right"


def test_formulary_detail_sheet_quantity_column_right_aligned(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    path = build_formulary_report()
    wb = load_workbook(path)
    ws = wb["Detail"]
    headers = [ws.cell(row=1, column=c).value for c in range(1, ws.max_column + 1)]
    qty_col = headers.index("quantity") + 1
    assert ws.cell(row=2, column=qty_col).alignment.horizontal == "right"
