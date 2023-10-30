import sys

from i2cdevice import BitField, Device, MockSMBus, Register


class SMBus():
    SMBus = MockSMBus


def test_smbus_io():
    sys.modules['smbus2'] = SMBus
    device = Device(0x00, i2c_dev=None, registers=(
        Register('test', 0x00, fields=(
            BitField('test', 0xFF),
        )),
    ))
    del device
