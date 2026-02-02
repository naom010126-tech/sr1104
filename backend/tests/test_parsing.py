from app.services.metrics_extraction import parse_number


def test_parse_number_handles_commas_and_units():
    assert parse_number("1,234円") == 1234
    assert parse_number("55.12㎡") == 55.12
    assert parse_number("1.2%") == 1.2
    assert parse_number("3,000") == 3000


def test_parse_number_handles_fullwidth_and_units():
    assert parse_number("１,２００") == 1200
    assert parse_number("12,000円") == 12000
