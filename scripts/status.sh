#!/usr/bin/env bash
set -euo pipefail

docker compose ps

echo
printf '%-24s' 'Elasticsearch: '
curl --silent --fail --cacert certs/ca.crt -u "elastic:$(grep '^ELASTIC_PASSWORD=' .env | cut -d= -f2-)" \
  https://127.0.0.1:${ES_PORT:-9200}/_cluster/health?pretty | grep -E '"status"|"number_of_nodes"' || true

echo "\nKibana: https://127.0.0.1:${KIBANA_PORT:-5601}"
echo "Nginx:  http://127.0.0.1:${NGINX_PORT:-8080}/health"
