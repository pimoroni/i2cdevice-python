from i2cdevice import BitField, Device, MockSMBus, Register


def test_register_proxy():
    """This API pattern has been deprecated in favour of set/get."""
    bus = MockSMBus(1)
    device = Device(0x00, i2c_dev=bus, registers=(
        Register('test', 0x00, fields=(
            BitField('test', 0xFF),
        )),
    ))
    device.test.set_test(123)

    assert device.test.get_test() == 123

    assert bus.regs[0] == 123

    with device.test as test:
        test.set_test(77)
        test.write()

    assert device.test.get_test() == 77

    assert bus.regs[0] == 77

    assert device.test.read() == 77
