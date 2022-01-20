import abc
import typing
import struct


class TypeConv(abc.ABC):
    @abc.abstractmethod
    def c2p(self, data: bytes, size: int) -> typing.Any:
        return None

    @property
    def size(self) -> int:
        """
        If the size of the type is constant, it returns a positive number.
        If not knowen, it returns 0.
        """
        return 0


class NativeConv(TypeConv):
    _decoder: struct.Struct = None

    def __init__(self, format: str) -> None:
        self._decoder = struct.Struct(format)

    def c2p(self, data: bytes, offset: int = 0) -> typing.Any:
        values = list(self._decoder.unpack_from(data, offset))
        return values[0]

    @property
    def size(self) -> int:
        return self._decoder.size


class CstringConv(TypeConv):
    def c2p(self, data: bytes, offset: int = 0) -> typing.Any:
        end = data.find(b"\x00", offset)
        return data[offset:end].decode()


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
