# CPU Usage Monitor

FreeBSD maintains load average over 1, 3, and 15 minutes.

CPU usage can be calculated with load average and number of CPUs.

## Load Average and Background

A single process load is how much allocated time-slice a process used
in a period of time.  For example, if a process is waiting for user
input and being blocked by a system call, its load is 0.
If gzip is busy compressing and using all of its allocate time, its load is 1.
If mkuzip spawns 10 threads and all of them are fully used, its load is 10.

Load average is skewed by the number of CPUs.  If 2 processes use 100% of
their time-slice on a single CPU machine, its load average is 2 and
it uses 100% CPU resources already.  On the other hand, even if 10 processes use
100% of CPUs on a 128-core machine, its CPU usage is less than 10% although
its load is 10.

In order to calcarate CPU usage, both the number of CPUs and load average are
important.

## (cpu_usage.json)[cpu_usage.json]

This configuration is an example to monitor by percentage cpu usage over 1 minutes.

The action is to write to "/var/log/message" via "logger."

## prdanlz's loadavg Format

prdanz returns a tuple of 3 numbers representing 1-minute, 3-minute and
15-minute load average.

## loadavg Example

```
>>> from prdanlz.libc.sysctl import Sysctl
>>> s = Sysctl("vm.loadavg")
>>> s.value
(0.341796875, 0.3388671875, 0.330078125)
```

## Technical Notes

1. It only uses warn level and error nor info levels are omitted
1. It uses 1 "constants" to obtain number of CPUs via hw.ncpu;
this is because the number of CPUs doesn't change at run time
1. It uses "vm.loadavg" sysctl "variables" to capture load average at every period
