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

import ctypes
import struct
import time
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

"""
sysctl system call related functions
"""


def pysysctl(
    oid: typing.List[int],
    oldp: typing.Any,
    oldlenp,
    newp: typing.Optional[ctypes.c_char_p],
) -> bool:
    oid_len = len(oid)
    qoid_type = ctypes.c_uint * oid_len
    qoid = (qoid_type)(*oid)
    p_qoid = ctypes.POINTER(qoid_type)(qoid)
    l = len(newp.value) if newp else 0
    return libc.sysctl(p_qoid, oid_len, oldp, oldlenp, newp, l) == 0


def pysysctlnametomib(name: str) -> typing.Optional[typing.List[int]]:
    p_name = ctypes.c_char_p(name.encode())

    mib_type = ctypes.c_int * 16  # from swapctl
    mib = (mib_type)()
    p_mib = ctypes.POINTER(ctypes.c_int)(mib)

    length = ctypes.c_size_t(16)
    p_length = ctypes.POINTER(ctypes.c_size_t)(length)

    if libc.sysctlnametomib(p_name, p_mib, p_length) == -1:
        return None
    return mib[: length.value]  # c_int_Array to List[int]


def name2oid(name: str) -> typing.List[int]:
    p_name = ctypes.c_char_p(name.encode())

    length = ctypes.c_int(name2oid.NAME_TYPE.value * ctypes.sizeof(ctypes.c_int))
    p_length = ctypes.POINTER(ctypes.c_int)(length)

    res_type = ctypes.c_int * length.value
    res = (res_type)()
    p_res = ctypes.POINTER(res_type)(res)

    if not pysysctl(name2oid.opr, p_res, p_length, p_name):
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

    len = ctypes.c_long(buflen)

    if not pysysctl(oid, p_buf_void, ctypes.byref(len), None):
        raise RuntimeError(f"Invalid sysctl mib: '{oid}'")

    return buf[: len.value]  # c_char_Array to bytes


"""
sysctl Structure conversion
"""

CLOCKINFO = [
    ("int", "hz"),  #             /* clock frequency */
    ("int", "tick"),  #           /* micro-seconds per hz tick */
    ("int", ""),
    ("int", "stathz"),  #         /* statistics clock frequency */
    ("int", "profhz"),  #         /* profiling clock frequency */
]

LOADAVG = [
    ("uint32_t", "1min"),
    ("uint32_t", "3min"),
    ("uint32_t", "15min"),
    ("long", "scale"),
]

TIMEVAL = [
    ("time_t", "sec"),  #       /* seconds */
    ("suseconds_t", "usec"),  # /* and microseconds */
]

VMTOTAL = [
    ("uint64_t", "t_vm"),  #     /* total virtual memory */
    ("uint64_t", "t_avm"),  #    /* active virtual memory */
    ("uint64_t", "t_rm"),  #     /* total real memory in use */
    ("uint64_t", "t_arm"),  #    /* active real memory */
    ("uint64_t", "t_vmshr"),  #  /* shared virtual memory */
    ("uint64_t", "t_avmshr"),  # /* active shared virtual memory */
    ("uint64_t", "t_rmshr"),  #  /* shared real memory */
    ("uint64_t", "t_armshr"),  # /* active shared real memory */
    ("uint64_t", "t_free"),  #   /* free memory pages */
    ("int16_t", "t_rq"),  #      /* length of the run queue */
    ("int16_t", "t_dw"),  #      /* threads in ``disk wait'' (neg priority) */
    ("int16_t", "t_pw"),  #      /* threads in page wait */
    ("int16_t", "t_sl"),  #      /* threads sleeping in core */
    ("int16_t", "t_sw"),  #      /* swapped out runnable/short block threads */
]

INPUT_ID = [
    ("uint16_t", "bustype"),
    ("uint16_t", "vendor"),
    ("uint16_t", "product"),
    ("uint16_t", "version"),
]

# bios_smap_xattr in /usr/include/machine/pc/bios.h
BIOS_SMAP_XATTR = [
    ("u_int64_t", "base"),
    ("u_int64_t", "length"),
    ("u_int32_t", "type"),
    ("u_int32_t", "xattr"),
]

# efi_map_header in /usr/include/x86/metadata.h
# EFI_MAP_HEADER


def optimize(
    mapping: typing.List[typing.Tuple[str, str]]
) -> typing.List[typing.Tuple[tconv.TypeConv, str]]:
    return [(tconv.TYPE2CONV[i[0]], i[1]) for i in mapping]


class DictConv(tconv.TypeConv):
    _sizeof = None

    def __init__(self, mapping: typing.List[typing.Tuple[tconv.TypeConv, str]]) -> None:
        self._mapping = mapping

    def c2p(self, data: bytes, offset: int = 0) -> typing.Any:
        if self._mapping is None:
            return data
        value = {}
        start = offset
        for (conv, name) in self._mapping:
            if name != "":
                value[name] = conv.c2p(data, start)
            start += conv.size
        return value

    @property
    def sizeof(self) -> int:
        """
        The size of the C-struct with padding considered
        """
        if DictConv._sizeof is None:
            fmts = [nconv._decoder.format for (nconv, name) in self._mapping]
            DictConv._sizeof = struct.Struct("".join(fmts)).size
        return DictConv._sizeof


class LoadavgConv(DictConv):
    _mapping = optimize(LOADAVG)

    def __init__(self) -> None:
        super().__init__(LoadavgConv._mapping)

    def c2p(self, data: bytes, offset: int = 0) -> typing.Any:
        map = super().c2p(data)
        scale = float(map["scale"])
        return (map["1min"] / scale, map["3min"] / scale, map["15min"] / scale)


class TimevalConv(DictConv):
    _mapping = optimize(TIMEVAL)

    def __init__(self) -> None:
        super().__init__(TimevalConv._mapping)

    def c2p(self, data: bytes, offset: int = 0) -> typing.Any:
        t = super().c2p(data)
        return (t, time.ctime(t["sec"]))


class PagesizesConv(tconv.TypeConv):
    def c2p(self, data: bytes, offset: int = 0) -> typing.Any:
        num = int(len(data) / tconv.long.size)
        l = []
        for i in range(num):
            l.append(tconv.long.c2p(data, offset))
            offset += tconv.long.size
        return l


class SmapConv(tconv.TypeConv):
    _smapconv = None
    _sizeof = None

    def __init__(self) -> None:
        if SmapConv._smapconv is None:
            SmapConv._smapconv = DictConv(optimize(BIOS_SMAP_XATTR))
            SmapConv._sizeof = SmapConv._smapconv.sizeof

    def c2p(self, data: bytes, offset: int = 0) -> typing.Any:
        smap = []
        while offset < len(data):
            smap.append(SmapConv._smapconv.c2p(data, offset))
            offset += SmapConv._sizeof
        return smap


clockinfo = DictConv(optimize(CLOCKINFO))
loadavg = LoadavgConv()
timeval = TimevalConv()
vmtotal = DictConv(optimize(VMTOTAL))
pagesizes = PagesizesConv()
input_id = DictConv(optimize(INPUT_ID))
bios_smap_xattr = SmapConv()

FMT2TCONV = {
    "S,clockinfo": clockinfo,
    "S,loadavg": loadavg,
    "S,timeval": timeval,
    "S,vmtotal": vmtotal,
    "S,input_id": input_id,
    "S,pagesizes": pagesizes,
    "S,efi_map_header": tconv.byte,
    "S,bios_smap_xattr": bios_smap_xattr,
}


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
            if self.type == CTLTYPE_OPAQUE:
                self._tconv = FMT2TCONV.get(self.fmt, tconv.byte)
            elif self.type != CTLTYPE_NODE:
                self._tconv = TYPE2TCONV.get(self.type, tconv.byte)
            elif self.name == "vm.swap_info":
                self._tconv = SwapinfoConv(self)
            else:
                self._tconv = tconv.byte
        return self._tconv

    @property
    def raw_value(self) -> bytes:
        if self.type == CTLTYPE_NODE:
            return b""
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


XSWDEV = [
    ("uint", "xsw_version"),
    ("uint64_t", "xsw_dev"),  # dev_t
    ("int", "xsw_flags"),
    ("int", "xsw_nblks"),
    ("int", "xsw_used"),
]


class SwapinfoConv(tconv.TypeConv):
    _swconv = None
    _sizeof = None
    _pagesize = None

    def __init__(self, node: Sysctl) -> None:
        self._name = node._name
        self._mib = node._mib
        if SwapinfoConv._sizeof is None:
            SwapinfoConv._swconv = DictConv(optimize(XSWDEV))
            SwapinfoConv._sizeof = SwapinfoConv._swconv.sizeof
            SwapinfoConv._pagesize = libc.getpagesize()

    def c2p(self, data: bytes, offset: int = 0) -> typing.Any:
        devs = []
        nblks = 0
        used = 0
        try:
            i = 0
            while True:
                data = oidvalue(self._mib + [i], SwapinfoConv._sizeof)
                swdev = SwapinfoConv._swconv.c2p(data)
                swdev["xsw_nblks"] *= SwapinfoConv._pagesize
                swdev["xsw_used"] *= SwapinfoConv._pagesize
                device = libc.devname(swdev["xsw_dev"], 0x2000)
                if device != b"#NODEV":
                    swdev["device"] = "/dev/" + device.decode()
                devs.append(swdev)
                nblks += swdev["xsw_nblks"]
                used += swdev["xsw_used"]
                i += 1
        except RuntimeError:
            pass
        devs.append({"device": "Total", "xsw_nblks": nblks, "xsw_used": used})
        return devs
