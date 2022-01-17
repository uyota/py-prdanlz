import abc
import typing
import struct


class TypeConv(abc.ABC):
    @abc.abstractmethod
    def c2p(self, data: bytes, size: int) -> typing.Any:
        return None


class NativeConv(TypeConv):
    _decoder: struct.Struct = None

    def __init__(self, format: str) -> None:
        self._decoder = struct.Struct(format)

    def c2p(self, data: bytes, offset: int = 0) -> typing.Any:
        values = list(self._decoder.unpack_from(data, offset))
        return values[0]


class CstringConv(TypeConv):
    def c2p(self, data: bytes, offset: int = 0) -> typing.Any:
        if offset:
            return data[offset:].decode()
        else:
            return data.decode()


int = NativeConv("i")
uint = NativeConv("I")
long = NativeConv("l")
ulong = NativeConv("L")

int8 = NativeConv("b")
uint8 = NativeConv("B")
int16 = NativeConv("h")
uint16 = NativeConv("H")
int32 = int
uint32 = uint
int64 = NativeConv("q")
uint64 = NativeConv("Q")

cstr = CstringConv()
