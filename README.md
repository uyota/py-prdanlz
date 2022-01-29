# Periodic Analyzer - prdanlz

Prdanlz can refresh data and evaluate rules periodically.
It fetch data and save to a variable.
Derivatives are calculated from variables.
Once all variables are refreshed, each incident rule is evaluated based on variables and derivatives.

An incident is a unit of monitoring.
Each incident defines 3 levels: "error", "warn", and "info."
An action is triggered when an incident goes into a new status.
Each level defines a range of a value.


# What can Prdanlz Help?

1. Monitor a system and report an incident
1. Monitor a system and take actions/remediation automatically

# Examples

1. (Swap usage monitor)[example/swap_usage.md]
1. (CPU usage monitor)[example/cpu_usage.md]

## Aiming

1. Help monitoring a small set of FreeBSD machines
1. Obtaining system information and statistics with sysctl and commands
1. Experimenting auto-turn FreeBSD system

# How to Install

It runs on FreeBSD only.

## PyPI

```
% python -m venv venv
% source venv/bin/activate.csh
% pip install prdanlz
```

## PKG + Ports

py-prdanlz is not yet in FreeBSD's ports.
However, ports' Makefile is prepared with the code base.

```
$ cd /usr/ports
$ fetch https://github.com/uyota/py-prdanlz/archive/refs/tags/v0.0.5.tar.gz
$ tar xf v0.0.5.tar.gz
$ cd py-prdanlz/ports
$ make fetch makesum install
```

1. Check [release page](https://github.com/uyota/py-prdanlz/releases) for the latest version.
1. Ports "distinfo" file contains timestamp, checksum, and size of the release file. This file cannot be maintained well in the source repo itself due to chicken and egg problem.  Run 'makesum' to generate it as a part of build process.


# How to Setup

1. Define 'constants' in JSON file
1. Define 'variables' in JSON file
1. Define 'derivatives' in JSON file
1. Define 'incidents' in JSON file
1. Invoke prdanlz program with interval and JSON file(s)

# How to Run

```
% python -m prdanlz -c config.json -i 10 -l prdanlz.log
```

# How does prdanlz Work?

1. Fetch all of constants at startup
1. After waiting an interval second, fetch all variables
1. After all variables are fetched, calcarate all of derivatives
1. After all variables are fetched and derivatives are calculated, evaluate all of incidents
1. If a value moves into a new level of an incident, trigger an action
1. Wait for another interval period and repeat

# Motivations

BSD's sysctl provides a lot of information about the running system.

Sysctl is a system call as well as a corresponding program name.

Base system provides number of other tools to capture
system information one-time or a period of time such as
"systat", "vmstat", "top", "swapctl", and etc.


Using sysctl program becomes very expensive as it starts a new process
each time when gathering number of information.
Calling sysctl system call saves process creation and decoding overhead;
however, writing or adjusting C/C++ program requires a lot of programming hours.

prdanlz uses Python binding of sysctl system call via a library.
This avoid process creation overhead.
By taking advantage of Python interpreter, prdanlz can also provide and
perform complex arithmetics at very low cost compare to shell scripts.

# JSON format

## Top Level

Top level is a dictionary that may contain any of
"constants", "variables", and/or "incidents".

Multiple JSON files may be supplied to prdanlz.

All of "constants" and "variables" names must be unique among them per prdanlz invocation.
All of "incidents" names must be unique among incidents.
An incident can access all of variables regardless of the order in JSON files.

All JSON configuration keywords are spelled in lower cases only.

## "constants", "variables", and "derivatives"

All of "constants", "variables", "derivatives" are all dictionaries.

All of "constants", "variables", "derivatives" are variables but they
have different properties.
"constants" are only fetched once and thus resulting the same value
all times during the monitoring.
"variables" are re-fetched at each cycle.
"derivatives" are calculated variables; they are derived from "constants" and
variables".

Both of "constants" and "variables" are to capture system output and not
convenient to manipulate their values on the fly at same time.
"derivatives" can be used to calculate from "constants" and "variables"
to run arithmetics on and store their results.

All of "constants" and "variables" are stored in their given names.
In addition, "variables" and "derivatives" generate variables that
start with "last_" allowing to refer to previous values.

A dictionary key specifies the name of a variable and dictionary value
represents how to fetch data.
There are 2 data types supported: "syscmd" and "sysctl"


For example,
```
"variables": {
    "time": {"syscmd": "date '+%H:%M:%S'"}
}
```
creates "time" with "19:28:37" and "last_time" with "19:26:37" with 2 minutes
interval.

### "Syscmd" type

A dictionary value of "syscmd" specifies unix command(s) to run.
A sequence of commands with a pipe may be also specified.

```
"time": {"syscmd": "date '+%H:%M:%S'"}
"var_messages": {"syscmd": "wc -l /var/log/messages | awk '{print $1}'"
```

### "Sysctl" type

Sysctl is issued.
Prdanlz uses 'py-sysctl' library and doesn't invoke external 'sysctl' command.

```
"vm__kmem_size": {"sysctl": "vm.kmem_size"},
"hw__ncpu": {"sysctl": "hw.ncpu"}
```

### Order of Evaluations among Variables

1. All "constants" are fetched at start time and only once, first.
1. Then, all "variables" are fetched at each cycle.
1. Then, all "derivatives" are calculated.

Priorities are not defined among same type of variables.
Therefore, they cannot depend on each other.
However, different tiers of variables are always evaluated in the same
order as above and thus safe to assume values are latest.

## "Incidents" and their "Levels"

"Incidents" is a dictionary that contains "indecent" definitions.

### "Incident" Definition

An incident is a directory.

1. Requires "description"
1. Requires either one or more of "error", "warn", "info" level definition

#### Custom Levels

The 3 tier level of "error", "warn", and "info" is a preset value.
Custom level can be specified with --levels option.
The levels are ordered from highest to lowest severity.

```
% python --levels critical error warning info ...
```

### "Level" Definition

A level is a directory.

1. Requires "description"
1. Requires "trigger"
1. Requires "untrigger"
1. Requires "escalation"

#### "description"

Useful description is helpful to keep track what it does, how it does,
who wants what.

#### "trigger"

A trigger is an expression to indicate a variable becomes within threshold.
When an expression is evaluated to true for the first time,
its "escalation" is executed.

#### "untrigger"

An untrigger is an expression.
When an expression is evaluated to true for being alerted,
its "escalated" status is cleared.

Both true values from trigger and untrigger expressions indicates a value
is within threshold.
An untrigger is a low watermark and an trigger is a hight watermark.

#### "trigger"/"untrigger" Formats

"trigger" and "untrigger" take a string of expressions.
These expressions can access constants and variables by
surrounded variable name with curly braces.

##### Examples

Given
```
"trigger": "90 < {value}",
"untrigger": "{value} < 85"
```

1. When value changes [ 10, 20, 30 ], nothing is triggered
1. When value changes [ 0, 95 ], 95 is a trigger
1. When value changes [ 0, 88 ], 88 is NOT a trigger
1. When value changes [ 0, 95, 83 ], 95 is a trigger and 83 is an untrigger
1. When value changes [ 0, 95, 93 ], 95 is a trigger but 93 is not
1. When value changes [ 0, 95, 89, 91 ], 95 is an trigger but neither 89 nor 91

#### "escalation" and its Format

An escalation is an expression that is executed as a shell command.
A sequence of commands can be specified.
Variables surrounded by curly braces are replaced to actual values.

##### Examples

An useful way is send '{description} with 'logger' to write to syslog.

```
"escalation": "logger '{level} {description}'"
```

### "Level" Inheritance

If any of "trigger", "untrigger", or "escalation" is not specified,
lower levels assume they are same as a higher level entry.

Use "level" local variables to simplify and re-use same trigger, untrigger,
and/or escalation at multiple levels.

Given
```
"error": { "trigger":..., "untrigger":..., "escalation": "logger '${level}'" },
"warn": { "trigger":..., "untrigger":...  },
"info": { "trigger":..., "untrigger":..., "escalation": "echo ${level}" }
```
"error" and "warn" are sent to syslog but "info" is only echo-ed.

## "Incident" / "Level" Variables

Primitive values in each of "incident" and "level" dictionaries are accessible.
However, collisions with other variables are not warned.

Given
```
{
"error": { "urgency": "!!!", "escalation": "echo 'Help{urgency}', ... }
"warn": { "urgency": "!", ... }
"info": { "urgency": "", ... }
}
```
"error" prints "Help!!!" and "warn" does "Help!" and "info" does "Help" accordingly.
