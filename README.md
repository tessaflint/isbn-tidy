# isbn-tidy

ISBNs and barcodes look like plain numbers but they're not - the last
digit is a checksum over the rest. Copy one out of a PDF catalog, an
Excel column, or a photo run through OCR and you'll get things like:

```
978-3-16-148410-О     (that's a Cyrillic О, not a zero)
0 13 468599 x
ISBN: 9780134685991
013468599X
```

Different dash characters, stray spaces, a capitalization-sensitive
check character on ISBN-10, and sometimes a label glued onto the front.
Before you can even check whether the number is *right*, you have to
agree on what the number *is*.

`isbn-tidy` does that normalisation step: strip separators, uppercase
the check character, figure out from the resulting length whether
you're looking at an ISBN-10, ISBN-13/EAN-13, or UPC-A, and verify the
checksum. If it's valid it gives you back a clean `payload-check`
string; if not, it tells you what check digit it expected instead.

It does not know the ISBN range registry (which prefixes belong to
which country or publisher), so it can't insert publisher/title
hyphens the way a real ISBN is usually printed - it only ever splits
off the trailing check digit, which is structurally correct no matter
who issued the number.

## Install

Nothing to install - it's standard library only. Drop the `isbn_tidy/`
package next to your code, or `pip install -e .` from a checkout.

## Use it from Python

```python
from isbn_tidy import format_identifier, convert_isbn10_to_13

result = format_identifier("0 13 468599 x")
result.kind        # "ISBN-10"
result.valid        # True
result.formatted    # "013468599-X"

bad = format_identifier("978-3-16-148410-5")
bad.valid                  # False
bad.expected_check_digit   # "0"
bad.message                # "check digit is '5', expected '0'"

convert_isbn10_to_13("013468599X")  # "9780134685991"
```

## Use it from the shell

```
$ python -m isbn_tidy "0-13-468599-X" "978-3-16-148410-5"
ISBN-10  013468599-X
ISBN-13  INVALID  '978-3-16-148410-5' -> check digit is '5', expected '0'
```

Or pipe a column straight out of a spreadsheet export:

```
$ cut -f3 catalog_export.tsv | python -m isbn_tidy
```

## Layout

- `isbn_tidy/checksum.py` - the check-digit math for ISBN-10, ISBN-13/EAN-13, and UPC-A
- `isbn_tidy/formatter.py` - cleans input and produces a `FormatResult`
- `isbn_tidy/__main__.py` - the `python -m isbn_tidy` CLI

## License

MIT, see `LICENSE`.
