from i2cdevice import MockSMBus, Device, Register, BitField


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
