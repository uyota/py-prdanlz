# TODOs

## MIB may change

kldload and kldunload can result adding or removing sysctl entries.
MIB is updated and prdanlz needs to address.

## Sysctl Entry Removal
kldunload can result not having some sysctl entries being monitored.
prdanlz need to define behavior for the cases.
