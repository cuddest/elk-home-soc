# elk-home-soc

A self-contained home SOC lab on Docker: an ELK stack (Elasticsearch, Logstash, Kibana, Filebeat) ingesting logs from simulated web, SSH, and application traffic — plus a Windows security event pipeline. Everything you need to practice detection engineering, log parsing, and alerting without standing up a production SIEM.

## Stack

| Service      | Role                                                        |
|--------------|-------------------------------------------------------------|
| Elasticsearch | Storage + search engine (single node, security disabled)   |
| Logstash      | Parses/grok/normalizes events, ships to ES                  |
| Kibana        | Dashboards, Discover, alerting UI                          |
| Filebeat      | Tailers the log files and forwards to Logstash              |
| Nginx + Flask | Generates realistic web/API traffic                         |
| SSH simulator | Writes synthetic `auth.log` entries                         |

## Layout

```
config/
  filebeat.yml      # inputs: nginx, ssh, app logs
  logstash.conf     # grok, geoip, date parsing, index routing
docker/
  docker-compose.yml
  nginx.conf
  generate_ssh_logs.sh
  app/              # Flask app that emits JSON request logs
sample_nginx.log            # reference data, load it manually
sample_windows_events.txt   # reference data, load it manually
```

## Quick start

```bash
docker compose -f docker/docker-compose.yml up --build
```

Wait for the Elasticsearch healthcheck to pass, then:

- Kibana: http://localhost:5601
- Elasticsearch: http://localhost:9200
- Nginx: http://localhost:8080

Generate traffic to see it land in Kibana:

```bash
curl http://localhost:8080/health
curl http://localhost:8080/products
curl -X POST http://localhost:8080/checkout -H 'Content-Type: application/json' -d '{"item":"prod-101"}'
docker exec ssh-simulator sh /generate_ssh_logs.sh 100
```

## Indices

Logstash routes events by source into daily indices:

| Index              | Source        |
|--------------------|---------------|
| `lab-nginx-*`      | Nginx access logs (grok + geoip)   |
| `lab-ssh-*`        | SSH auth events                    |
| `lab-app-*`        | Flask API request logs             |
| `lab-windows-*`    | Winlogbeat / Windows events        |
| `lab-misc-*`       | Everything else                    |

## Windows events

Point a Winlogbeat agent at Logstash on port `5044` and events land in
`lab-windows-*`. A sample export of real event IDs lives in
`sample_windows_events.txt` if you want to load a baseline by hand.