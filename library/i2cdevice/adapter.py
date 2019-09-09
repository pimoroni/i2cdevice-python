class Adapter:
    """
    Must implement `_decode()` and `_encode()`.
    """
    def _decode(self, value):
        raise NotImplementedError

    def _encode(self, value):
        raise NotImplementedError


class LookupAdapter(Adapter):
    """Adaptor with a dictionary of values.

    :param lookup_table: A dictionary of one or more key/value pairs where the key is the human-readable value and the value is the bitwise register value

    """
    def __init__(self, lookup_table, snap=True):
        self.lookup_table = lookup_table
        self.snap = snap

    def _decode(self, value):
        for k, v in self.lookup_table.items():
            if v == value:
                return k
        raise ValueError("{} not in lookup table".format(value))

    def _encode(self, value):
        if self.snap and type(value) in [int, float]:
            value = min(list(self.lookup_table.keys()), key=lambda x: abs(x - value))
        return self.lookup_table[value]


class U16ByteSwapAdapter(Adapter):
    """Adaptor to swap the bytes in a 16bit integer."""
    def _byteswap(self, value):
        return (value >> 8) | ((value & 0xFF) << 8)

    def _decode(self, value):
        return self._byteswap(value)

    def _encode(self, value):
        return self._byteswap(value)
