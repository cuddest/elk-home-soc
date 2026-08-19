# Detection engineering

The detector is intentionally small and readable. The goal is to demonstrate the mechanics of security analytics rather than hide everything inside a framework.

## 1. SSH brute force

Query:

```text
source dataset = lab.ssh
AND event.outcome = failure
AND @timestamp >= now-5m
```

Aggregate by `source.ip`. Alert at 5 or more failures.

Investigation:

- inspect targeted accounts;
- inspect source GeoIP metadata;
- check for a successful authentication from the same IP;
- pivot into web/application telemetry around the same time.

## 2. Windows brute force

Use Windows event code `4625` as a failed logon signal. Aggregate by `source.ip` and alert at 5 or more in five minutes.

## 3. Web scanning

Use HTTP 404 bursts as a simple discovery signal. Ten or more 404s from the same source in five minutes produces a medium-severity alert.

The model is intentionally conservative. In a real environment you would add URI reputation, path categories, user-agent analysis, and allowlists.

## 4. Application error burst

Three or more 5xx responses for one application path in five minutes creates a medium-severity alert.

This is both an application-health signal and a possible security signal because abnormal errors can appear during probing or abuse.

## 5. Authentication failure -> success

The correlation detector looks across the authentication telemetry for a source that has at least three failures and at least one success in a ten-minute window.

This is a useful investigation pattern because successful authentication immediately after repeated failures can indicate credential guessing or a user finally entering valid credentials after mistakes.

## False positives

Every detector is intentionally simple. Real deployments need:

- administrator and service-account allowlists;
- known scanner IPs;
- VPN/NAT context;
- business-hour context;
- thresholds tuned to real baselines;
- correlation across hosts and accounts;
- analyst feedback loops.
