# Investigation workflow

## Case 1 — SSH brute force followed by success

### Initial alert

`ssh_bruteforce` reports repeated authentication failures from one source.

### Triage

1. Open the alert in `security-detections-*`.
2. Extract `source.ip` and the targeted users.
3. Search `logs-ssh-*` for the same source.
4. Check whether `event.outcome=success` occurs after the failure burst.
5. Search all telemetry around the timestamp.

### Timeline

```text
T0    multiple SSH failures
T0+   more failures against additional users
T0+   successful authentication
T0+   application/web activity
```

### Assessment

The combination is more suspicious than either event alone. The analyst should determine whether the successful login belongs to a legitimate user or represents a compromised account.

## Case 2 — Windows authentication anomaly

Search `logs-windows-*` for `event.code:4625` and pivot on `source.ip`. Look for a later `event.code:4624` from the same address.

## Case 3 — Web scanning

Start from the `web_scanning` alert and inspect:

- source IP;
- requested paths;
- response codes;
- user agent;
- request volume over time.

The analyst should decide whether the activity is ordinary client behavior, a scanner, or a precursor to further application abuse.
