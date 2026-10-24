"""Functions that clean individual fields of a customer or invoice record."""
import re
from datetime import datetime          # needed for parsing dates

def clean_phone_number(phone):
    """Return a NZ phone number as '09 234 5678'.

    Returns "" if the phone is blank, or None if it can't be standardised.
    """
    digits = re.sub(r"\D", "", phone)       # keep only the digits

    if digits == "":
        return ""

    if digits.startswith("64"):             # +64 9 234 5678 -> 092345678
        digits = "0" + digits[2:]

    if len(digits) != 9 or not digits.startswith("0"):
        return None                         # doesn't look like a number we understand

    return f"{digits[:2]} {digits[2:5]} {digits[5:]}"

DATE_FORMATS = ["%d/%m/%Y", "%Y-%m-%d", "%d %b %Y"]   # the formats we expect

def clean_date(text):
    """Return a date as 'YYYY-MM-DD'.

    Returns "" if blank, or None if it matches none of the known formats.
    """
    text = text.strip()
    if text == "":
        return ""

    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue                   # wrong format, try the next one

    return None

def clean_name(name):
    """Standardise a company name: tidy spaces, Title Case, 'Limited' -> 'Ltd'."""
    name = re.sub(r"\s+", " ", name).strip()    # collapse repeated spaces, trim the ends
    name = name.title()                          # KAURI PLUMBING LTD -> Kauri Plumbing Ltd
    name = re.sub(r"\bLimited\b", "Ltd", name)   # Limited -> Ltd
    return name

def clean_email(email):
    """Return an email in lowercase, "" if blank, or None if it doesn't look valid."""
    email = email.strip().lower()
    if email == "":
        return ""
    if re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return email
    return None

def _apply(cleaner, row, field, line, log):               # cleans one field with one cleaner and returns the result
    """Run one cleaner on one field, log what happened, return the value to keep."""
    old = row[field]
    new = cleaner(old)

    if new is None:                                       # cleaner couldn't understand it
        log.append({"line": line, "field": field, "old": old, "new": old,
                    "note": "FLAG: could not clean"})
        return old                                        # keep the original, don't guess
    if new == "":
        log.append({"line": line, "field": field, "old": old, "new": "",
                    "note": "FLAG: missing value"})
    elif new != old:                                      # original changed
        log.append({"line": line, "field": field, "old": old, "new": new,
                    "note": "changed"})
    return new


def clean_customers(rows):
    """Clean every customer row. Returns (cleaned_rows, log)."""
    cleaned = []
    log = []
    for line, row in enumerate(rows, start=2):            # line 1 of the file is the header
        new_row = dict(row)                               # a copy, so the loaded data stays untouched
        new_row["ContactName"] = _apply(clean_name, row, "ContactName", line, log)
        new_row["EmailAddress"] = _apply(clean_email, row, "EmailAddress", line, log)
        new_row["PhoneNumber"] = _apply(clean_phone_number, row, "PhoneNumber", line, log)
        new_row["CreatedDate"] = _apply(clean_date, row, "CreatedDate", line, log)
        cleaned.append(new_row)
    return cleaned, log


def clean_invoices(rows):
    """Clean every invoice row. Returns (cleaned_rows, log)."""
    cleaned = []
    log = []
    for line, row in enumerate(rows, start=2):
        new_row = dict(row)
        new_row["ContactName"] = _apply(clean_name, row, "ContactName", line, log)
        new_row["InvoiceDate"] = _apply(clean_date, row, "InvoiceDate", line, log)
        try:                                              # prevents crash on incorrect "Total" value
            total = float(row["Total"])                   # blank or text will fail here
        except (ValueError, TypeError):
            log.append({"line": line, "field": "Total", "old": row["Total"],
                        "new": row["Total"], "note": "FLAG: Total is not a number"})
        else:
            if total < 0:                                 # only a check, the value isn't changed
                log.append({"line": line, "field": "Total", "old": row["Total"],
                            "new": row["Total"], "note": "FLAG: negative amount"})
        cleaned.append(new_row)
    return cleaned, log
