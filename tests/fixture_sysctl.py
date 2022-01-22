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
        # ("", "S,efi_map_header",12), # amd64 only
        # ("machdep.smap", "S,bios_smap_xattr",12), # amd64/i386 only
    ]
    if i[-1] < OS_VERSION
]
