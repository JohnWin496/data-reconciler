"""Tests for the invoice checks in src/reconciler.py."""
from src.reconciler import reconcile_invoices

CUSTOMERS = [{"ContactName": "Kauri Plumbing Ltd"}, {"ContactName": "Tui Dental Ltd"}]


def make_invoice(number="INV-0001", name="Kauri Plumbing Ltd", subtotal="100.00", tax="15.00", total="115.00"):
    """Build a small invoice row for testing."""
    return {"InvoiceNumber": number, "ContactName": name,
            "SubTotal": subtotal, "TaxTotal": tax, "Total": total}


def notes(log):
    return [entry["note"] for entry in log]


def test_clean_invoices_produce_no_problems():
    assert reconcile_invoices([make_invoice(), make_invoice("INV-0002", "Tui Dental Ltd")], CUSTOMERS) == []


def test_invoice_for_unknown_customer_is_flagged():
    log = reconcile_invoices([make_invoice(name="Kauri Fabrication Ltd")], CUSTOMERS)
    assert notes(log) == ["FLAG: no matching customer"]
    assert log[0]["line"] == 2                               # first data row is line 2


def test_total_that_does_not_add_up_is_flagged():
    log = reconcile_invoices([make_invoice(total="165.00")], CUSTOMERS)
    assert len(log) == 1
    assert log[0]["field"] == "Total"
    assert "115.00" in log[0]["note"]                       # says what the total should be


def test_one_cent_difference_is_allowed():
    assert reconcile_invoices([make_invoice(total="115.01")], CUSTOMERS) == []


def test_repeated_invoice_number_flags_both_rows():
    log = reconcile_invoices([make_invoice("INV-0007"), make_invoice("INV-0007")], CUSTOMERS)
    assert notes(log) == ["FLAG: repeated invoice number"] * 2
    assert [e["line"] for e in log] == [2, 3]


def test_unreadable_total_is_skipped_by_the_sum_check():
    assert reconcile_invoices([make_invoice(total="")], CUSTOMERS) == []


def test_invoices_are_not_changed():
    invoices = [make_invoice(total="165.00"), make_invoice(name="Nobody Ltd")]
    before = [dict(i) for i in invoices]
    reconcile_invoices(invoices, CUSTOMERS)
    assert invoices == before
