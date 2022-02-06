# Battery Life Monitor

Monitor AC line and battery life to prevent unsafe shutdown.

Referred from [Shell script to shutdown FreeBSD laptop when running out of battery power](https://bash.cyberciti.biz/monitoring/shell-script-to-shutdown-freebsd-laptop-when-low-on-battery-power/).

## [battery.json](./battery.json)

This configuration is an example to monitor AC line and battery life.
If battery life isn't available, py-prdanlz stops.

The info and warn actions are to write to "/var/log/message" via "logger."
However, the error action is to "shutdown" the system.

## Technical Notes

1. It only uses all 3 levels
1. It uses 1 "error" "escalation" to shutdown
1. It uses same "warn" and "info" "escalation" to write to syslog
1. It uses same "trigger" and "untrigger" based on "percent" for all levels
