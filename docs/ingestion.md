# Ingestion walkthrough

A single Nginx request demonstrates the entire pipeline.

```text
curl http://localhost:8080/products
        ↓
Nginx
        ↓
/logs/nginx/access.log
        ↓
Filebeat filestream
        ↓
TLS Beats connection
        ↓
Logstash :5044
        ↓
ECS normalization / tags / enrichment
        ↓
HTTPS Elasticsearch API
        ↓
logs-nginx-YYYY.MM.dd
        ↓
Kibana Discover
```

## Why JSON logs?

The original university version relied heavily on raw text + Grok. The new version uses structured NDJSON for the generated sources so fields arrive already separated. Nginx emits JSON directly; this removes unnecessary text parsing for the normal path.

Grok remains relevant conceptually and is still covered in the docs as the approach to use when a source only provides unstructured text.

## Why ECS-style fields?

Using consistent fields makes cross-source analysis possible. The most important fields used by the project are:

```text
@timestamp
source.ip
user.name
event.category
event.outcome
event.code
http.request.method
http.response.status_code
url.path
user_agent.original
```

## Parse failures

The pipeline tags malformed events with `parse_failure` when `event.original` is present. This provides a visible place to investigate data-quality problems instead of silently ignoring them.
