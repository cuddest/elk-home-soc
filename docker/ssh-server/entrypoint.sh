#!/bin/sh
set -eu

apk add --no-cache openssh >/dev/null

mkdir -p /run/sshd /logs/ssh
ssh-keygen -A >/dev/null 2>&1

if ! id "$SSH_USER" >/dev/null 2>&1; then
  adduser -D "$SSH_USER"
fi

echo "$SSH_USER:$SSH_PASSWORD" | chpasswd

# Lab-only configuration: password authentication is intentionally enabled.
# SSHD logs are captured through a custom auth log file for Filebeat.
cat >/etc/ssh/sshd_config.d/lab.conf <<CFG
PasswordAuthentication yes
PermitRootLogin no
UsePAM no
LogLevel VERBOSE
CFG

# Keep sshd in foreground and mirror its stderr into a local file.
exec /usr/sbin/sshd -D -e 2>/logs/ssh-real/sshd.log
