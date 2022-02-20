# Swap Usage Monitor

Swap usage information is available on FreeBSD via sysctl "vm.swap_info."
"vm.swap_info" is a special NODE type such that sysctl.1 cannot retrieve
but swapctl -l can.

There is a maximum amount of swap space FreeBSD system can used.
That can be captured with vm.swap_maxpages.

When calculating the size of swap device usage, this maximum
also need to be considered; otherwise, system won't be
able to swap out even though there are physical spaces seemingly available.

## [swap_usage.json](./swap_usage.json)

This configuration is an example to monitor by percentage usage
of swap space.

The action is to write to "/var/log/message" via "logger."

## prdanlz's swap_info Format

prdanz puts "Total" at end all times unlike swapctl -l.

## swap_info Example

```
>>> from prdanlz.libc.sysctl import Sysctl
>>> s = Sysctl("vm.swap_info")
>>> s.value
[
    {
        "xsw_version": 2,
        "xsw_dev": 104,
        "xsw_flags": 1,
        "xsw_nblks": 5368709120,
        "xsw_used": 2973700096,
        "device": "/dev/ada0s1b",
    },
    {"device": "Total", "xsw_nblks": 5368709120, "xsw_used": 2973700096},
]
```

## Technical Notes

1. It uses 3 levels
1. It consders the system maximum in addition to device space along
1. It uses 1 "escalation" and uses "percent" to use per "level" message context
