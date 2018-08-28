from i2cdevice import _mask_width, _leading_zeros, _trailing_zeros, _int_to_bytes


def test_mask_width():
    assert _mask_width(0b111) == 3
    assert _mask_width(0b101) == 3
    assert _mask_width(0b0111) == 3
    assert _mask_width(0b1110) == 3


def test_leading_zeros():
    assert _leading_zeros(0b1) == 7
    assert _leading_zeros(0b10) == 6
    assert _leading_zeros(0b100) == 5


def test_trailing_zeros():
    assert _trailing_zeros(0b1) == 0
    assert _trailing_zeros(0b10) == 1
    assert _trailing_zeros(0b100) == 2


def test_int_to_bytes():
    assert _int_to_bytes(512, 2) == b'\x02\x00'
    assert _int_to_bytes(512, 2, endianness='little') == b'\x00\x02'
