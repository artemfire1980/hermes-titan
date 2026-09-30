#!/bin/bash
# Git credential helper для GitHub fine-grained token

# Источник env-файла: сначала Hermes, потом локальный (для совместимости)
if [ -f /mnt/ai-ssd/hermes/.env ]; then
    set -a
    source /mnt/ai-ssd/hermes/.env
    set +a
elif [ -f ~/ai-system/.env ]; then
    set -a
    source ~/ai-system/.env
    set +a
fi

if [ "$1" = "get" ]; then
    while IFS= read -r line; do
        case "$line" in
            protocol=*) protocol="${line#*=}" ;;
            host=*) host="${line#*=}" ;;
        esac
    done

    if [ "$host" = "github.com" ] && [ -n "$GITHUB_TOKEN" ]; then
        echo "protocol=$protocol"
        echo "host=$host"
        echo "username=$GITHUB_USER"
        echo "password=$GITHUB_TOKEN"
    fi
fi
