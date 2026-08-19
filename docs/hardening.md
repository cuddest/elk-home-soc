# Hardening notes

## Implemented in this lab

- Elasticsearch security enabled.
- Elasticsearch HTTP and transport TLS enabled.
- Kibana HTTPS enabled.
- Filebeat -> Logstash TLS enabled.
- Elasticsearch -> host exposure limited to localhost.
- Logstash port 5044 is internal-only.
- Dedicated `logstash_writer` account.
- Credentials stored in `.env` and excluded from Git.
- Certificates generated locally and excluded from Git.

## Why the old version was weaker

The original lab used:

```text
xpack.security.enabled=false
```

and exposed `9200:9200` without authentication. That is convenient for a classroom exercise but is not an acceptable security boundary for a real deployment.

## Remaining production concerns

A real production Elastic deployment would additionally need:

- trusted CA-signed certificates where appropriate;
- stronger secret storage and rotation;
- multi-node Elasticsearch for resilience;
- snapshots and tested recovery;
- resource limits and capacity planning;
- firewall/network segmentation;
- patching and vulnerability management;
- monitoring of Elastic itself;
- documented access control and audit requirements.
