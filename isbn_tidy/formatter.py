"""Turn messy, pasted-from-anywhere identifiers into a clean, validated form.

"Messy" here means the stuff that actually shows up in spreadsheets and
scanned catalog records: extra whitespace, ascii and unicode dashes mixed
together, stray slashes or underscores used as separators, and a lowercase
x on ISBN-10 check digits. This module does not know about the ISBN range
registry, so it can't split a number into group/registrant/publisher parts -
it only ever separates the trailing check digit, which is always correct
regardless of which agency issued the number.
"""

import re
from dataclasses import dataclass
from typing import Optional

from . import checksum

# Ascii hyphen, common unicode dash variants, underscores, slashes, dots -
# anything that turns up as a separator in pasted identifiers.
_SEPARATORS = re.compile(r"[\s‐‑‒–—−_/.-]")


# Letters OCR engines routinely emit in place of digits. Applied after
# uppercasing, so a lowercase l arrives here as L. The Cyrillic capital O is
# included because it is visually identical to Latin O and shows up in
# text copied out of PDFs. X is deliberately absent: it is a legal ISBN-10
# check character.
_OCR_FIXES = str.maketrans({
    "O": "0",
    "О": "0",
    "I": "1",
    "L": "1",
})


@dataclass
class FormatResult:
    raw: str
    cleaned: str
    kind: str
    valid: bool
    formatted: Optional[str]
    expected_check_digit: Optional[str]
    message: str
    ocr_fixed: bool = False


def clean(raw: str) -> str:
    """Strip separators and normalise case, leaving only the payload characters."""
    if raw is None:
        raise ValueError("clean() needs a string")
    return _SEPARATORS.sub("", raw).upper()


def format_identifier(raw: str) -> FormatResult:
    """Classify, validate, and reformat a barcode-like string.

    Length after cleanup decides what the string is being treated as:
    10 characters -> ISBN-10, 13 -> ISBN-13/EAN-13, 12 -> UPC-A. Anything
    else is reported as unknown rather than guessed at.

    Look-alike letters (O, I, L) are read as digits only once the length has
    matched a known format, so arbitrary text is never rewritten. When that
    happens `ocr_fixed` is set and `cleaned` holds the corrected string; the
    checksum still has to pass, which keeps a wrong guess from being
    reported as valid.
    """
    cleaned = clean(raw)
    length = len(cleaned)

    if length in (10, 12, 13):
        fixed = cleaned.translate(_OCR_FIXES)
        handler = {10: _format_isbn10, 13: _format_isbn13, 12: _format_upca}[length]
        result = handler(raw, fixed)
        if fixed != cleaned:
            result.ocr_fixed = True
            if result.valid:
                result.message = "valid after correcting look-alike letters to digits"
        return result

    return FormatResult(
        raw=raw,
        cleaned=cleaned,
        kind="unknown",
        valid=False,
        formatted=None,
        expected_check_digit=None,
        message=f"got {length} characters after cleanup, expected 10, 12, or 13",
    )


def _format_isbn10(raw: str, cleaned: str) -> FormatResult:
    kind = "ISBN-10"
    if not cleaned[:9].isdigit() or cleaned[9] not in "0123456789X":
        return FormatResult(raw, cleaned, kind, False, None, None,
                             "first nine characters must be digits, last must be a digit or X")
    expected = checksum.isbn10_check_digit(cleaned[:9])
    valid = cleaned[9] == expected
    formatted = f"{cleaned[:9]}-{cleaned[9]}" if valid else None
    message = "valid" if valid else f"check digit is {cleaned[9]!r}, expected {expected!r}"
    return FormatResult(raw, cleaned, kind, valid, formatted, expected, message)


def _format_isbn13(raw: str, cleaned: str) -> FormatResult:
    kind = "ISBN-13" if cleaned.startswith(("978", "979")) else "EAN-13"
    if not cleaned.isdigit():
        return FormatResult(raw, cleaned, kind, False, None, None, "must be 13 digits")
    expected = checksum.isbn13_check_digit(cleaned[:12])
    valid = cleaned[12] == expected
    formatted = f"{cleaned[:12]}-{cleaned[12]}" if valid else None
    message = "valid" if valid else f"check digit is {cleaned[12]!r}, expected {expected!r}"
    return FormatResult(raw, cleaned, kind, valid, formatted, expected, message)


def _format_upca(raw: str, cleaned: str) -> FormatResult:
    kind = "UPC-A"
    if not cleaned.isdigit():
        return FormatResult(raw, cleaned, kind, False, None, None, "must be 12 digits")
    expected = checksum.upca_check_digit(cleaned[:11])
    valid = cleaned[11] == expected
    formatted = f"{cleaned[:11]}-{cleaned[11]}" if valid else None
    message = "valid" if valid else f"check digit is {cleaned[11]!r}, expected {expected!r}"
    return FormatResult(raw, cleaned, kind, valid, formatted, expected, message)
