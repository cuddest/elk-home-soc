# Application error burst

**Signal:** 3+ HTTP 5xx responses for one application path within five minutes.

**Data view:** `logs-application-*`

**Primary fields:** `url.path`, `http.response.status_code`, `event.duration`, `@timestamp`.
