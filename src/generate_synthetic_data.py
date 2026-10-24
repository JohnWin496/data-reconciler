
"""Generate messy, fake Xero-style customer and invoice CSVs.

All data is synthetic. Seeded, so every run produces the same files.
"""
import csv
import random
from datetime import date, timedelta

random.seed(42)

FIRST_WORDS = ["Kauri", "Harbour", "Pacific", "Summit", "Tui", "Southern",
               "Northland", "Rimu", "Manuka", "Fernleaf", "Bluewater",
               "Granite", "Cedar", "Albatross", "Pohutukawa"]
SECOND_WORDS = ["Plumbing", "Logistics", "Dental", "Builders", "Foods",
                "Electrical", "Consulting", "Print", "Motors", "Landscapes"]
STREETS = ["Queen", "Victoria", "Karangahape", "Great South", "Ormiston", "Pah"]
CITIES = ["Auckland", "Manukau", "Takapuna", "Hamilton", "Wellington"]


def format_phone(digits):
    """Return the same phone number written in one of five different styles."""
    area, a, b = digits[:2], digits[2:5], digits[5:]
    styles = [
        f"{area} {a} {b}",
        f"({area}) {a}-{b}",
        f"+64 {area[1]} {a} {b}",
        digits,
        f"{area}-{a}-{b}",
    ]
    return random.choice(styles)


def random_date(start_year, end_year):
    """Return a random date between 1 Jan of start_year and 31 Dec of end_year."""
    start = date(start_year, 1, 1)
    end = date(end_year, 12, 31)
    return start + timedelta(days=random.randint(0, (end - start).days))


def format_date(d):
    """Return a date written in one of three different formats."""
    return d.strftime(random.choice(["%d/%m/%Y", "%Y-%m-%d", "%d %b %Y"]))


def mangle_name(name):
    """Make a sloppy variant of a company name, like a duplicate typed by hand."""
    options = [
        name.upper(),
        name.replace("Ltd", "Limited"),
        name.lower(),
        "  " + name.replace(" ", "  ", 1) + " ",
    ]
    return random.choice(options)


def make_customer(name, email, digits):
    """Build one customer row. Email and phone are sometimes left blank."""
    return {
        "ContactName": name,
        "EmailAddress": "" if random.random() < 0.10 else email,
        "PhoneNumber": "" if random.random() < 0.05 else format_phone(digits),
        "POAddressLine1": f"{random.randint(1, 300)} {random.choice(STREETS)} Road",
        "POCity": random.choice(CITIES),
        "CreatedDate": format_date(random_date(2015, 2024)),
    }


def build_customers():
    """Return (customer rows, dict of real name -> every spelling used for it)."""
    rows = []
    spellings = {}
    combos = [(a, b) for a in FIRST_WORDS for b in SECOND_WORDS] # creates all possible combinations

    for index, (first, second) in enumerate(random.sample(combos, 40)):
        name = f"{first} {second} Ltd"
        email = f"info@{first}{second}.co.nz".lower()
        digits = random.choice(["09", "04", "03"]) + str(random.randint(2000000, 9999999))
        spellings[name] = [name]
        rows.append(make_customer(name, email, digits))

        if index < 12:  # the first 12 companies also get a sloppy duplicate
            dup_name = mangle_name(name)
            spellings[name].append(dup_name)
            rows.append(make_customer(dup_name, email.upper(), digits))

    # Two genuinely different companies with similar names. NOT duplicates.
    rows.append(make_customer("Smith Ltd", "accounts@smithltd.co.nz", "093334444"))
    rows.append(make_customer("Smith & Sons Ltd", "office@smithandsons.co.nz", "094445555"))
    spellings["Smith Ltd"] = ["Smith Ltd"]
    spellings["Smith & Sons Ltd"] = ["Smith & Sons Ltd"]

    return rows, spellings


def build_invoices(spellings):
    """Return 1 to 5 invoices per real company, under any spelling of its name."""
    rows = []
    number = 1
    for names_used in spellings.values():
        for i in range(random.randint(1, 5)):
            subtotal = round(random.uniform(100, 5000), 2)
            tax = round(subtotal * 0.15, 2)  # NZ GST is 15%
            total = round(subtotal + tax, 2)
            if random.random() < 0.03:  # a few suspicious negative amounts
                subtotal, tax, total = -subtotal, -tax, -total
            rows.append({
                "InvoiceNumber": f"INV-{number:04d}",
                "ContactName": random.choice(names_used),
                "InvoiceDate": "" if random.random() < 0.03 else format_date(random_date(2023, 2025)), # blank if random number is less than 0.3, else, random date with random format
                "SubTotal": subtotal,
                "TaxTotal": tax,
                "Total": total,
            })
            number += 1

    # Deliberate faults for the reconciler to catch. No random calls here,
    # so the rest of the data is identical to before.
    rows[9]["Total"] = round(rows[9]["Total"] + 50, 2)         # total no longer adds up
    rows[19]["ContactName"] = "Kauri Fabrication Ltd"          # not a real customer (orphan)
    rows[39]["InvoiceNumber"] = rows[38]["InvoiceNumber"]      # repeated invoice number

    return rows



def write_csv(path, rows):
    """Write a list of dicts to a CSV file, using the first row's keys as headers."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main():
    customers, spellings = build_customers()
    random.shuffle(customers)
    invoices = build_invoices(spellings)
    write_csv("data/old_customers.csv", customers)
    write_csv("data/old_invoices.csv", invoices)
    print(f"Wrote {len(customers)} customers and {len(invoices)} invoices to data/")


if __name__ == "__main__": # main runs if this file is directly ran 
    main()
