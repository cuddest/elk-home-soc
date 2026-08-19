# Real endpoint integration

## Linux / SSH

Install Filebeat on a Linux host and configure it to read the host's authentication log. Point its `output.logstash` host to the machine running the lab, using TCP/5044 and the lab CA certificate.

The important architectural property is that the downstream pipeline does not change:

```text
Linux host -> Filebeat -> Logstash -> Elasticsearch -> Kibana
```

The lab's synthetic SSH generator simply replaces the Linux host log source when you do not have an external machine.

## Windows / Winlogbeat

Install Winlogbeat directly on Windows. Copy/adapt `config/winlogbeat/winlogbeat.yml` to the Windows endpoint and configure its `output.logstash.hosts` value to the ELK host's TCP/5044 listener.

Winlogbeat reads Windows Event Logs locally and ships structured event data to Logstash. The lab's Windows generator exists only to make 4624/4625 investigations reproducible without a Windows endpoint.

## Same backend, multiple sources

Real and simulated sources can run simultaneously. This allows a hybrid demonstration such as:

```text
Docker Nginx -----------┐
Docker Flask -----------┤
Synthetic SSH ----------┤
Synthetic Windows ------┤
Real Linux Filebeat ----┤--> Logstash --> Elasticsearch --> Kibana
Real Windows Winlogbeat-┘
```
