from statements_manager.src.variables_converter import to_string


class MockStatementConfig:
    def __init__(self, digit_separator=",", exponential_threshold=1000000):
        self.digit_separator = digit_separator
        self.exponential_threshold = exponential_threshold


class TestToString:
    def test_to_string_non_custom_comma_separator(self):
        config = MockStatementConfig(digit_separator=",")
        result = to_string(1000, config, use_literal_digit_separator=False)
        assert result == "1{,}000"

    def test_to_string_non_custom_space_separator(self):
        config = MockStatementConfig(digit_separator=" ")
        result = to_string(1000, config, use_literal_digit_separator=False)
        assert result == "1\\\\,000"

    def test_to_string_non_custom_none_separator(self):
        config = MockStatementConfig(digit_separator="none")
        result = to_string(1000, config, use_literal_digit_separator=False)
        assert result == "1000"

    def test_to_string_custom_comma_separator(self):
        config = MockStatementConfig(digit_separator=",")
        result = to_string(1000, config, use_literal_digit_separator=True)
        assert result == "1,000"

    def test_to_string_custom_space_separator(self):
        config = MockStatementConfig(digit_separator=" ")
        result = to_string(1000, config, use_literal_digit_separator=True)
        assert result == "1 000"

    def test_to_string_custom_none_separator(self):
        config = MockStatementConfig(digit_separator="none")
        result = to_string(1000, config, use_literal_digit_separator=True)
        assert result == "1none000"

    def test_to_string_custom_custom_separator(self):
        config = MockStatementConfig(digit_separator="_")
        result = to_string(1000, config, use_literal_digit_separator=True)
        assert result == "1_000"

    def test_to_string_exponential_notation(self):
        config = MockStatementConfig(exponential_threshold=1000)
        result = to_string(1000000, config, use_literal_digit_separator=False)
        assert result == "10^{6}"

    def test_to_string_exponential_notation_custom(self):
        config = MockStatementConfig(exponential_threshold=1000)
        result = to_string(1000000, config, use_literal_digit_separator=True)
        assert result == "10^{6}"

    def test_to_string_non_integer(self):
        config = MockStatementConfig()
        result = to_string("test", config, use_literal_digit_separator=False)
        assert result == "test"

    def test_to_string_non_integer_custom(self):
        config = MockStatementConfig()
        result = to_string("test", config, use_literal_digit_separator=True)
        assert result == "test"

    def test_to_string_large_number_with_custom_separator(self):
        config = MockStatementConfig(
            digit_separator=",", exponential_threshold=10000000
        )
        result = to_string(1000000, config, use_literal_digit_separator=True)
        assert result == "1,000,000"

    def test_to_string_large_number_with_custom_separator_non_custom(self):
        config = MockStatementConfig(
            digit_separator=",", exponential_threshold=10000000
        )
        result = to_string(1000000, config, use_literal_digit_separator=False)
        assert result == "1{,}000{,}000"
