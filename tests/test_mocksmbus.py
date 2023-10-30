from i2cdevice import MockSMBus


def test_smbus_io():
    bus = MockSMBus(1)
    bus.write_i2c_block_data(0x00, 0x00, [0xff, 0x00, 0xff])
    assert bus.read_i2c_block_data(0x00, 0x00, 3) == [0xff, 0x00, 0xff]


def test_smbus_default_regs():
    bus = MockSMBus(1, default_registers={0x60: 0x99, 0x88: 0x51})
    assert bus.read_i2c_block_data(0x00, 0x60, 1) == [0x99]
    assert bus.read_i2c_block_data(0x00, 0x88, 1) == [0x51]
