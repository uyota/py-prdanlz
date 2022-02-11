# Copyright (c) 2021, 2022 Yoshihiro Ota <ota@j.email.ne.jp>
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

from . import OS_VERSION

BYTE = b"\x102Tv\x98\xba\xdc\xfe"  # 0xFEDCBA9876543210 in little endian

# The last columns indicate FreeBSD version number available

TYPES = [
    (i[0], i[1], i[2])
    for i in [
        ("CTLTYPE_INT", "kern.osrevision", "integer", 12),
        ("CTLTYPE_STRING", "kern.ostype", "string", 12),
        # CTLTYPE_S8 - No Entry
        # CTLTYPE_S16 - No Entry
        # CTLTYPE_S32 - TCP only
        ("CTLTYPE_S64", "kern.ipc.maxmbufmem", "int64_t", 13),
        # CTLTYPE_OPAQUE / CTLTYPE_STRUCT | "vm.pmap", "node"
        ("CTLTYPE_U8", "kern.poweroff_on_panic", "uint8_t", 12),
        ("CTLTYPE_U16", "vm.uma.domainset.bucket_size", "uint16_t", 13),
        ("CTLTYPE_U32", "vm.uma.domainset.size", "uint32_t", 13),
        ("CTLTYPE_U32", "vm.stats.vm.v_free_count", "uint32_t", 12),
        ("CTLTYPE_U64", "vm.swap_total", "uint64_t", 12),
        ("CTLTYPE_UINT", "kern.maxvnodes", "unsigned integer", 12),
        ("CTLTYPE_LONG", "vm.kvm_size", "long integer", 12),
        ("CTLTYPE_ULONG", "vm.kmem_size", "unsigned long", 12),
    ]
    if i[-1] < OS_VERSION
]


OPAQUES = [
    (i[0], i[1])
    for i in [
        ("kern.clockrate", "S,clockinfo", 12),
        ("vm.loadavg", "S,loadavg", 12),
        ("kern.boottime", "S,timeval", 12),
        ("vm.vmtotal", "S,vmtotal", 12),
        # ("", "S,input_id",14),
        ("hw.pagesizes", "S,pagesizes", 13)
        # ("machdep.efi_map", "S,efi_map_header",12), # amd64 only
        # ("machdep.smap", "S,bios_smap_xattr",12), # amd64/i386 only
    ]
    if i[-1] < OS_VERSION
]
