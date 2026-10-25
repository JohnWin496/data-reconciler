# Notes

## Design decisions

- **Never guess.** A cleaner returns `None` when it can't understand a value. The original is kept and the row is flagged, not "fixed" by a guess.
- **Duplicates are matched on the cleaned company name.** Email and phone are supporting evidence only, because they are often blank in real exports. A merge with no agreeing email or phone is flagged for review.
- **Which row survives a merge:** the one with the most filled-in fields (first in the file on a tie). Its blank fields are filled from the dropped row, and the log records both the merge and each fill.
- **Similar names stay separate.** `Smith Ltd` and `Smith & Sons Ltd` are different companies, and the tests check they are not merged.
- **1-cent tolerance** on `SubTotal + TaxTotal = Total`, to allow for rounding.
- **Inputs are copied, never changed.** Functions return new rows and a log.
- **One change log** with a `stage` column, so every entry can be filtered in a spreadsheet.
- **Reproducible data.** The generator is seeded. A few faults (an unknown customer, a wrong total, a repeated invoice number) are added at the end without extra random calls, so the reconciler has something to find.

## Known limitations

- Duplicates must match exactly after cleaning. Typos (`Kauri Plumbin Ltd`) or different spellings of a business name are not caught.
- `str.title()` mangles some names, such as `McDonald` becoming `Mcdonald` and `ABC Ltd` becoming `Abc Ltd`.
- Phone cleaning handles 9-digit NZ landlines only. Mobile (`021...`) and `0800` numbers are flagged as "could not clean".
- Dates assume day/month/year and only the three formats the generator produces.
- Email validation is a simple pattern check, not a real deliverability check.
- When duplicates disagree (for example on address or created date), the dropped row's values are not kept. The log only says which line it was merged into.
- The GST check (tax is 15% of subtotal) is not implemented. Negative invoices are flagged but not matched to credit notes.
- Whole files are read into memory, which is fine for small exports but not very large ones.

## Ideas for next steps

- Fuzzy name matching, with a similarity score in the log.
- Accept more phone and date formats.
- Command-line options for input and output paths.
- Keep the dropped row's conflicting values in the log.
