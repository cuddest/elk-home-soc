# Architecture

## Data plane

The lab has four main telemetry paths:

1. Nginx access events.
2. Flask application events.
3. Synthetic SSH authentication events.
4. Synthetic Windows authentication events.

Nginx and Flask write JSON logs to bind-mounted directories. The SSH and Windows generators write JSON Lines to the same shared log tree. Filebeat tails those files using the `filestream` input and forwards events to Logstash.

## Processing plane

Logstash is the normalization boundary. It:

- identifies each source with `event.dataset`;
- adds source tags;
- ensures ECS-style categorization fields are present;
- converts data types where required;
- optionally enriches source IPs with GeoIP for SSH telemetry;
- routes each dataset to a dedicated daily index.

## Storage plane

Elasticsearch receives events over HTTPS using a dedicated `logstash_writer` account. Index names are:

```text
logs-nginx-YYYY.MM.dd
logs-application-YYYY.MM.dd
logs-ssh-YYYY.MM.dd
logs-windows-YYYY.MM.dd
security-detections-YYYY.MM.dd
```

## Analyst plane

Kibana is exposed on HTTPS localhost-only and uses the built-in `kibana_system` account to communicate with Elasticsearch.

## Network model

```text
Host
├── 127.0.0.1:5601 → Kibana
├── 127.0.0.1:8080 → Nginx
└── 127.0.0.1:9200 → Elasticsearch (local diagnostic access only)

Docker network
├── Kibana → Elasticsearch
├── Logstash → Elasticsearch
├── Filebeat → Logstash
├── Nginx → Flask
└── Generators → shared log volumes
```

The Elasticsearch host mapping is localhost-only so it remains useful for testing with curl without exposing the service on every host interface.
