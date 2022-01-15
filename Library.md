There are 2 Python sysctl libraries in FreeBSD ports.

# Dependencies

prdanlz uses py-sysctl.

1. FreeBSD pkg version 0.3.1
2. PyPI version 0.3.3 - prior version cannot be installed with pip

# sysctl Libraries

'py-freebsd-sysctl' and 'py-sysctl' exist.
Both use C-binding to access sysctl.

## py-prdanlz uses py-sysctl

Both have bugs but py-sysctl bugs were easier to deal in Python.

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
