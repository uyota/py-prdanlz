# Copyright (c) 2022 Yoshihiro Ota <ota@j.email.ne.jp>
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

import typing
import struct


class TypeConv:
    def c2p(self, data: bytes, offset: int = 0) -> typing.Any:
        return data

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


byte = TypeConv()

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


TYPE2CONV = {
    "integer": int,
    "int": int,
    "unsigned int": uint,
    "uint": uint,
    "long integer": long,
    "long": long,
    "unsigned long": ulong,
    "ulong": ulong,
    "int8_t": int8,
    "uint8_t": uint8,
    "int16_t": int16,
    "uint16_t": uint16,
    "int32_t": int32,
    "uint32_t": uint32,
    "int64_t": int64,
    "uint64_t": uint64,
    "size_t": ulong,  # based on /usr/include/x86/_types.h
    "time_t": int,  # 8 bytes on all supported architectures except i386 per man arch
    "suseconds_t": long,
}
