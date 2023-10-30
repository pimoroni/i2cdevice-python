import pytest

from i2cdevice.adapter import Adapter, LookupAdapter, U16ByteSwapAdapter


def test_adaptor_class():
    adapter = Adapter()
    with pytest.raises(NotImplementedError):
        adapter._decode(0)
    with pytest.raises(NotImplementedError):
        adapter._encode(0)


def test_lookup_adapter():
    adapter = LookupAdapter({'Zero': 0, 'One': 1})
    assert adapter._decode(0) == 'Zero'
    assert adapter._decode(1) == 'One'
    with pytest.raises(ValueError):
        adapter._decode(2)
    with pytest.raises(KeyError):
        adapter._encode('Two')


def test_lookup_adapter_snap():
    adapter = LookupAdapter({0: 0, 1: 1})
    assert adapter._encode(0) == 0
    assert adapter._encode(1) == 1
    assert adapter._encode(0.1) == 0
    assert adapter._encode(0.9) == 1

    adapter = LookupAdapter({0: 0, 1: 0}, snap=False)
    with pytest.raises(KeyError):
        adapter._encode(0.1)


def test_byteswap_adapter():
    adapter = U16ByteSwapAdapter()
    assert adapter._encode(0xFF00) == 0x00FF
    assert adapter._decode(0x00FF) == 0xFF00
