# Threat model

| Asset | Threat | Telemetry | Control / Detection |
|---|---|---|---|
| Linux authentication | Password guessing | SSH events | SSH brute-force detector |
| Windows authentication | Password guessing | 4625/4624-style events | Windows brute-force + correlation |
| Web application | Discovery/probing | Nginx access logs | 404-burst detector |
| API | Abuse / instability | Flask logs | 5xx-burst detector |
| Monitoring platform | Unauthorized data access | Elastic auth/TLS | Authentication + localhost exposure |
| Detection pipeline | Lost/invalid telemetry | Logstash/Filebeat | Parse-failure visibility |
