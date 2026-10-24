"""Run the whole pipeline: load, clean, merge duplicates, reconcile, write output."""
import csv
import os

from src.loader import load_csv
from src.cleaner import clean_customers, clean_invoices
from src.deduper import dedupe_customers
from src.reconciler import reconcile_invoices

BASE = os.path.dirname(os.path.abspath(__file__))       # the project folder, wherever you run from
LOG_FIELDS = ["stage", "line", "field", "old", "new", "note"]


def write_csv(path, rows, fieldnames):
    """Write a list of dicts to a CSV file with the given column order."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def tag(log, stage):
    """Return the log entries with a 'stage' column added at the front."""
    return [{"stage": stage, **entry} for entry in log]


def main():
    customers = load_csv(os.path.join(BASE, "data", "old_customers.csv"))
    invoices = load_csv(os.path.join(BASE, "data", "old_invoices.csv"))
    customers_loaded = len(customers)

    customers, clean_customer_log = clean_customers(customers)
    customers, merge_log = dedupe_customers(customers)
    invoices, clean_invoice_log = clean_invoices(invoices)
    problem_log = reconcile_invoices(invoices, customers)

    change_log = (tag(clean_customer_log, "clean customers")
                  + tag(merge_log, "merge duplicates")
                  + tag(clean_invoice_log, "clean invoices")
                  + tag(problem_log, "reconcile"))

    out = os.path.join(BASE, "output")
    os.makedirs(out, exist_ok=True)
    write_csv(os.path.join(out, "cleaned_customers.csv"), customers, list(customers[0].keys()))
    write_csv(os.path.join(out, "cleaned_invoices.csv"), invoices, list(invoices[0].keys()))
    write_csv(os.path.join(out, "change_log.csv"), change_log, LOG_FIELDS)

    flags = sum(1 for entry in change_log if entry["note"].startswith("FLAG"))
    print(f"Customers: {customers_loaded} loaded, {len(customers)} after merging "
          f"{customers_loaded - len(customers)} duplicates")
    print(f"Invoices:  {len(invoices)} loaded")
    print(f"Change log: {len(change_log)} entries, {flags} flagged for review")
    print("Wrote 3 files to output/")


if __name__ == "__main__":
    main()
