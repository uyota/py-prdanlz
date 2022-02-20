# Struct Sysctl Types

The output examples of supported struct based sysctl are displayed as below.

1. [bios_smap_xattr type](./SysctlTypes.md#bios_smap_xattr)
1. [clockinfo type](./SysctlTypes.md#clockinfo)
1. [loadavg type](./SysctlTypes.md#loadavg)
1. [pagesizes type](./SysctlTypes.md#pagesizes)
1. [timeval type](./SysctlTypes.md#timeval)
1. [vmtotal type](./SysctlTypes.md#vmtotal)

## bios_smap_xattr

Sysctl machdep.smap is only available on i386 and amd64 only.
The return type is a list of dicts.

### sysctl bios_smap_xattr
```
sysctl machdep.smap
machdep.smap:
SMAP type=01, xattr=01, base=0000000000000000, len=000000000009d800
SMAP type=02, xattr=01, base=000000000009d800, len=0000000000002800
SMAP type=02, xattr=01, base=00000000000e0000, len=0000000000020000
SMAP type=01, xattr=01, base=0000000000100000, len=00000000bf3d6000
SMAP type=04, xattr=01, base=00000000bf4d6000, len=0000000000048000
SMAP type=03, xattr=01, base=00000000bf51e000, len=000000000000b000
SMAP type=04, xattr=01, base=00000000bf529000, len=0000000000001000
SMAP type=02, xattr=01, base=00000000bf52a000, len=0000000000024000
SMAP type=01, xattr=01, base=00000000bf54e000, len=0000000000002000
SMAP type=04, xattr=01, base=00000000bf550000, len=0000000000021000
SMAP type=02, xattr=01, base=00000000bf571000, len=0000000000023000
SMAP type=04, xattr=01, base=00000000bf594000, len=000000000000b000
SMAP type=02, xattr=01, base=00000000bf59f000, len=0000000000002000
SMAP type=04, xattr=01, base=00000000bf5a1000, len=0000000000011000
SMAP type=02, xattr=01, base=00000000bf5b2000, len=000000000002b000
SMAP type=04, xattr=01, base=00000000bf5dd000, len=0000000000043000
SMAP type=01, xattr=01, base=00000000bf620000, len=00000000001e0000
SMAP type=01, xattr=01, base=0000000100000000, len=000000023e000000
SMAP type=02, xattr=01, base=00000000fed1c000, len=0000000000024000
SMAP type=02, xattr=01, base=00000000ff000000, len=0000000001000000
```
### prdanlz bios_smap_xattr
```
>>> from prdanlz.libc.sysctl import Sysctl
>>> s = Sysctl("machdep.smap")
>>> s.value
[
    {"base": 0, "length": 645120, "type": 1, "xattr": 1},
    {"base": 645120, "length": 10240, "type": 2, "xattr": 1},
    {"base": 917504, "length": 131072, "type": 2, "xattr": 1},
    {"base": 1048576, "length": 3208470528, "type": 1, "xattr": 1},
    {"base": 3209519104, "length": 294912, "type": 4, "xattr": 1},
    {"base": 3209814016, "length": 45056, "type": 3, "xattr": 1},
    {"base": 3209859072, "length": 4096, "type": 4, "xattr": 1},
    {"base": 3209863168, "length": 147456, "type": 2, "xattr": 1},
    {"base": 3210010624, "length": 8192, "type": 1, "xattr": 1},
    {"base": 3210018816, "length": 135168, "type": 4, "xattr": 1},
    {"base": 3210153984, "length": 143360, "type": 2, "xattr": 1},
    {"base": 3210297344, "length": 45056, "type": 4, "xattr": 1},
    {"base": 3210342400, "length": 8192, "type": 2, "xattr": 1},
    {"base": 3210350592, "length": 69632, "type": 4, "xattr": 1},
    {"base": 3210420224, "length": 176128, "type": 2, "xattr": 1},
    {"base": 3210596352, "length": 274432, "type": 4, "xattr": 1},
    {"base": 3210870784, "length": 1966080, "type": 1, "xattr": 1},
    {"base": 4294967296, "length": 9630121984, "type": 1, "xattr": 1},
    {"base": 4275159040, "length": 147456, "type": 2, "xattr": 1},
    {"base": 4278190080, "length": 16777216, "type": 2, "xattr": 1},
]
```

## clockinfo

Dict type.

### sysctl clockinfo
```
% sysctl kern.clockrate
kern.clockrate: { hz = 1000, tick = 1000, profhz = 8128, stathz = 127 }
```

### prdanlz clockinfo
```
>>> from prdanlz.libc.sysctl import Sysctl
>>> s = Sysctl("kern.clockrate")
>>> s.value
{'hz': 1000, 'tick': 1000, 'stathz': 127, 'profhz': 8128}
```

## loadavg

Tuple of 3 elements.

### sysctl loadavg
```
% sysctl vm.loadavg
vm.loadavg: { 0.28 1.28 1.79 }
```

### prdanlz loadavg
```
>>> from prdanlz.libc.sysctl import Sysctl
>>> s = Sysctl("vm.loadavg")
>>> s.value
(0.26025390625, 1.26171875, 1.78173828125)
```

## pagesizes

List of integers.

### sysctl pagesizes
```
% sysctl hw.pagesizes
hw.pagesizes: { 4096, 2097152 }
```

### prdanlz pagesizes
```
>>> from prdanlz.libc.sysctl import Sysctl
>>> s = Sysctl("hw.pagesizes")
>>> s.value
[4096, 2097152]
```

## timeval

Tuple of dict and str format date.

```
% sysctl kern.boottime
kern.boottime: { sec = 1644445940, usec = 361239 } Wed Feb  9 17:32:20 2022
```

```
>>> from prdanlz.libc.sysctl import Sysctl
>>> s = Sysctl("kern.boottime")
>>> s.value
({'sec': 1644445940, 'usec': 1551509691039744}, 'Wed Feb  9 17:32:20 2022')
amd64
```

## vmtotal

Dict with short notation names.
Sysctl prints very customized format.

### sysctl vmtotal
```
% sysctl vm.vmtotal
vm.vmtotal:
System wide totals computed every five seconds: (values in kilobytes)
===============================================
Processes:              (RUNQ: 5 Disk Wait: 0 Page Wait: 0 Sleep: 190)
Virtual Memory:         (Total: 4951784K Active: 4951456K)
Real Memory:            (Total: 1097612K Active: 1097416K)
Shared Virtual Memory:  (Total: 160K Active: 0K)
Shared Real Memory:     (Total: 140K Active: 0K)
Free Memory:    8243536K
```

### prdanlz vmtotal
```
>>> from prdanlz.libc.sysctl import Sysctl
>>> s = Sysctl("vm.vmtotal")
>>> s.value
{'t_vm': 2091810, 't_avm': 2087529, 't_rm': 746083, 't_arm': 745940, 't_vmshr': 4210, 't_avmshr': 7, 't_rmshr': 130, 't_armshr': 7, 't_free': 1788658, 't_rq': 48, 't_dw': 0, 't_pw': 0, 't_sl': 277, 't_sw': 0}
>>>
```

## swap_info

List of swap devices with device name, bytes used, size of block in bytes,
and some internal information.
The last entry is the total.

The sysctl program does not print anything.
However, `swapctl -l` uses vm.swap_info sysctl behind the scene.

### sysctl swap_info / swapctl
```
% sysctl vm.swap_info
% swapctl -l
Device:       1024-blocks     Used:
/dev/ada0s1b    5242880   2268788
```

### prdanlz swap_info
```
>>> from prdanlz.libc.sysctl import Sysctl
>>> s = Sysctl("vm.swap_info")
>>> s.value
[
    {'xsw_version': 2, 'xsw_dev': 104, 'xsw_flags': 1, 'xsw_nblks': 5368709120, 'xsw_used': 2323210240, 'device': '/dev/ada0s1b'},
    {'device': 'Total', 'xsw_nblks': 5368709120, 'xsw_used': 2323210240}
]
>>>
```
