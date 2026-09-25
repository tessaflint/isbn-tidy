import pytest

from isbn_tidy import checksum


class TestIsbn10CheckDigit:
    def test_check_digit_is_x(self):
        assert checksum.isbn10_check_digit("123456789") == "X"

    def test_check_digit_is_a_plain_digit(self):
        assert checksum.isbn10_check_digit("111111111") == "1"

    def test_rejects_wrong_length(self):
        with pytest.raises(ValueError):
            checksum.isbn10_check_digit("12345678")

    def test_rejects_non_digits(self):
        with pytest.raises(ValueError):
            checksum.isbn10_check_digit("12345678X")


class TestIsbn13CheckDigit:
    def test_known_value(self):
        assert checksum.isbn13_check_digit("978123456789") == "7"

    def test_rejects_wrong_length(self):
        with pytest.raises(ValueError):
            checksum.isbn13_check_digit("97812345678")

    def test_rejects_non_digits(self):
        with pytest.raises(ValueError):
            checksum.isbn13_check_digit("97812345678X")

    def test_ean13_alias_matches(self):
        assert checksum.ean13_check_digit("978123456789") == checksum.isbn13_check_digit(
            "978123456789"
        )


class TestUpcaCheckDigit:
    def test_known_value(self):
        assert checksum.upca_check_digit("12345678901") == "2"

    def test_rejects_wrong_length(self):
        with pytest.raises(ValueError):
            checksum.upca_check_digit("1234567890")

    def test_rejects_non_digits(self):
        with pytest.raises(ValueError):
            checksum.upca_check_digit("1234567890A")


class TestValidateIsbn10:
    def test_valid_with_x_check_digit(self):
        assert checksum.validate_isbn10("123456789X")

    def test_valid_lowercase_x(self):
        assert checksum.validate_isbn10("123456789x")

    def test_invalid_check_digit(self):
        assert not checksum.validate_isbn10("1234567891")

    def test_wrong_length(self):
        assert not checksum.validate_isbn10("123456789")

    def test_non_digit_payload(self):
        assert not checksum.validate_isbn10("12345678AX")


class TestValidateIsbn13:
    def test_valid(self):
        assert checksum.validate_isbn13("9781234567897")

    def test_invalid_check_digit(self):
        assert not checksum.validate_isbn13("9781234567890")

    def test_wrong_length(self):
        assert not checksum.validate_isbn13("978123456789")

    def test_non_digit_payload(self):
        assert not checksum.validate_isbn13("978123456789X")


class TestValidateUpca:
    def test_valid(self):
        assert checksum.validate_upca("123456789012")

    def test_invalid_check_digit(self):
        assert not checksum.validate_upca("123456789010")

    def test_wrong_length(self):
        assert not checksum.validate_upca("12345678901")


class TestConvertIsbn10To13:
    def test_known_conversion(self):
        assert checksum.convert_isbn10_to_13("123456789X") == "9781234567897"

    def test_rejects_invalid_isbn10(self):
        with pytest.raises(ValueError):
            checksum.convert_isbn10_to_13("1234567891")
