"""Tests for duplicate detection and merging in src/deduper.py."""
from src.deduper import dedupe_customers, find_duplicate_groups, match_evidence


def make_row(name, email="", phone=""):
    """Build a small customer row for testing."""
    return {"ContactName": name, "EmailAddress": email, "PhoneNumber": phone, "POCity": "Auckland"}


def test_find_duplicate_groups_returns_only_repeated_names_with_line_numbers():
    rows = [make_row("Kauri Plumbing Ltd"), make_row("Tui Dental Ltd"),
            make_row("Kauri Plumbing Ltd"), make_row("Smith Ltd")]
    groups = find_duplicate_groups(rows)
    assert len(groups) == 1
    assert [line for line, _ in groups[0]] == [2, 4]          # line 1 is the header


def test_match_evidence_both_fields_agree():
    group = [(2, make_row("A", "a@a.nz", "09 111 2222")), (3, make_row("A", "a@a.nz", "09 111 2222"))]
    assert match_evidence(group) == ["EmailAddress", "PhoneNumber"]


def test_match_evidence_a_blank_does_not_count():
    group = [(2, make_row("A", "a@a.nz", "09 111 2222")), (3, make_row("A", "a@a.nz", ""))]
    assert match_evidence(group) == ["EmailAddress"]


def test_match_evidence_two_blanks_do_not_count():
    group = [(2, make_row("A", "", "")), (3, make_row("A", "", ""))]
    assert match_evidence(group) == []


def test_dedupe_merges_duplicates_and_keeps_similar_names_apart():
    rows = [make_row("Smith Ltd", "a@s.nz", "09 333 4444"),
            make_row("Smith & Sons Ltd", "b@s.nz", "09 444 5555"),
            make_row("Rimu Foods Ltd", "r@r.nz", "03 555 6666"),
            make_row("Rimu Foods Ltd", "r@r.nz", "03 555 6666")]
    unique, log = dedupe_customers(rows)
    assert [r["ContactName"] for r in unique] == ["Smith Ltd", "Smith & Sons Ltd", "Rimu Foods Ltd"]
    assert [e["note"] for e in log] == ["merged into line 4"]   # the tie goes to the first row, line 4


def test_dedupe_fills_a_gap_from_the_dropped_row():
    rows = [make_row("Kauri Ltd", "info@k.nz", ""),
            make_row("Kauri Ltd", "", "09 234 5678")]
    unique, log = dedupe_customers(rows)
    assert len(unique) == 1
    assert unique[0]["EmailAddress"] == "info@k.nz"
    assert unique[0]["PhoneNumber"] == "09 234 5678"          # copied from the dropped row
    assert any(e["note"].startswith("filled from line") for e in log)


def test_dedupe_flags_a_merge_made_on_the_name_alone():
    rows = [make_row("Bluewater Ltd", "x@b.nz", ""), make_row("Bluewater Ltd", "y@b.nz", "")]
    unique, log = dedupe_customers(rows)
    assert len(unique) == 1
    assert any(e["note"].startswith("FLAG: merged on name only") for e in log)


def test_dedupe_does_not_change_the_input_rows():
    rows = [make_row("Kauri Ltd", "info@k.nz", ""), make_row("Kauri Ltd", "", "09 234 5678")]
    before = [dict(r) for r in rows]
    dedupe_customers(rows)
    assert rows == before
