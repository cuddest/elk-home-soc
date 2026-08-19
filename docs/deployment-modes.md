# Deployment modes

The lab supports three operating modes.

## Simulation

```bash
./lab.sh start --mode simulation
```

Use this when you want a fully reproducible local lab. Nginx and Flask produce real local telemetry, while SSH and Windows events come from deterministic generators.

## Real endpoint mode

```bash
./lab.sh start --mode real
```

This starts the ELK backend and publishes the Logstash Beats port. Real Linux Filebeat and Windows Winlogbeat agents can send telemetry to the host running Logstash.

Set these in `.env` for a real networked endpoint:

```text
LOGSTASH_BEATS_BIND=0.0.0.0
LOGSTASH_BEATS_PORT=5044
```

Only do this on a trusted lab network and protect TCP/5044 with a firewall and TLS. Do not expose it directly to the public Internet.

## Hybrid mode

```bash
./lab.sh start --mode hybrid
```

Hybrid mode runs the simulation sources and also allows real endpoints to send telemetry into the same Logstash instance.

Optional real SSH container:

```bash
./lab.sh start --mode hybrid --real-ssh
```

The SSH container runs a real `sshd` process for controlled local authentication testing. It is deliberately a lab source, not a hardened production SSH host.

## Windows integration

A real Windows endpoint is external to Docker. Install Winlogbeat on the Windows machine and use `config/winlogbeat/winlogbeat.yml` as the project template. The endpoint sends directly to the published Logstash Beats listener.

The synthetic Windows generator remains available for reproducible tests.
