# Windows brute force

**Signal:** 5+ Windows Security event `4625` failures from the same `source.ip` within five minutes.

**Data view:** `logs-windows-*`

**Primary fields:** `event.code`, `source.ip`, `user.name`, `winlog.event_data.IpAddress`, `@timestamp`.

**MITRE ATT&CK:** T1110 Brute Force.
