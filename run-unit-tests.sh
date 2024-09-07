#!/bin/sh
set -e

docker compose -f docker-compose-unit-tests.yml build
docker compose -f docker-compose-unit-tests.yml up --no-log-prefix --remove-orphans --force-recreate --abort-on-container-exit --exit-code-from unit-tests