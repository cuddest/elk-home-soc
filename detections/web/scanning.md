# Web scanning

**Signal:** 10+ HTTP 404 responses from the same source within five minutes.

**Data view:** `logs-nginx-*`

**Primary fields:** `source.ip`, `url.path`, `http.response.status_code`, `user_agent.original`.
