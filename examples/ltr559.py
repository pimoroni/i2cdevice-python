import sys
import time

sys.path.insert(0, "../")
from i2cdevice import BitField, Device, MockSMBus, Register  # noqa: E402
from i2cdevice.adapter import Adapter, LookupAdapter, U16ByteSwapAdapter  # noqa: E402

I2C_ADDR = 0x23


class Bit12Adapter(Adapter):
    def _encode(self, value):
        """
        Convert the 16-bit output into the correct format for reading:

            0bLLLLLLLLXXXXHHHH -> 0bHHHHLLLLLLLL
        """
        return ((value & 0xFF)) << 8 | ((value & 0xF00) >> 8)

    def _decode(self, value):
        """
        Convert the 12-bit input into the correct format for the registers,
        the low byte followed by 4 empty bits and the high nibble:

            0bHHHHLLLLLLLL -> 0bLLLLLLLLXXXXHHHH
        """
        return ((value & 0xFF00) >> 8) | ((value & 0x000F) << 8)


ltr559 = Device(I2C_ADDR, i2c_dev=MockSMBus(0, default_registers={0x86: 0x92}), bit_width=8, registers=(

    Register('ALS_CONTROL', 0x80, fields=(
        BitField('gain', 0b00011100, adapter=LookupAdapter({1: 0b000, 2: 0b001, 4: 0b011, 8: 0b011, 48: 0b110, 96: 0b111})),
        BitField('sw_reset', 0b00000010),
        BitField('mode', 0b00000001)
    )),

    Register('PS_CONTROL', 0x81, fields=(
        BitField('saturation_indicator_enable', 0b00100000),
        BitField('active', 0b00000011, adapter=LookupAdapter({False: 0b00, True: 0b11}))
    )),

    Register('PS_LED', 0x82, fields=(
        BitField('pulse_freq_khz', 0b11100000, adapter=LookupAdapter({30: 0b000, 40: 0b001, 50: 0b010, 60: 0b011, 70: 0b100, 80: 0b101, 90: 0b110, 100: 0b111})),
        BitField('duty_cycle', 0b00011000, adapter=LookupAdapter({0.25: 0b00, 0.5: 0b01, 0.75: 0b10, 1.0: 0b11})),
        BitField('current_ma', 0b00000111, adapter=LookupAdapter({5: 0b000, 10: 0b001, 20: 0b010, 50: 0b011, 100: 0b100}))
    )),

    Register('PS_N_PULSES', 0x83, fields=(
        BitField('count', 0b00001111),
    )),

    Register('PS_MEAS_RATE', 0x84, fields=(
        BitField('rate_ms', 0b00001111, adapter=LookupAdapter({10: 0b1000, 50: 0b0000, 70: 0b0001, 100: 0b0010, 200: 0b0011, 500: 0b0100, 1000: 0b0101, 2000: 0b0110})),
    )),

    Register('ALS_MEAS_RATE', 0x85, fields=(
        BitField('integration_time_ms', 0b00111000, adapter=LookupAdapter({100: 0b000, 50: 0b001, 200: 0b010, 400: 0b011, 150: 0b100, 250: 0b101, 300: 0b110, 350: 0b111})),
        BitField('repeat_rate_ms', 0b00000111, adapter=LookupAdapter({50: 0b000, 100: 0b001, 200: 0b010, 500: 0b011, 1000: 0b100, 2000: 0b101}))
    )),

    Register('PART_ID', 0x86, fields=(
        BitField('part_number', 0b11110000),  # Should be 0x09H
        BitField('revision', 0b00001111)  # Should be 0x02H
    ), read_only=True, volatile=False),

    Register('MANUFACTURER_ID', 0x87, fields=(
        BitField('manufacturer_id', 0b11111111),  # Should be 0x05H
    ), read_only=True),

    # This will address 0x88, 0x89, 0x8A and 0x8B as a continuous 32bit register
    Register('ALS_DATA', 0x88, fields=(
        BitField('ch1', 0xFFFF0000, bit_width=16, adapter=U16ByteSwapAdapter()),
        BitField('ch0', 0x0000FFFF, bit_width=16, adapter=U16ByteSwapAdapter())
    ), read_only=True, bit_width=32),

    Register('ALS_PS_STATUS', 0x8C, fields=(
        BitField('als_data_valid', 0b10000000),
        BitField('als_gain', 0b01110000, adapter=LookupAdapter({1: 0b000, 2: 0b001, 4: 0b010, 8: 0b011, 48: 0b110, 96: 0b111})),
        BitField('als_interrupt', 0b00001000),  # True = Interrupt is active
        BitField('als_data', 0b00000100),  # True = New data available
        BitField('ps_interrupt', 0b00000010),  # True = Interrupt is active
        BitField('ps_data', 0b00000001)  # True = New data available
    ), read_only=True),

    # The PS data is actually an 11bit value but since B3 is reserved it'll (probably) read as 0
    # We could mask the result if necessary
    Register('PS_DATA', 0x8D, fields=(
        BitField('ch0', 0xFF0F, adapter=Bit12Adapter()),
        BitField('saturation', 0x0080)
    ), bit_width=16, read_only=True),

    # INTERRUPT allows the interrupt pin and function behaviour to be configured.
    Register('INTERRUPT', 0x8F, fields=(
        BitField('polarity', 0b00000100),
        BitField('mode', 0b00000011, adapter=LookupAdapter({'off': 0b00, 'ps': 0b01, 'als': 0b10, 'als+ps': 0b11}))
    )),

    Register('PS_THRESHOLD', 0x90, fields=(
        BitField('upper', 0xFF0F0000, adapter=Bit12Adapter(), bit_width=16),
        BitField('lower', 0x0000FF0F, adapter=Bit12Adapter(), bit_width=16)
    ), bit_width=32),

    # PS_OFFSET defines the measurement offset value to correct for proximity
    # offsets caused by device variations, crosstalk and other environmental factors.
    Register('PS_OFFSET', 0x94, fields=(
        BitField('offset', 0x03FF),  # Last two bits of 0x94, full 8 bits of 0x95
    ), bit_width=16),

    # Defines the upper and lower limits of the "ALS" reading.
    # An interrupt is triggered if values fall outside of this range.
    # See also INTERRUPT_PERSIST.
    Register('ALS_THRESHOLD', 0x97, fields=(
        BitField('upper', 0xFFFF0000, adapter=U16ByteSwapAdapter(), bit_width=16),
        BitField('lower', 0x0000FFFF, adapter=U16ByteSwapAdapter(), bit_width=16)
    ), bit_width=32),

    # This register controls how many values must fall outside of the range defined
    # by upper and lower threshold limits before the interrupt is asserted.

    # In the case of both "PS" and "ALS", a 0 value indicates that every value outside
    # the threshold range should be counted.
    # Values therein map to n+1 , ie: 0b0001 requires two consecutive values.
    Register('INTERRUPT_PERSIST', 0x9E, fields=(
        BitField('PS', 0xF0),
        BitField('ALS', 0x0F)
    ))

))


if __name__ == "__main__":
    part_id = ltr559.get('PART_ID')

    assert part_id.part_number == 0x09
    assert part_id.revision == 0x02

    print("""
Found LTR-559.
Part ID: 0x{:02x}
Revision: 0x{:02x}
    """.format(
        part_id.part_number,
        part_id.revision
    ))

    print("""
Soft Reset
    """)
    ltr559.set('ALS_CONTROL', sw_reset=1)
    ltr559.set('ALS_CONTROL', sw_reset=0)
    try:
        while True:
            status = ltr559.get('ALS_CONTROL').sw_reset
            print("Status: {}".format(status))
            if status == 0:
                break
            time.sleep(1.0)
    except KeyboardInterrupt:
        pass

    print("Setting light sensor threshold")

    # The `set` method can handle writes to multiple register fields
    # specify each field value as a keyword argument
    ltr559.set('ALS_THRESHOLD',
                lower=0x0001,
                upper=0xFFEE)

    print("{:08x}".format(ltr559.values['ALS_THRESHOLD']))

    # The `get` method returns register values as an immutable
    # namedtuple, and fields will be available as properties
    # You must use `set` to write a register.
    als_threshold = ltr559.get('ALS_THRESHOLD')
    assert als_threshold.lower == 0x0001
    assert als_threshold.upper == 0xFFEE

    print("Setting PS threshold")

    ltr559.set('PS_THRESHOLD',
               lower=0,
               upper=500)

    print("{:08x}".format(ltr559.values['PS_THRESHOLD']))

    ps_threshold = ltr559.get('PS_THRESHOLD')
    assert ps_threshold.lower == 0
    assert ps_threshold.upper == 500

    print("Setting integration time and repeat rate")
    ltr559.set('PS_MEAS_RATE', rate_ms=100)
    ltr559.set('ALS_MEAS_RATE',
                integration_time_ms=50,
                repeat_rate_ms=50)

    als_meas_rate = ltr559.get('ALS_MEAS_RATE')
    assert als_meas_rate.integration_time_ms == 50
    assert als_meas_rate.repeat_rate_ms == 50

    print("""
Activating sensor
    """)

    ltr559.set('INTERRUPT', mode='als+ps')
    ltr559.set('PS_CONTROL',
               active=True,
               saturation_indicator_enable=1)

    ltr559.set('PS_LED',
               current_ma=50,
               duty_cycle=1.0,
               pulse_freq_khz=30)

    ltr559.set('PS_N_PULSES', count=1)

    ltr559.set('ALS_CONTROL',
               mode=1,
               gain=4)

    als_control = ltr559.get('ALS_CONTROL')
    assert als_control.mode == 1
    assert als_control.gain == 4

    ltr559.set('PS_OFFSET', offset=69)

    als0 = 0
    als1 = 0
    ps0 = 0
    lux = 0

    ch0_c = (17743, 42785, 5926, 0)
    ch1_c = (-11059, 19548, -1185, 0)

    try:
        while True:
            als_ps_status = ltr559.get('ALS_PS_STATUS')
            ps_int = als_ps_status.ps_interrupt or als_ps_status.ps_data
            als_int = als_ps_status.als_interrupt or als_ps_status.als_data

            if ps_int:
                ps0 = ltr559.get('PS_DATA').ch0

            if als_int:
                als_data = ltr559.get('ALS_DATA')
                als0 = als_data.ch0
                als1 = als_data.ch1

                ratio = 1000
                if als0 + als0 > 0:
                    ratio = (als0 * 1000) / (als1 + als0)

                ch_idx = 3
                if ratio < 450:
                    ch_idx = 0
                elif ratio < 640:
                    ch_idx = 1
                elif ratio < 850:
                    ch_idx = 2

                lux = ((als0 * ch0_c[ch_idx]) - (als1 * ch1_c[ch_idx])) / 10000

            print("Lux: {:06.2f}, Light CH0: {:04d}, Light CH1: {:04d}, Proximity: {:04d}  New Data LP: 0b{:01d}{:01d}".format(lux, als0, als1, ps0, als_int, ps_int))
            time.sleep(0.05)
    except KeyboardInterrupt:
        pass
