There are 2 Python sysctl libraries in FreeBSD ports.

# Dependencies

prdanlz does not depend on other libraries

## Options

There were 2 python sysctl library implementations: 'py-sysctl' and 'py-freebsd_sysctl'.
prdanlz started with 'py-sysct' library.
It was a nice library to use for a proof of concept but came to limits shortly.
'py-freebsd_sysctl' had good examples of C-binding and making calls to
C APIs in libc. These were helpful starters.

1. prdanlz needed to use not only sysctl but other system calls and thus reusable byte converters
1. Both libraries had primitive type conversion errors
1. Both had API limitations and performance issues

Sysctl calls in prdanlz is 5 times faster than that of 'py-sysctl' and
'py-freebsd_sysctl' in nearly all use cases.
prdanlz makes periodic calls to sysctl and thus it optimizes to call
1 sysctl system call per fetch; other libraries call 5 sysctl system
calls per fetch.

'py-freebsd_sysctl' had some activates and accepted bug fixes.
'py-sysctl' didn't seem to have much activities but had APIs that
can be used to work-around the bugs.

Afte a proof of concept ran, it appeared what prdanlz needed most was
accessing struct sysctl types.  Neither libraries supported struct types.

# Old Notes

## sysctl Libraries

'py-freebsd-sysctl' and 'py-sysctl' exist.
Both use C-binding to access sysctl.

# Pros and Cons

## py-sysctl
### Pros
1. Everything is in C
### Cons
1. Can fetch value only once
1. Format string isn't accessible
1. Low activities
1. Not OOP
1. Conversion bugs for unsinged types

## py-freebsd_sysctl
### Pros
1. Use ctypes and strruct in Python
1. Moderate activities
### Cons
1. Can fetch value only once
1. Too many class instantiations and need optimizations
1. Test cases are failing

# py-sysctl

1. Exists longer period of time
1. Function call returns a list of classes
1. Setter exists
1. Seems to handle SOME OPEQ types
1. Returns a list
1. The value class member function returns a cached value

## Experiments

```
% python3
>>> import sysctl
>>> a = sysctl.filter('hw.ncpu')
>>> type(a)
<class 'list'>
>>> type(a[0])
<class 'Sysctl'>
>>> a[0].value
4
>>> type(a[0].value)
<class 'int'>
>>> b = sysctl.filter('vm.stats.vm.v_free_count')
>>> type(b)
<class 'list'>
>>> type(b[0])
<class 'Sysctl'>
>>> type(b[0].value)
<class 'bytearray'>
>>> b[0].value
bytearray(b'\x87\x91\x00\x00')
```

# py-freebsd-sysctl 

1. Class fetches and returns value, etc
1. Setter seems exist
1. Seems not handling OPEQ types
1. The value class member function returns a cached value

## Experiments


```
% python3
>>> from freebsd_sysctl import Sysctl
>>> a = Sysctl('hw.ncpu')
>>> type(a)
<class 'freebsd_sysctl.Sysctl'>
>>> a.value
4
>>> type(a.value)
<class 'int'>
>>> b = Sysctl('vm.stats.vm.v_free_count')
>>> type(b.value)
<class 'int'>
>>> b.value
33731

```
