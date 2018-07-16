from i2cdevice import MockSMBus, Device, Register, BitField
from i2cdevice.adapter import Adapter, LookupAdapter

class x2Adapter(Adapter):
    def _decode(self, value):
        return value >> 1

    def _encode(self, value):
        return value << 1

bus = MockSMBus(1)

device = Device(0x00, bus, registers=(
    Register('status', 0x00, fields=(
        BitField('interrupt',  0b00000001, read_only=True),
        BitField('data_ready', 0b00000010),
        BitField('power',      0b10000000),
        BitField('monkey',     0b01111100, adapter=x2Adapter())
    )),
    Register('measurement_rate', 0x85, fields=(
        BitField('integration_time_ms', 0b00111000, adapter=LookupAdapter({100: 0b000, 50: 0b001, 200: 0b010, 400: 0b011, 150: 0b100, 250: 0b101, 300: 0b110, 350: 0b111 })),
        BitField('repeat_rate_ms', 0b00000111, adapter=LookupAdapter({50: 0b000, 100: 0b001, 200: 0b010, 500: 0b011, 1000: 0b100, 2000: 0b101}))
    ))
))

device.set_field('status', 'power', False)
print(device.get_field('status','power'))
print(device.get_register('status'))
print(bus.regs[0])

device.set_field('status', 'power', True)
print(device.get_field('status', 'power'))
print(device.get_register('status'))
print(bus.regs[0])

print("Testing measurement_rate->integration_time_ms")
device.set_field('measurement_rate', 'integration_time_ms', 200)
print("{:08b}".format(bus.regs[0x85]))
assert device.get_field('measurement_rate', 'integration_time_ms') == 200

print("Object set", device.measurement_rate.set_integration_time_ms(400))
print("{:08b}".format(bus.regs[0x85]))
print("Object get", device.measurement_rate.get_integration_time_ms())

device.set_field('status', 'monkey', 1)
print("{:08b}".format(bus.regs[0]))
assert device.get_field('status', 'monkey') == 1

device.set_field('status', 'monkey', 2)
print("{:08b}".format(bus.regs[0]))
assert device.get_field('status', 'monkey') == 2

device.set_field('status', 'monkey', 3)
print("{:08b}".format(bus.regs[0]))
assert device.get_field('status', 'monkey') == 3