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
