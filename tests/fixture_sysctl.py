TYPES = [
    ["CTLTYPE_INT", "kern.osrevision", "integer"],
    ["CTLTYPE_STRING", "kern.ostype", "string"],
    # CTLTYPE_S8 - No Entry
    # CTLTYPE_S16 - No Entry
    # CTLTYPE_S32 - TCP only
    # CTLTYPE_S64 - only with PPS_SYNC defined and with ntp pps_req and time_freq
    # CTLTYPE_OPAQUE / CTLTYPE_STRUCT | "vm.pmap", "node"
    ["CTLTYPE_U8", "kern.poweroff_on_panic", "uint8_t"],
    ["CTLTYPE_U16", "vm.uma.domainset.bucket_size", "uint16_t"],
    ["CTLTYPE_U32", "vm.uma.domainset.size", "uint32_t"],
    ["CTLTYPE_U64", "vm.swap_total", "uint64_t"],
    ["CTLTYPE_UINT", "kern.maxvnodes", "unsigned integer"],
    ["CTLTYPE_LONG", "vm.kvm_size", "long integer"],
    ["CTLTYPE_ULONG", "vm.kmem_size", "unsigned long"],
]

OPAQUES = [
    ("kern.clockrate", "S,clockinfo"),
    ("vm.loadavg", "S,loadavg"),
    ("kern.boottime", "S,timeval"),
    ("vm.vmtotal", "S,vmtotal"),
    # ("", "S,input_id"), # doesn't seem to exist
    # ("hw.pagesizes", "S,pagesizes") # since FreeBSD 13.0
    # ("", "S,efi_map_header"), # amd64 only
    # ("machdep.smap", "S,bios_smap_xattr"), # amd64/i386 only
]
