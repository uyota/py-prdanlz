# Last Pid Monitor

Monitor last pid and reports when it wraps.

## [last_pid.json](./last_pid.json)

This configuration is an example to monitor last pid and to report a wrap.

The info action is written to "/var/log/message" via "logger."

## Technical Notes

1. It only uses "depth" for historical data
