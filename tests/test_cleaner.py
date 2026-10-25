"""Tests for the field cleaners in src/cleaner.py."""
import pytest

from src.cleaner import clean_date, clean_email, clean_name, clean_phone_number, clean_invoices


@pytest.mark.parametrize("raw, expected", [
    ("09 234 5678", "09 234 5678"),        # already clean
    ("(09) 234-5678", "09 234 5678"),      # brackets and a dash
    ("+64 9 234 5678", "09 234 5678"),     # international format
    ("092345678", "09 234 5678"),          # digits only
    ("09-234-5678", "09 234 5678"),        # dashes
    ("", ""),                              # blank stays blank
    ("12345", None),                       # too short to be a number we understand
])
def test_clean_phone_number(raw, expected):
    assert clean_phone_number(raw) == expected


@pytest.mark.parametrize("raw, expected", [
    ("25/12/2024", "2024-12-25"),
    ("2024-12-25", "2024-12-25"),
    ("25 Dec 2024", "2024-12-25"),
    ("", ""),
    ("   ", ""),                           # spaces only counts as blank
    ("Dec 25th", None),                    # no known format
    ("31/02/2024", None),                  # 31 February does not exist
])
def test_clean_date(raw, expected):
    assert clean_date(raw) == expected


@pytest.mark.parametrize("raw, expected", [
    ("KAURI PLUMBING LTD", "Kauri Plumbing Ltd"),
    ("  kauri   plumbing  Limited ", "Kauri Plumbing Ltd"),
    ("Smith & Sons Ltd", "Smith & Sons Ltd"),     # already clean, must not change
])
def test_clean_name(raw, expected):
    assert clean_name(raw) == expected


@pytest.mark.parametrize("raw, expected", [
    ("INFO@Kauri.CO.NZ ", "info@kauri.co.nz"),
    ("", ""),
    ("not-an-email", None),
    ("a@b", None),                         # no dot after the @
])
def test_clean_email(raw, expected):
    assert clean_email(raw) == expected


def test_bad_invoice_total_is_flagged_not_crashed():
    rows = [{"InvoiceNumber": "A", "ContactName": "x ltd", "InvoiceDate": "2025-01-01", "Total": ""}]
    cleaned, log = clean_invoices(rows)
    assert any(entry["note"] == "FLAG: Total is not a number" for entry in log)
