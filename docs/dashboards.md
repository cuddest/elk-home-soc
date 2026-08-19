# Kibana dashboards

The repository deliberately keeps dashboard content documented instead of shipping a large version-sensitive Lens export. Run `scripts/create-kibana-data-views.py` first, then build the dashboards in Kibana using the listed data views.

## SOC Overview

Data view: `logs-*`

Panels:

1. Total event count.
2. Events over time.
3. Authentication failures by source IP.
4. Authentication successes by source IP.
5. HTTP 4xx / 5xx counts.
6. Top target users.
7. Top source IPs.

## Authentication Monitoring

Data view: `logs-ssh-*` and `logs-windows-*`

Panels:

- failures over time;
- successes over time;
- source IPs;
- target users;
- event.code distribution;
- source GeoIP for SSH data.

## Web Security

Data view: `logs-nginx-*`

Panels:

- requests over time;
- top source IPs;
- top paths;
- 404 count;
- 5xx count;
- user agents.

## Windows Security

Data view: `logs-windows-*`

Panels:

- 4624 vs 4625;
- top source IPs;
- top target users;
- authentication timeline.

## Detection Overview

Data view: `security-detections-*`

Panels:

- alerts over time;
- alerts by rule name;
- severity;
- top source IPs;
- latest alerts table.
