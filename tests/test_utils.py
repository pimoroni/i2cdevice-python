import pytest

from i2cdevice import _int_to_bytes, _leading_zeros, _mask_width, _trailing_zeros


def test_mask_width():
    assert _mask_width(0b111) == 3
    assert _mask_width(0b101) == 3
    assert _mask_width(0b0111) == 3
    assert _mask_width(0b1110) == 3


def test_leading_zeros():
    assert _leading_zeros(0b1) == 7
    assert _leading_zeros(0b10) == 6
    assert _leading_zeros(0b100) == 5
    assert _leading_zeros(0b100000000) == 8  # 9nth bit not counted by default


def test_trailing_zeros():
    assert _trailing_zeros(0b1) == 0
    assert _trailing_zeros(0b10) == 1
    assert _trailing_zeros(0b100) == 2
    assert _trailing_zeros(0b00000000) == 8  # Mask is all zeros


def test_int_to_bytes():
    assert _int_to_bytes(512, 2) == b'\x02\x00'
    assert _int_to_bytes(512, 2, endianness='little') == b'\x00\x02'
    assert _int_to_bytes(512, 2, endianness='big') == b'\x02\x00'

    with pytest.raises(TypeError):
        _int_to_bytes('', 2)
