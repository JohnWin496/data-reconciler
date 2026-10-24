"""Find customers that appear more than once."""
from collections import defaultdict


def find_duplicate_groups(rows):
    """Group customer rows that share the same cleaned ContactName.

    Returns a list of groups. Each group is a list of (line, row) pairs,
    where line is the row's line number in the CSV file. Only names that
    appear 2 or more times are returned.
    """
    by_name = defaultdict(list)
    for line, row in enumerate(rows, start=2):        # line 1 of the file is the header
        by_name[row["ContactName"]].append((line, row))
    return [group for group in by_name.values() if len(group) > 1]


def match_evidence(group):
    """Return which of EmailAddress / PhoneNumber agree across the whole group.

    A field only counts if every row has it filled in and all values are equal.
    """
    evidence = []
    for field in ("EmailAddress", "PhoneNumber"):
        values = {row[field] for _, row in group}
        if len(values) == 1 and "" not in values:
            evidence.append(field)
    return evidence

def _filled_count(row):
    """Count how many fields in a row are not blank."""
    return sum(1 for value in row.values() if value != "")


def merge_group(group):
    """Merge one duplicate group into a single row.

    Keeps the row with the most filled-in fields (the first one wins a tie),
    fills its blank fields from the other rows, and logs everything it does.
    Returns (kept_line, merged_row, log).
    """
    kept_line, kept_row = max(group, key=lambda pair: _filled_count(pair[1]))
    merged = dict(kept_row)                               # a copy, so the input stays untouched
    log = []

    for line, row in group:
        if line == kept_line:
            continue
        log.append({"line": line, "field": "ContactName", "old": row["ContactName"],
                    "new": merged["ContactName"], "note": f"merged into line {kept_line}"})
        for field, value in row.items():
            if merged[field] == "" and value != "":       # a gap we can fill
                merged[field] = value
                log.append({"line": kept_line, "field": field, "old": "",
                            "new": value, "note": f"filled from line {line}"})

    if not match_evidence(group):                         # matched on the name alone
        log.append({"line": kept_line, "field": "ContactName", "old": merged["ContactName"],
                    "new": merged["ContactName"], "note": "FLAG: merged on name only, please review"})
    return kept_line, merged, log


def dedupe_customers(rows):
    """Merge every duplicate group. Returns (unique_rows, log)."""
    replacements = {}                                     # kept line -> merged row
    dropped = set()                                       # lines that were merged away
    log = []
    for group in find_duplicate_groups(rows):
        kept_line, merged, group_log = merge_group(group)
        replacements[kept_line] = merged
        dropped.update(line for line, _ in group if line != kept_line)
        log.extend(group_log)

    unique = []
    for line, row in enumerate(rows, start=2):
        if line in dropped:
            continue
        unique.append(replacements.get(line, row))
    return unique, log
