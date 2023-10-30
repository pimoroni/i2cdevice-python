import pytest

from i2cdevice import BitField, Device, MockSMBus, Register
from i2cdevice.adapter import LookupAdapter


def test_set_regs():
    bus = MockSMBus(1)
    device = Device(0x00, i2c_dev=bus, registers=(
        Register('test', 0x00, fields=(
            BitField('test', 0xFF),
        )),
    ))
    device.set('test', test=123)

    assert device.get('test').test == 123

    assert bus.regs[0] == 123


def test_get_regs():
    bus = MockSMBus(1)
    device = Device(0x00, i2c_dev=bus, registers=(
        Register('test', 0x00, fields=(
            BitField('test', 0xFF00),
            BitField('monkey', 0x00FF),
        ), bit_width=16),
    ))
    device.set('test', test=0x66, monkey=0x77)

    reg = device.get('test')
    reg.test == 0x66
    reg.monkey == 0x77

    assert bus.regs[0] == 0x66
    assert bus.regs[1] == 0x77


def test_field_name_in_adapter_error():
    bus = MockSMBus(1)
    device = Device(0x00, i2c_dev=bus, registers=(
        Register('test', 0x00, fields=(
            BitField('test', 0xFF00, adapter=LookupAdapter({'x': 1})),
        ), bit_width=16),
    ))

    with pytest.raises(ValueError) as e:
        reg = device.get('test')
        assert 'test' in e
        del reg
