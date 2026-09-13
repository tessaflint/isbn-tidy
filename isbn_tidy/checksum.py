"""Check-digit math for ISBN-10, ISBN-13/EAN-13, and UPC-A.

All three schemes are simple weighted mod-N sums over the digits that
precede the check digit. UPC-A shares ISBN-13's algorithm once you treat
it as a 13-digit EAN with a leading zero, which is why it delegates here
instead of getting its own formula.
"""


def isbn10_check_digit(nine_digits: str) -> str:
    """Return the ISBN-10 check character (0-9 or 'X') for nine digits."""
    if len(nine_digits) != 9 or not nine_digits.isdigit():
        raise ValueError("isbn10_check_digit needs exactly 9 digits")
    total = sum((10 - i) * int(d) for i, d in enumerate(nine_digits))
    remainder = (11 - total % 11) % 11
    return "X" if remainder == 10 else str(remainder)


def isbn13_check_digit(twelve_digits: str) -> str:
    """Return the ISBN-13 / EAN-13 check digit for twelve digits."""
    if len(twelve_digits) != 12 or not twelve_digits.isdigit():
        raise ValueError("isbn13_check_digit needs exactly 12 digits")
    total = sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(twelve_digits))
    return str((10 - total % 10) % 10)


# EAN-13 uses the exact same weighting as ISBN-13; the name is kept
# separate so callers don't have to pretend a barcode is a book.
ean13_check_digit = isbn13_check_digit


def upca_check_digit(eleven_digits: str) -> str:
    """Return the UPC-A check digit for eleven digits."""
    if len(eleven_digits) != 11 or not eleven_digits.isdigit():
        raise ValueError("upca_check_digit needs exactly 11 digits")
    return isbn13_check_digit("0" + eleven_digits)


def validate_isbn10(candidate: str) -> bool:
    candidate = candidate.upper()
    if len(candidate) != 10 or not candidate[:9].isdigit():
        return False
    if candidate[9] not in "0123456789X":
        return False
    return isbn10_check_digit(candidate[:9]) == candidate[9]


def validate_isbn13(candidate: str) -> bool:
    if len(candidate) != 13 or not candidate.isdigit():
        return False
    return isbn13_check_digit(candidate[:12]) == candidate[12]


def validate_upca(candidate: str) -> bool:
    if len(candidate) != 12 or not candidate.isdigit():
        return False
    return upca_check_digit(candidate[:11]) == candidate[11]


def convert_isbn10_to_13(isbn10: str) -> str:
    """Rewrite a valid ISBN-10 as its ISBN-13 equivalent under the 978 prefix."""
    if not validate_isbn10(isbn10):
        raise ValueError("not a valid ISBN-10")
    core = "978" + isbn10.upper()[:9]
    return core + isbn13_check_digit(core)
