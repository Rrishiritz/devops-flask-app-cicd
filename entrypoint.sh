#!/bin/bash
set -euo pipefail

# If DOCKER_SOCK is mounted, try to align group ownership so jenkins can use it.
DOCKER_SOCK=${DOCKER_SOCK:-/var/run/docker.sock}

if [ -S "$DOCKER_SOCK" ]; then
  # get host socket gid
  HOST_GID=$(stat -c '%g' "$DOCKER_SOCK" 2>/dev/null || true)
  if [ -n "$HOST_GID" ]; then
    # create docker group with same gid if not exists
    if ! getent group docker >/dev/null 2>&1; then
      sudo groupadd -g "$HOST_GID" docker || true
    else
      # if docker group exists but gid differs, create alt group name
      EXISTING_GID=$(getent group docker | cut -d: -f3)
      if [ "$EXISTING_GID" != "$HOST_GID" ]; then
        ALT_GROUP="docker_host_$HOST_GID"
        if ! getent group "$ALT_GROUP" >/dev/null 2>&1; then
          sudo groupadd -g "$HOST_GID" "$ALT_GROUP" || true
        fi
        sudo usermod -aG "$ALT_GROUP" jenkins || true
      else
        sudo usermod -aG docker jenkins || true
      fi
    fi
    # ensure socket is group-readable
    sudo chgrp "$HOST_GID" "$DOCKER_SOCK" 2>/dev/null || true
    sudo chmod g+rw "$DOCKER_SOCK" 2>/dev/null || true
  fi
fi

# Exec Jenkins (base image entrypoint)
exec /sbin/tini -- /usr/local/bin/jenkins.sh
