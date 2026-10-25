# data-reconciler

A small Python tool that cleans and reconciles messy accounting exports. It takes Xero-style customer and invoice CSV files, standardises the fields, merges duplicate customers, and checks the invoices against the customers. Every change is written to a log, so nothing is silently altered or deleted.

All data in this repo is synthetic (made up by `src/generate_synthetic_data.py`).

## What it does

1. **Cleans** customer and invoice fields: NZ phone numbers (`+64 9 234 5678` becomes `09 234 5678`), dates (three input formats become `YYYY-MM-DD`), company names (`KAURI  plumbing LIMITED` becomes `Kauri Plumbing Ltd`) and emails.
2. **Merges duplicate customers** that have the same cleaned name, keeping the most complete record and filling its blanks from the duplicate.
3. **Reconciles invoices** against the customers: unknown customer, `SubTotal + TaxTotal` not equal to `Total`, repeated invoice numbers.
4. **Writes** the cleaned data and a single change log to `output/`.

Values it can't understand are kept as they were and flagged for a human, not guessed.

## Run it

Python 3.8 or newer, standard library only.

```
python3 main.py
```

```
Customers: 54 loaded, 42 after merging 12 duplicates
Invoices:  128 loaded
Change log: 237 entries, 22 flagged for review
Wrote 3 files to output/
```

Tests (needs `pip install pytest`):

```
pytest
```

## Example log entries

| stage | line | field | old | new | note |
|---|---|---|---|---|---|
| clean customers | 2 | PhoneNumber | (09) 848-4967 | 09 848 4967 | changed |
| merge duplicates | 44 | ContactName | Kauri Consulting Ltd | Kauri Consulting Ltd | merged into line 2 |
| reconcile | 21 | ContactName | Kauri Fabrication Ltd | Kauri Fabrication Ltd | FLAG: no matching customer |

`line` is the row's line number in the original CSV file.

## Project layout

```
main.py                         runs the whole pipeline
src/loader.py                   reads CSV files
src/cleaner.py                  field and row cleaners
src/deduper.py                  finds and merges duplicate customers
src/reconciler.py               checks invoices against customers
src/generate_synthetic_data.py  makes the fake input data
data/                           input CSVs
output/                         cleaned CSVs and change_log.csv
tests/                          pytest tests
```

See [NOTES.md](NOTES.md) for design decisions and known limitations.

## How this was built

I built this as a learning project, one step at a time, with Claude (Anthropic's AI assistant) as a guide: it explained concepts and suggested designs, and I made the design choices, then ran, tested and committed each step myself.
