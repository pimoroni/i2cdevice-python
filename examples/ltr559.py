import sys
sys.path.insert(0, "../library/")
from i2cdevice import MockSMBus, Device, Register, BitField
from i2cdevice.adapter import Adapter, LookupAdapter, U16ByteSwapAdapter

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


ltr559 = Device(I2C_ADDR, i2c_dev=MockSMBus(1), bit_width=8, registers=(

    Register('ALS_CONTROL', 0x80, fields=(
        BitField('gain', 0b00011100, adapter=LookupAdapter({1: 0b000, 2: 0b001, 4: 0b011, 8:0b011, 48:0b110, 96:0b111})),
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
        BitField('integration_time_ms', 0b00111000, adapter=LookupAdapter({100: 0b000, 50: 0b001, 200: 0b010, 400: 0b011, 150: 0b100, 250: 0b101, 300: 0b110, 350: 0b111 })),
        BitField('repeat_rate_ms', 0b00000111, adapter=LookupAdapter({50: 0b000, 100: 0b001, 200: 0b010, 500: 0b011, 1000: 0b100, 2000: 0b101}))
    )),

    Register('PART_ID', 0x86, fields=(
        BitField('part_number', 0b11110000), # Should be 0x09H
        BitField('revision', 0b00001111) # Should be 0x02H
    ), read_only=True, volatile=False),

    Register('MANUFACTURER_ID', 0x87, fields=(
        BitField('manufacturer_id', 0b11111111), # Should be 0x05H
    ), read_only=True),

    # This will address 0x88, 0x89, 0x8A and 0x8B as a continuous 32bit register
    Register('ALS_DATA', 0x88, fields=(
        BitField('ch1', 0xFFFF0000, bit_width=16, adapter=U16ByteSwapAdapter()),
        BitField('ch0', 0x0000FFFF, bit_width=16, adapter=U16ByteSwapAdapter())
    ), read_only=True, bit_width=32),

    Register('ALS_PS_STATUS', 0x8C, fields=(
        BitField('als_data_valid', 0b10000000),
        BitField('als_gain', 0b01110000, adapter=LookupAdapter({1: 0b000, 2: 0b001, 4: 0b010, 8: 0b011, 48: 0b110, 96: 0b111})),
        BitField('als_interrupt', 0b00001000), # True = Interrupt is active
        BitField('als_data', 0b00000100), # True = New data available
        BitField('ps_interrupt', 0b00000010), # True = Interrupt is active
        BitField('ps_data', 0b00000001) # True = New data available
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
        BitField('upper', 0xFF0F0000, adapter=Bit12Adapter()),
        BitField('lower', 0x0000FF0F, adapter=Bit12Adapter())
    ), bit_width=32),

    # PS_OFFSET defines the measurement offset value to correct for proximity
    # offsets caused by device variations, crosstalk and other environmental factors.
    Register('PS_OFFSET', 0x94, fields=(
        BitField('offset', 0x03FF), # Last two bits of 0x94, full 8 bits of 0x95
    ), bit_width=16),

    # Defines the upper and lower limits of the ALS reading.
    # An interrupt is triggered if values fall outside of this range.
    # See also INTERRUPT_PERSIST.
    Register('ALS_THRESHOLD', 0x97, fields=(
        BitField('upper', 0xFFFF0000, adapter=U16ByteSwapAdapter()),
        BitField('lower', 0x0000FFFF, adapter=U16ByteSwapAdapter())
    ), bit_width=32),

    # This register controls how many values must fall outside of the range defined
    # by upper and lower threshold limits before the interrupt is asserted.

    # In the case of both PS and ALS, a 0 value indicates that every value outside
    # the threshold range should be counted.
    # Values therein map to n+1 , ie: 0b0001 requires two consecutive values.
    Register('INTERRUPT_PERSIST', 0x9E, fields=(
        BitField('PS', 0xF0),
        BitField('ALS', 0x0F)
    ))

))