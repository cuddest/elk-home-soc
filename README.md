# ELK Security Monitoring Lab
You can read more about it [Here](https://cuddest.github.io/cuddest/writeups/elk-security-monitoring.html) in this article ! 

A reproducible, containerized SOC-style laboratory for collecting, normalizing, detecting, and investigating Linux, web, application, and Windows-security telemetry with the Elastic Stack.

## What this project demonstrates

- Centralized security telemetry collection with Filebeat and Winlogbeat.
- Three deployment modes: `simulation`, `real`, and `hybrid`.
- Real endpoint integration paths for Linux/Filebeat and Windows/Winlogbeat.
- Optional real OpenSSH container for controlled authentication testing.
- Secure ingestion from Filebeat to Logstash with TLS.
- Log parsing, normalization, enrichment, and routing with Logstash.
- Elasticsearch indexing and search with authentication and HTTPS.
- Kibana investigation over HTTPS.
- ECS-inspired event fields such as `@timestamp`, `source.ip`, `user.name`, `event.category`, `event.outcome`, `event.code`, and HTTP fields.
- Synthetic attack scenarios for SSH brute force, Windows authentication failures, web scanning, and application failures.
- Transparent detection logic that queries Elasticsearch and writes alerts to `security-detections-*`.
- Incident-investigation workflows and case studies.
- Development-friendly Docker Compose deployment with localhost-only exposure of Elasticsearch, Kibana, and Nginx.

> This is a laboratory. The attack data is synthetic and intentionally generated for detection engineering and investigation practice. It is not a production SOC deployment.

## Architecture

```text
                         Synthetic Activity
      ┌───────────────────────┬────────────────────────┐
      │                       │                        │
      ▼                       ▼                        ▼
   Nginx/Web             SSH generator          Windows generator
      │                       │                        │
      ▼                       ▼                        ▼
  access.log              auth.log                events.log
      │                       │                        │
      └───────────────────────┴────────────────────────┘
                              │
                           Filebeat
                              │
                       TLS / Beats 5044
                              │
                              ▼
                          Logstash
                 ┌────────────┼────────────┐
                 │            │            │
              parse       normalize     enrich
                 │            │            │
                 └────────────┼────────────┘
                              │
                         HTTPS / REST
                              │
                              ▼
                        Elasticsearch
                              │
                    ┌─────────┴─────────┐
                    │                   │
                 Kibana             Detector
                    │                   │
                    ▼                   ▼
               Analyst views       Security alerts
                                        │
                                        ▼
                            security-detections-*
```

## Portfolio article

The repository is the implementation layer. The portfolio article can be the narrative/documentation layer: explain the problem, architecture, telemetry sources, simulated-vs-real modes, data pipeline, detection logic, investigations, hardening, and lessons learned. Add the final article URL here when published.

> Portfolio article: `https://cuddest.github.io/cuddest/writeups/elk-security-monitoring.html`

## Documentation

The repository contains engineering documentation under [`docs/`](docs/), while the portfolio article is intended to be the reader-friendly narrative.

## Components

| Component | Role |
|---|---|
| Nginx | Reverse proxy and web-access telemetry source |
| Flask | Small API used to generate realistic application telemetry |
| Filebeat | Collects JSON/NDJSON logs and forwards them to Logstash |
| Logstash | Parses, normalizes, enriches, tags, and routes telemetry |
| Elasticsearch | Searchable event store |
| Kibana | Investigation and visualization interface |
| SSH simulator | Generates synthetic SSH authentication telemetry |
| Windows simulator | Generates synthetic Windows 4624/4625-style security telemetry |
| Detector | Runs transparent threshold/correlation detections against Elasticsearch |

## Versioning

The repository pins the Elastic Stack to `9.4.4` by default. Keep Elasticsearch, Kibana, Logstash, Filebeat, and other Elastic components on the same version.

## Prerequisites

- Docker Engine with Compose V2.
- At least ~4 GB of RAM available to Docker; more is better for Elasticsearch/Kibana.
- Bash.
- OpenSSL.
- Python 3.11+ on the host for the testing/detection scripts.

## Deployment modes

### Simulation mode

Fully reproducible local lab; no external endpoints are required.

```bash
cp .env.example .env
./scripts/bootstrap-certs.sh
./lab.sh start --mode simulation
```

### Real endpoint mode

Starts the ELK backend and publishes the Logstash Beats listener for external Filebeat/Winlogbeat endpoints.

```bash
./lab.sh start --mode real
```

For a LAN lab, set `LOGSTASH_BEATS_BIND` in `.env` to the host interface you want to expose. Protect TCP/5044 with your firewall.

### Hybrid mode

Run simulated sources and real endpoints at the same time.

```bash
./lab.sh start --mode hybrid
```

Optional real OpenSSH container:

```bash
./lab.sh start --mode hybrid --real-ssh
```

More detail: [`docs/deployment-modes.md`](docs/deployment-modes.md) and [`docs/real-endpoints.md`](docs/real-endpoints.md).

Check the stack:

```bash
./scripts/status.sh
```

Open Kibana:

```text
https://localhost:5601
```

The browser will warn about the self-signed lab CA. For local testing, import `certs/ca.crt` into your browser/OS trust store or continue through the warning if your browser allows it.

Default lab username/password values come from `.env`:

```text
username: elastic
password: the value of ELASTIC_PASSWORD
```

Create Kibana data views:

```bash
python3 -m pip install -r tools/requirements.txt
python3 scripts/create-kibana-data-views.py
```

## Generate activity

### Normal traffic

```bash
python3 generators/scenarios/run_normal_traffic.py --count 40
```

### SSH brute force

```bash
SOURCE_IP=185.234.72.45 MODE=failure \
  bash generators/ssh/generate_ssh_logs.sh 12
```

### Windows authentication failures

```bash
python3 generators/windows/generate_windows_events.py \
  --count 12 \
  --mode failure \
  --source-ip 185.234.72.45
```

### Web scanning

```bash
python3 generators/web/generate_web_scan.py --count 20
```

### Failure -> success correlation scenario

```bash
python3 generators/scenarios/run_auth_compromise.py
```

## Run detections

Install Python dependencies once:

```bash
python3 -m pip install -r tools/requirements.txt
```

Run the detection pack:

```bash
ES_PASSWORD="$(grep '^ELASTIC_PASSWORD=' .env | cut -d= -f2-)" \
  python3 scripts/detect.py --once
```

The detector checks:

1. SSH brute force.
2. Windows 4625 brute force.
3. Web scanning based on repeated 404s.
4. Application 5xx bursts.
5. Repeated authentication failures followed by success.

Alerts are written to `security-detections-*` and can be investigated in Kibana.

## Useful Elasticsearch checks

Cluster health:

```bash
curl --cacert certs/ca.crt \
  -u "elastic:${ELASTIC_PASSWORD}" \
  https://localhost:9200/_cluster/health?pretty
```

Indexes:

```bash
curl --cacert certs/ca.crt \
  -u "elastic:${ELASTIC_PASSWORD}" \
  https://localhost:9200/_cat/indices?v
```

Count events:

```bash
curl --cacert certs/ca.crt \
  -u "elastic:${ELASTIC_PASSWORD}" \
  'https://localhost:9200/logs-*/_count?pretty'
```

Failed authentication events:

```bash
curl --cacert certs/ca.crt \
  -u "elastic:${ELASTIC_PASSWORD}" \
  -H 'Content-Type: application/json' \
  https://localhost:9200/logs-*/_search?pretty \
  -d '{"query":{"term":{"event.outcome":"failure"}},"size":10,"sort":[{"@timestamp":"desc"}]}'
```

## Detection matrix

| Scenario | Source | Main signal | Threshold |
|---|---|---|---:|
| SSH brute force | `logs-ssh-*` | `event.outcome=failure`, grouped by `source.ip` | 5 / 5 min |
| Windows brute force | `logs-windows-*` | `event.code=4625`, grouped by `source.ip` | 5 / 5 min |
| Web scanning | `logs-nginx-*` | HTTP 404 burst by `source.ip` | 10 / 5 min |
| Application error burst | `logs-application-*` | HTTP 5xx grouped by `url.path` | 3 / 5 min |
| Authentication anomaly | SSH + Windows | failures + subsequent success by `source.ip` | 3 failures + 1 success / 10 min |

## Investigation workflow

```text
Alert
  ↓
Triage
  ↓
Identify source / target
  ↓
Build timeline
  ↓
Correlate related telemetry
  ↓
Assess impact
  ↓
Document evidence
  ↓
Recommend containment/remediation
```

See:

- `docs/architecture.md`
- `docs/ingestion.md`
- `docs/detection.md`
- `docs/investigation.md`
- `docs/hardening.md`
- `docs/threat-model.md`
- `docs/dashboards.md`

## Project structure

```text
.
├── app/                 # Flask API + Dockerfile
├── config/              # Filebeat and Logstash configuration
├── dashboards/          # Dashboard definitions/guides
├── detections/          # Detection documentation
├── generators/          # Normal and adversarial event generators
├── nginx/               # Reverse proxy configuration
├── scripts/              # Bootstrap, security, detection, testing
├── tools/               # Python dependencies for host-side tooling
├── tests/               # Static/unit tests
├── docs/                # Architecture and SOC documentation
├── sample-data/         # Small hand-crafted examples
└── docker-compose.yml   # Lab orchestration
```

## Security model

- Elasticsearch is protected by authentication and HTTPS.
- Elasticsearch is published only on `127.0.0.1`.
- Kibana is published only on `127.0.0.1`.
- Nginx is published only on `127.0.0.1`.
- Logstash is not published to the host; only the Docker network can reach port 5044.
- Logstash uses a dedicated writer account rather than the `elastic` superuser.
- TLS is used between Filebeat -> Logstash and Logstash -> Elasticsearch.
- The CA and private key are generated locally and ignored by Git.

## Windows telemetry note

The repository uses a Python simulator to generate ECS-style Windows security events so the lab remains reproducible on Linux/Kali/macOS. In a real Windows endpoint, Winlogbeat or Elastic Agent would collect native Windows Event Log records and forward them into the same pipeline. The sample data models common Security event IDs such as 4624 and 4625.

## Development vs production

This repository is intended for local development, demonstration, and training. It is **not** a production deployment. Production would require additional measures such as trusted certificates, stronger secret management, multi-node Elasticsearch, backups, operational monitoring, firewalling, and a deployment model appropriate to the environment.

## Stop / reset

Stop while keeping data:

```bash
docker compose down
```

Stop and delete Elasticsearch data:

```bash
docker compose down -v
```

Reset logs too:

```bash
rm -f data/logs/*/*.log
```

Then rebuild with:

```bash
./scripts/bootstrap-certs.sh
docker compose up -d
```

## License

This project is released under the [MIT License](LICENSE).

You are free to use, copy, modify, merge, publish, distribute, sublicense, and sell copies of the project, subject to the conditions of the license.

See the [LICENSE](LICENSE) file for the full terms.
