"""Load the messy CSV files into Python."""
import csv


def load_csv(path):
    """Read a CSV file and return a list of dictionaries, one per row."""
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))
