#!/bin/sh
COUNT=${1:-50}
LOG_FILE="/logs/ssh/auth.log"
mkdir -p /logs/ssh

i=1
while [ $i -le $COUNT ]; do
    TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    USERS="root admin user ubuntu test git deploy"
    IPS="185.234.72.45 91.213.50.12 103.45.67.89 45.33.32.156 192.168.1.10 10.0.0.5 172.16.0.22 203.0.113.42"
    
    IDX_U=$(( $(od -An -N1 -tu1 /dev/urandom | tr -d ' ') % 7 ))
    IDX_I=$(( $(od -An -N1 -tu1 /dev/urandom | tr -d ' ') % 8 ))
    
    USER=$(echo $USERS | cut -d' ' -f$(( IDX_U + 1 )))
    IP=$(echo $IPS | cut -d' ' -f$(( IDX_I + 1 )))
    PORT=$(( $(od -An -N2 -tu2 /dev/urandom | tr -d ' ') % 64000 + 1024 ))
    SESSION=$(od -An -N4 -tx1 /dev/urandom | tr -d ' \n' | head -c 8 | tr 'a-f' 'A-F')
    
    RAND=$(( $(od -An -N1 -tu1 /dev/urandom | tr -d ' ') % 5 ))
    if [ $RAND -eq 0 ]; then
        RESULT="failure"
    else
        RESULT="success"
    fi
    
    printf '{"timestamp":"%s","event":"ssh_auth","user":"%s","source_ip":"%s","port":%d,"auth_method":"password","session_id":"%s","result":"%s"}\n' \
        "$TS" "$USER" "$IP" "$PORT" "$SESSION" "$RESULT" >> $LOG_FILE
    
    i=$(( i + 1 ))
done

echo "Generated $COUNT SSH log entries in $LOG_FILE"
