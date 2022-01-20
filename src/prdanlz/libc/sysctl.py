import ctypes
import typing

from .libc import libc
from . import tconv

CTL_SYSCTL = 0

# /usr/include/sys/sysctl.h
CTLTYPE_NODE = 1
CTLTYPE_INT = 2
CTLTYPE_STRING = 3
CTLTYPE_S64 = 4
CTLTYPE_OPAQUE = 5
CTLTYPE_STRUCT = CTLTYPE_OPAQUE
CTLTYPE_UINT = 6
CTLTYPE_LONG = 7
CTLTYPE_ULONG = 8
CTLTYPE_U64 = 9
CTLTYPE_U8 = 0xA
CTLTYPE_U16 = 0xB
CTLTYPE_S8 = 0xC
CTLTYPE_S16 = 0xD
CTLTYPE_S32 = 0xE
CTLTYPE_U32 = 0xF

TYPE2TCONV = {
    CTLTYPE_INT: tconv.int,
    CTLTYPE_STRING: tconv.cstr,
    CTLTYPE_S64: tconv.int16,
    CTLTYPE_UINT: tconv.uint,
    CTLTYPE_LONG: tconv.long,
    CTLTYPE_ULONG: tconv.ulong,
    CTLTYPE_U64: tconv.uint64,
    CTLTYPE_U8: tconv.uint8,
    CTLTYPE_U16: tconv.uint16,
    CTLTYPE_S8: tconv.int8,
    CTLTYPE_S16: tconv.int16,
    CTLTYPE_S32: tconv.int32,
    CTLTYPE_U32: tconv.uint32,
}

BUF_TYPE = ctypes.c_char * 1024  # 1024 is BUFSIZE in stdio.h


def pysysctl(
    oid: typing.List[int], oldp: typing.Any, oldlenp, newp: ctypes.c_char_p
) -> bool:
    oid_len = len(oid)
    qoid_type = ctypes.c_uint * oid_len
    qoid = (qoid_type)(*oid)
    p_qoid = ctypes.POINTER(qoid_type)(qoid)
    l = len(newp.value) if newp else 0
    return libc.sysctl(p_qoid, oid_len, oldp, oldlenp, newp, l) == 0


def name2oid(name: str) -> typing.List[int]:
    p_name = ctypes.c_char_p(name.encode())

    length = ctypes.c_int(name2oid.NAME_TYPE.value * ctypes.sizeof(ctypes.c_int))
    p_length = ctypes.POINTER(ctypes.c_int)(length)

    Res = ctypes.c_int * length.value
    res = (Res)()

    rc = pysysctl(name2oid.opr, ctypes.POINTER(Res)(res), p_length, p_name)
    if not rc:
        raise RuntimeError(f"Invalid sysctl name: '{name}'")

    oid_length = int(length.value / ctypes.sizeof(ctypes.c_int))
    return res[:oid_length]


name2oid.NAME_TYPE = ctypes.c_uint(24)
name2oid.opr = [CTL_SYSCTL, 3]  # CTL_SYSCTL_NAME2OID


def oidfmt(mib: typing.List[int]) -> typing.Tuple[int, str]:
    buf = BUF_TYPE()
    p_buf = ctypes.POINTER(BUF_TYPE)(buf)
    buf_void = ctypes.cast(p_buf, ctypes.c_void_p)

    buf_length = ctypes.sizeof(buf)
    p_buf_length = ctypes.POINTER(ctypes.c_int)(ctypes.c_int(buf_length))

    pysysctl(oidfmt.opr + mib, buf_void, p_buf_length, 0)

    pbuf = buf[:buf_length]  # c_char_Array to bytes
    return (tconv.uint.c2p(pbuf), tconv.cstr.c2p(pbuf[4:]))


oidfmt.opr = [CTL_SYSCTL, 4]  # CTL_SYSCTL_OIDFMT


def oiddesc(mib: typing.List[int]) -> str:
    buf = BUF_TYPE()
    p_buf = ctypes.POINTER(BUF_TYPE)(buf)
    buf_void = ctypes.cast(p_buf, ctypes.c_void_p)

    buf_length = ctypes.sizeof(buf)
    p_buf_length = ctypes.POINTER(ctypes.c_int)(ctypes.c_int(buf_length))

    pysysctl(oiddesc.opr + mib, buf_void, p_buf_length, None)
    return buf.value.decode()


oiddesc.opr = [CTL_SYSCTL, 5]  # CTL_SYSCTL_OIDDESCR


def oidsize(mib: typing.List[int]) -> int:
    len = ctypes.c_long()
    pysysctl(mib, None, ctypes.byref(len), None)
    return len.value


def oidvalue(oid: typing.List[int], buflen: int) -> bytes:
    buf_type = ctypes.c_char * buflen
    buf = buf_type()
    p_buf = ctypes.POINTER(buf_type)(buf)
    p_buf_void = ctypes.cast(p_buf, ctypes.c_void_p)

    buf_length = ctypes.sizeof(buf)
    p_buf_length = ctypes.POINTER(ctypes.c_int)(ctypes.c_int(buf_length))

    pysysctl(oid, p_buf_void, p_buf_length, None)

    return buf[:buf_length]  # c_char_Array to bytes


class Sysctl:
    def __init__(self, name: str) -> None:
        self._name: str = name
        self._mib: typing.List[int] = name2oid(name)
        self._kind: typing.Optional[int] = None
        self._fmt: typing.Optional[str] = None
        self._tconv: typing.Optional[tconv.TypeConv] = None
        self._buflen: typing.Optional[int] = None
        self._description: typing.Optional[str] = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def kind(self) -> int:
        if self._kind is None:
            self._kind, self._fmt = oidfmt(self._mib)
        return self._kind

    @property
    def type(self) -> int:
        return self.kind & 0xF

    @property
    def fmt(self) -> int:
        if self._fmt is None:
            self._kind, self._fmt = oidfmt(self._mib)
        return self._fmt

    def _conv(self) -> tconv.TypeConv:
        if self._tconv is None:
            self._tconv = TYPE2TCONV.get(self.type, None)
            # TODO assert self._tconv
        return self._tconv

    @property
    def raw_value(self) -> bytes:
        buflen = self._reserve()
        return oidvalue(self._mib, buflen)

    @property
    def value(self) -> typing.Any:
        return self._conv().c2p(self.raw_value)

    @property
    def description(self) -> str:
        if self._description is None:
            self._description = oiddesc(self._mib)
        return self._description

    def _reserve(self) -> int:
        if self._buflen is None:
            self._buflen = self._conv().size
            if self._buflen == 0:
                self._buflen = 2 * oidsize(self._mib)
        return self._buflen
