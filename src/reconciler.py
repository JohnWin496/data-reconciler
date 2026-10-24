"""Check the cleaned invoices against the cleaned customers."""
from collections import Counter


def reconcile_invoices(invoices, customers):
    """Look for inconsistencies between invoices and customers.

    Checks: the invoice's customer exists, the invoice number is unique,
    and SubTotal + TaxTotal equals Total (within 1 cent).
    Nothing is changed or removed. Returns a log of the problems found.
    """
    customer_names = {row["ContactName"] for row in customers}
    number_counts = Counter(row["InvoiceNumber"] for row in invoices)
    log = []

    for line, row in enumerate(invoices, start=2):        # line 1 of the file is the header
        name = row["ContactName"]
        if name not in customer_names:
            log.append({"line": line, "field": "ContactName", "old": name, "new": name,
                        "note": "FLAG: no matching customer"})

        number = row["InvoiceNumber"]
        if number_counts[number] > 1:
            log.append({"line": line, "field": "InvoiceNumber", "old": number, "new": number,
                        "note": "FLAG: repeated invoice number"})

        try:
            subtotal = float(row["SubTotal"])
            tax = float(row["TaxTotal"])
            total = float(row["Total"])
        except (ValueError, TypeError):
            continue                                      # can't do the sum on a non-number
        if abs(round(subtotal + tax - total, 2)) > 0.01:
            log.append({"line": line, "field": "Total", "old": row["Total"], "new": row["Total"],
                        "note": f"FLAG: SubTotal + TaxTotal is {subtotal + tax:.2f}, not Total"})
    return log
