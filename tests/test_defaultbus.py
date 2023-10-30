from i2cdevice import MockSMBus, Device, Register, BitField
import sys


class SMBus():
    SMBus = MockSMBus


def test_smbus_io():
    sys.modules['smbus'] = SMBus
    device = Device(0x00, i2c_dev=None, registers=(
        Register('test', 0x00, fields=(
            BitField('test', 0xFF),
        )),
    ))
    del device
