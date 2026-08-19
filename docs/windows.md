# Windows collection with Winlogbeat

The default lab uses `generators/windows/generate_windows_events.py` because that keeps the repository runnable on Linux/Kali/macOS without requiring a separate Windows machine.

For a real Windows endpoint, use the included `config/winlogbeat/winlogbeat.yml` as the starting point.

The relevant architecture becomes:

```text
Windows Security Event Log
        ↓
Winlogbeat
        ↓
TLS / Logstash 5044
        ↓
Logstash
        ↓
logs-windows-*
        ↓
Kibana
```

Collect at least the `Security` channel for this project's authentication detections.

For a real Windows host, make Logstash reachable from that host using a properly firewalled listener. Do not expose the ingestion endpoint broadly to the Internet. Use authentication/TLS and network restrictions appropriate to the environment.
