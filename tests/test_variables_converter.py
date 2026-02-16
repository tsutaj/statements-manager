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
        assert result == "1000"

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

    def test_to_string_998244353_not_exponential(self):
        """Test that 998244353 is NOT converted to exponential notation (issue #236)"""
        config = MockStatementConfig(exponential_threshold=1000000)
        result = to_string(998244353, config, use_literal_digit_separator=False)
        # Should NOT be "9.98244353 × 10^8", should be formatted with digit separator
        assert result == "998{,}244{,}353"

    def test_to_string_998244353_custom_separator(self):
        """Test that 998244353 is NOT converted to exponential notation with custom separator"""
        config = MockStatementConfig(exponential_threshold=1000000)
        result = to_string(998244353, config, use_literal_digit_separator=True)
        assert result == "998,244,353"

    def test_to_string_number_ending_with_zeros_exponential(self):
        """Test that numbers ending with enough zeros ARE converted to exponential notation"""
        config = MockStatementConfig(exponential_threshold=1000000)
        # 10000000 ends with "0000000" which includes "000000", so it should be converted
        result = to_string(10000000, config, use_literal_digit_separator=False)
        assert result == "10^{7}"

    def test_to_string_number_ending_with_zeros_multiplier(self):
        """Test that numbers like 2*10^7 are converted correctly"""
        config = MockStatementConfig(exponential_threshold=1000000)
        result = to_string(20000000, config, use_literal_digit_separator=False)
        assert result == "2 \\times 10^{7}"

    def test_to_string_number_not_ending_with_enough_zeros(self):
        """Test that numbers not ending with enough zeros are NOT converted"""
        config = MockStatementConfig(exponential_threshold=1000000)
        # 1500000 ends with "500000", not "000000", so it should NOT be converted
        result = to_string(1500000, config, use_literal_digit_separator=False)
        assert result == "1{,}500{,}000"

    def test_to_string_negative_large_number_not_exponential(self):
        """Test that negative numbers not ending with zeros are NOT converted"""
        config = MockStatementConfig(exponential_threshold=1000000)
        result = to_string(-998244353, config, use_literal_digit_separator=False)
        assert result == "-998{,}244{,}353"

    def test_to_string_negative_power_of_ten(self):
        """Test that negative powers of ten ARE converted"""
        config = MockStatementConfig(exponential_threshold=1000000)
        result = to_string(-10000000, config, use_literal_digit_separator=False)
        assert result == "-10^{7}"

    def test_to_string_threshold_999999_same_as_1000000(self):
        config_999999 = MockStatementConfig(exponential_threshold=999999)
        config_1000000 = MockStatementConfig(exponential_threshold=1000000)
        test_values = [
            998244353,
            1000000007,
            10000000,
            20000000,
            1500000,
            -998244353,
            -10000000,
            1000000,
            2000000,
        ]
        for value in test_values:
            assert to_string(value, config_999999) == to_string(
                value, config_1000000
            ), f"Mismatch for value={value}"
