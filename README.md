# Periodic Analyzer - prdanlz

Prdanlz can refresh data and evaluate rules periodically.
It fetch data and save to a variable.
Once all variables are refreshed, each incident rule is evaluated based on variables.

An incident is a unit of monitoring.
Each incident defines 3 levels: "error", "warn", and "info."
An action is triggered when an incident goes into a new status.
Each level defines a range of a value.


# What can Prdanlz Help?

1. Monitor a system and report an incident
1. Monitor a system and take actions/remediation automatically

## Aiming

1. Help monitoring a small set of FreeBSD machines
1. Obtaining system information and statistics with sysctl and commands
1. Experimenting auto-turn FreeBSD system

# How to Install and Setup

It runs on FreeBSD only.

```
$ pkg install py##-sysctl
% pip install --no-deps prdanlz
```

Unfortunately, "pypi sysctl" cannot be installed as it is out-dated.
Py-sysctl must be installed via ports/pkg as it fetches a newer and working version.

# How to Setup

1. Define 'constants' in JSON file
1. Define 'variables' in JSON file
1. Define 'incidents' in JSON file
1. Invoke prdanlz program with interval and JSON file(s)

# How to Run

```
% python -m prdanlz -c config.json -i 10 -l prdanlz.log
```

# How does prdanlz Work?

1. Fetch all of constants at startup
1. After waiting an interval second, fetch all variables
1. After all variables are fetched, evaluate all of incidents
1. If a value moves into a new level of an incident, trigger an action
1. Wait for another interval period and repeat

# JSON format

## Top Level

Top level is a dictionary that may contain any of
"constants", "variables", and/or "incidents".

Multiple JSON files may be supplied to prdanlz.

All of "constants" and "variables" names must be unique among them per prdanlz invocation.
All of "incidents" names must be unique among incidents.
An incident can access all of variables regardless of the order in JSON files.

All JSON configuration keywords are spelled in lower cases only.

## "Constants" and "variables"

"Constants" and "variables" are both dictionaries.

"Constants" and "variables" are both variables but "constants"
are only fetched once while "variables" are re-fetched at each cycle.

Both of "constants" and "variables" are stored in their given names.
In addition, "variables" generates variables start with "last_"

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

## "Incidents" and their "Levels"

"Incidents" is a dictionary that contains "indecent" definitions.

### "Incident" Definition

An incident is a directory.

1. Requires "description"
1. Requires either one or more of "error", "warn", "info" level definition

### "Level" Definition

A level is a directory.

1. Requires "trigger"
1. Requires "untrigger"
1. Requires "escalation"

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
