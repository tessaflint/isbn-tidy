from isbn_tidy import formatter


class TestClean:
    def test_strips_ascii_hyphens_and_spaces(self):
        assert formatter.clean("0 13 468599 x") == "013468599X"

    def test_strips_unicode_dashes(self):
        assert formatter.clean("978–16–148410‒5") == "978161484105"

    def test_strips_slashes_dots_underscores(self):
        assert formatter.clean("978.3/16_148410.5") == "9783161484105"

    def test_uppercases_check_letter(self):
        assert formatter.clean("013468599x") == "013468599X"

    def test_rejects_none(self):
        try:
            formatter.clean(None)
        except ValueError:
            pass
        else:
            raise AssertionError("expected ValueError")


class TestFormatIdentifierIsbn10:
    def test_valid(self):
        result = formatter.format_identifier("1-23-456789-X")
        assert result.kind == "ISBN-10"
        assert result.valid
        assert result.formatted == "123456789-X"

    def test_invalid_check_digit(self):
        result = formatter.format_identifier("1234567891")
        assert result.kind == "ISBN-10"
        assert not result.valid
        assert result.formatted is None
        assert result.expected_check_digit == "X"

    def test_non_digit_payload(self):
        result = formatter.format_identifier("01346859AX")
        assert result.kind == "ISBN-10"
        assert not result.valid
        assert result.expected_check_digit is None


class TestFormatIdentifierIsbn13:
    def test_valid_isbn13_prefix(self):
        result = formatter.format_identifier("978 1234567897")
        assert result.kind == "ISBN-13"
        assert result.valid
        assert result.formatted == "978123456789-7"

    def test_non_isbn_prefix_reported_as_ean13(self):
        result = formatter.format_identifier("4006381333931")
        assert result.kind == "EAN-13"
        assert result.valid

    def test_invalid_check_digit(self):
        result = formatter.format_identifier("978-3-16-148410-5")
        assert result.kind == "ISBN-13"
        assert not result.valid
        assert result.expected_check_digit == "0"


class TestFormatIdentifierUpca:
    def test_valid(self):
        result = formatter.format_identifier("1 23456 78901 2")
        assert result.kind == "UPC-A"
        assert result.valid
        assert result.formatted == "12345678901-2"

    def test_invalid_check_digit(self):
        result = formatter.format_identifier("123456789010")
        assert result.kind == "UPC-A"
        assert not result.valid
        assert result.expected_check_digit == "2"


class TestOcrConfusions:
    def test_letter_o_read_as_zero(self):
        result = formatter.format_identifier("O13468599X")
        assert result.valid
        assert result.ocr_fixed
        assert result.formatted == "013468599-X"
        assert "correcting" in result.message

    def test_lowercase_l_read_as_one(self):
        result = formatter.format_identifier("978l234567897")
        assert result.valid
        assert result.ocr_fixed
        assert result.cleaned == "9781234567897"

    def test_cyrillic_o_read_as_zero(self):
        result = formatter.format_identifier("978-3-16-148410-О")
        assert result.kind == "ISBN-13"
        assert result.ocr_fixed
        assert result.cleaned == "9783161484100"
        assert result.valid

    def test_clean_input_not_flagged(self):
        result = formatter.format_identifier("013468599X")
        assert result.valid
        assert not result.ocr_fixed

    def test_fix_does_not_bypass_checksum(self):
        result = formatter.format_identifier("978O234567891")
        assert not result.valid
        assert result.ocr_fixed
        assert result.expected_check_digit == "0"

    def test_unknown_length_left_alone(self):
        result = formatter.format_identifier("LOL")
        assert result.kind == "unknown"
        assert result.cleaned == "LOL"
        assert not result.ocr_fixed


class TestFormatIdentifierUnknownLength:
    def test_too_short(self):
        result = formatter.format_identifier("12345")
        assert result.kind == "unknown"
        assert not result.valid
        assert "5 characters" in result.message

    def test_empty_string(self):
        result = formatter.format_identifier("")
        assert result.kind == "unknown"
        assert not result.valid
