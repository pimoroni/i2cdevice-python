from i2cdevice import MockSMBus


def test_smbus_io():
    bus = MockSMBus(1)
    bus.write_i2c_block_data(0x00, 0x00, [0xff, 0x00, 0xff])
    assert bus.read_i2c_block_data(0x00, 0x00, 3) == [0xff, 0x00, 0xff]
