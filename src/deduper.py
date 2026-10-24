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
