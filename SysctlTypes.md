# Struct Sysctl Types

The output examples of supported struct based sysctl are displayed as below.

1. [clockinfo type](./SysctlTypes.md#clockinfo-type)
1. [loadavg type](./SysctlTypes.md#loadavg-type)
1. [pagesizes type](./SysctlTypes.md#pagesizes-type)
1. [timeval type](./SysctlTypes.md#timeval-type)
1. [vmtotal type](./SysctlTypes.md#vmtotal-type)

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
