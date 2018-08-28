# i2cdevice

[![Build Status](https://travis-ci.com/pimoroni/i2cdevice-python.svg?branch=master)](https://travis-ci.com/pimoroni/i2cdevice-python)

i2cdevice is a python domain-specific language aimed at dealing with common SMBus/i2c device interaction patterns.

This project aims to make group-up implementations of Python libraries for i2c devices easier, simpler and inherently self-documenting.

It does this by separating a detailed description of the hardware registers and how they should be manipulated into a stuctured definition language.

This project does not aim to help you make a public API for Python devices- that should be built on top of the fundamentals presented here.

# Using This Library

You should generally aim for a 1:1 representation of the hardware registers in the device you're implementing, even if you don't plan to use all the functionality. Having the full register set implemented allows for the easy addition of new features in future.

Checkout the libraries listed below for real-world examples.

# Features

* Classes for describing devices, registers and individual bit fields within registers in a fashion which maps closely with the datasheet
* Value translation from real world numbers (such as `512ms`) to register values (such as `0b111`) and back again
* Automatic generation of accessors for every BitField- add a `mode` field and you'll get `get_mode` and `set_mode` methods on your Register.
* Support for treating multiple-bytes as a single value, or single register with multiple values

# Built With i2cdevice

* bh1745 - https://github.com/pimoroni/bh1745-python
* as7262 - https://github.com/pimoroni/as7262-python
* lsm303d - https://github.com/pimoroni/lsm303d-python
* ltr559 - https://github.com/pimoroni/ltr559-python

# Examples

The below example defines the `ALS_CONTROL` register on an ltr559, with register address `0x80`.

It has 3 fields; gain - which is mapped to real world values - and sw_reset/mode which are single bit flags.

```python
ALS_CONTROL = Register('ALS_CONTROL', 0x80, fields=(
    BitField('gain', 0b00011100, values_map={1: 0b000, 2: 0b001, 4: 0b011, 8:0b011, 48:0b110, 96:0b111}),
    BitField('sw_reset', 0b00000010),
    BitField('mode', 0b00000001)
))
```

A lookup table is not required for values, however, a function can be used to translate values from and to a format that the device understands.

The below example uses `i2cdevice._byte_swap` to change the endianness of two 16bit values before they are stored/retrieved.

```python
# This will address 0x88, 0x89, 0x8A and 0x8B as a continuous 32bit register
ALS_DATA = Register('ALS_DATA', 0x88, fields=(
    BitField('ch1', 0xFFFF0000, bitwidth=16, values_in=_byte_swap, values_out=_byte_swap),
    BitField('ch0', 0x0000FFFF, bitwidth=16, values_in=_byte_swap, values_out=_byte_swap)
), read_only=True, bitwidth=32)
```

A "Register" and its "BitField"s define a set of rules and logic for detailing with the hardware register which is intepreted by the device class. Registers are declared on a device using the `registers=()` keyword argument:

```python
I2C_ADDR = 0x23
ltr559 = Device(I2C_ADDR, bit_width=8, registers=(
	ALS_CONTROL,
	ALS_DATA
))
```

