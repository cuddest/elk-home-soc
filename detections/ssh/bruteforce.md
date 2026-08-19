# SSH brute force

**Signal:** 5+ failed SSH authentications from the same `source.ip` within five minutes.

**Data view:** `logs-ssh-*`

**Primary fields:** `source.ip`, `user.name`, `event.outcome`, `@timestamp`.

**MITRE ATT&CK:** T1110 Brute Force.
