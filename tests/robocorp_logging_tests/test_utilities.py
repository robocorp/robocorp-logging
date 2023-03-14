def test_gen_id(data_regression):
    from robocorp_logging._impl import _gen_id

    iter_in = _gen_id()
    generated = []
    for _ in range(200):
        generated.append(next(iter_in))

    data_regression.check(generated)


def test_convert():
    from robocorp_logging import _convert_to_bytes

    assert _convert_to_bytes("100") == 100
    assert _convert_to_bytes("100kb") == 100000
    assert _convert_to_bytes("1mb") == 1e6
    assert _convert_to_bytes("0.1mb") == 1e5
