#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CERT_DIR="$ROOT_DIR/certs"
mkdir -p "$CERT_DIR"

if command -v openssl >/dev/null 2>&1; then
  OPENSSL_BIN=openssl
else
  echo "openssl is required. Install it and rerun." >&2
  exit 1
fi

if [[ -f "$CERT_DIR/ca.crt" && -f "$CERT_DIR/stack.crt" && -f "$CERT_DIR/stack.key" ]]; then
  echo "Certificates already exist in $CERT_DIR"
  exit 0
fi

TMP_DIR="$CERT_DIR/.tmp"
rm -rf "$TMP_DIR"
mkdir -p "$TMP_DIR"
trap 'rm -rf "$TMP_DIR"' EXIT

cat > "$TMP_DIR/openssl.cnf" <<'CNF'
[req]
distinguished_name = dn
x509_extensions = v3_ca
prompt = no

[dn]
CN = ELK Security Lab CA

[v3_ca]
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid:always,issuer
basicConstraints = critical, CA:true
keyUsage = critical, keyCertSign, cRLSign
CNF

LOGSTASH_HOSTNAME="${LOGSTASH_HOSTNAME:-localhost}"

cat > "$TMP_DIR/server.cnf" <<CNF
[req]
distinguished_name = dn
req_extensions = req_ext
prompt = no

[dn]
CN = elk-security-lab

[req_ext]
subjectAltName = @alt_names
keyUsage = critical, digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth

[alt_names]
DNS.1 = elasticsearch
DNS.2 = kibana
DNS.3 = logstash
DNS.4 = localhost
IP.1 = 127.0.0.1
DNS.5 = ${LOGSTASH_HOSTNAME}
CNF

echo "[*] Generating local CA..."
$OPENSSL_BIN genrsa -out "$CERT_DIR/ca.key" 4096
$OPENSSL_BIN req -x509 -new -nodes -key "$CERT_DIR/ca.key" -sha256 -days 825 \
  -out "$CERT_DIR/ca.crt" -config "$TMP_DIR/openssl.cnf"

echo "[*] Generating shared lab certificate..."
$OPENSSL_BIN genrsa -out "$CERT_DIR/stack.key" 2048
$OPENSSL_BIN req -new -key "$CERT_DIR/stack.key" \
  -out "$TMP_DIR/stack.csr" -config "$TMP_DIR/server.cnf"
$OPENSSL_BIN x509 -req -in "$TMP_DIR/stack.csr" \
  -CA "$CERT_DIR/ca.crt" -CAkey "$CERT_DIR/ca.key" -CAcreateserial \
  -out "$CERT_DIR/stack.crt" -days 825 -sha256 \
  -extensions req_ext -extfile "$TMP_DIR/server.cnf"

chmod 644 "$CERT_DIR"/ca.crt "$CERT_DIR"/stack.crt
chmod 600 "$CERT_DIR"/ca.key "$CERT_DIR"/stack.key
rm -f "$CERT_DIR/ca.srl"
echo "[+] Certificates created under $CERT_DIR"
