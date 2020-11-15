from i2cdevice import MockSMBus, Device, Register, BitField
from i2cdevice.adapter import LookupAdapter
import pytest


def test_bank_select():
    bus = MockSMBus(1, bank_select_register=0x00, banks=2)
    device = Device(0x00, i2c_dev=bus, registers=(
        Register('one', 0x01, bank=0, fields=(
            BitField('value', 0xFF),
        )),
        Register('two', 0x01, bank=1, fields=(
            BitField('value', 0xFF),
        )),
    ), bank_select=Register('bank', 0x00))

    device.set('one', value=111)
    assert bus.bank == 0

    device.set('two', value=222)
    assert bus.bank == 1

    assert device.get('two').value == 222
    assert bus.regs[1][1] == 222
    assert bus.bank == 1

    assert device.get('one').value == 111
    assert bus.regs[0][1] == 111
    assert bus.bank == 0



