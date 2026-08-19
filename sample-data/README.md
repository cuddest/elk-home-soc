# Sample data

The live lab generates data under `data/logs/`. This directory intentionally starts empty except for the files needed by the containers.

The Windows simulator models common native security events:

- `4624` — successful logon.
- `4625` — failed logon.

The simulated events are clearly tagged with `lab.synthetic=true` so they cannot be mistaken for real endpoint telemetry.
