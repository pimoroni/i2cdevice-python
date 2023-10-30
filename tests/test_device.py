import pytest

from i2cdevice import BitField, BitFlag, Device, MockSMBus, Register
from i2cdevice.adapter import U16ByteSwapAdapter


def test_register_locking():
    bus = MockSMBus(1)
    device = Device(0x00, i2c_dev=bus, registers=(
        Register('test', 0x00, fields=(
            BitField('test', 0xFF),
        )),
    ))

    device.test.set_test(77)
    device.lock_register('test')

    bus.regs[0] = 11
    assert device.test.get_test() == 77

    device.unlock_register('test')
    assert device.test.get_test() == 11


def test_adapters():
    bus = MockSMBus(1)
    device = Device(0x00, i2c_dev=bus, registers=(
        Register('adapter', 0x01, fields=(
            BitField('test', 0xFFFF, adapter=U16ByteSwapAdapter()),
        )),
    ))

    device.adapter.set_test(0xFF00)

    assert device.adapter.get_test() == 0xFF00

    assert bus.regs[0:2] == [0x00, 0xFF]


def test_address_select():
    bus = MockSMBus(1)
    device = Device([0x00, 0x01], i2c_dev=bus, registers=(
        Register('test', 0x00, fields=(
            BitField('test', 0xFF),
        )),
    ))

    assert device.get_addresses() == [0x00, 0x01]
    assert device.select_address(0x01) is True
    with pytest.raises(ValueError):
        device.select_address(0x02)

    assert device.next_address() == 0x00
    assert device.next_address() == 0x01


def test_get_set_field():
    bus = MockSMBus(1)
    device = Device([0x00, 0x01], i2c_dev=bus, registers=(
        Register('test', 0x00, fields=(
            BitField('test', 0xFF),
        )),
    ))

    device.set_field('test', 'test', 99)

    assert device.get_field('test', 'test') == 99

    assert bus.regs[0] == 99


def test_get_set_field_overflow():
    bus = MockSMBus(1)
    device = Device([0x00, 0x01], i2c_dev=bus, registers=(
        Register('test', 0x00, fields=(
            BitField('test', 0xFF),
        )),
    ))

    device.set_field('test', 'test', 9999999)

    assert device.get_field('test', 'test') == 127

    assert bus.regs[0] == 127


def test_bitflag():
    bus = MockSMBus(1)
    device = Device([0x00, 0x01], i2c_dev=bus, registers=(
        Register('test', 0x00, fields=(
            BitFlag('test', 6),  # Sixth bit from the right
        )),
    ))

    device.test.set_test(True)

    assert bus.regs[0] == 0b01000000

    device.test.set_test(False)

    assert bus.regs[0] == 0b00000000


def test_get_register():
    bus = MockSMBus(1)
    bus.regs[0:3] = [0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF]
    device = Device([0x00, 0x01], i2c_dev=bus, registers=(
        Register('test24', 0x00, fields=(
            BitField('test', 0xFFF),
        ), bit_width=24),
        Register('test32', 0x00, fields=(
            BitField('test', 0xFFF),
        ), bit_width=32),
        Register('test48', 0x00, fields=(
            BitField('test', 0xFFF),
        ), bit_width=48),
    ))

    assert device.get_register('test24') == 0xAABBCC

    assert device.get_register('test32') == 0xAABBCCDD

    assert device.get_register('test48') == 0xAABBCCDDEEFF


def test_missing_regiser():
    bus = MockSMBus(1)
    device = Device([0x00, 0x01], i2c_dev=bus, registers=(
        Register('test', 0x00, fields=(
            BitFlag('test', 6),  # Sixth bit from the right
        )),
    ))

    with pytest.raises(KeyError):
        device.get_register('foo')
