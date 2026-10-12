"""Functions that clean individual fields of a customer or invoice record."""
import re


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
