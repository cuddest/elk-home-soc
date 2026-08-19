#!/bin/sh
set -eu

ES_URL="https://elasticsearch:9200"
CA="/certs/ca.crt"

until curl --silent --fail --cacert "$CA" -u "elastic:${ELASTIC_PASSWORD}" "$ES_URL/_cluster/health" >/dev/null; do
  echo "Waiting for Elasticsearch..."
  sleep 5
done

echo "Creating/updating kibana_system password..."
curl --silent --fail --cacert "$CA" -u "elastic:${ELASTIC_PASSWORD}" \
  -H 'Content-Type: application/json' \
  -X POST "$ES_URL/_security/user/kibana_system/_password" \
  -d "{\"password\":\"${KIBANA_SYSTEM_PASSWORD}\"}" \
  >/dev/null

echo "Creating/updating Logstash writer role..."
curl --silent --fail --cacert "$CA" -u "elastic:${ELASTIC_PASSWORD}" \
  -H 'Content-Type: application/json' \
  -X PUT "$ES_URL/_security/role/logstash_writer" \
  -d '{"cluster":["monitor"],"indices":[{"names":["logs-*","security-detections-*"],"privileges":["auto_configure","create","create_doc","create_index","write"]}]}' \
  >/dev/null

echo "Creating/updating Logstash writer user..."
curl --silent --fail --cacert "$CA" -u "elastic:${ELASTIC_PASSWORD}" \
  -H 'Content-Type: application/json' \
  -X PUT "$ES_URL/_security/user/logstash_writer" \
  -d "{\"password\":\"${LOGSTASH_PASSWORD}\",\"roles\":[\"logstash_writer\"],\"full_name\":\"ELK Lab Logstash Writer\"}" \
  >/dev/null

echo "[+] Security bootstrap complete."
