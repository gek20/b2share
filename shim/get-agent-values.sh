#!/bin/bash

#
# This script is now part of the docker-entrypoint.sh for:
# - Postgres
# - Rabbitmq
#

# If in Postgres container, write secret values into files
if [[ ${PG_MAJOR} ]]; then
  echo -e "Setting up postgres ${PG_MAJOR}\n"

  export AGENT_ADDR="http://agent:8100"

  if [[ ${VAULT_AGENT_ADDR} ]]; then
    export AGENT_ADDR=${VAULT_AGENT_ADDR}
  fi

  SECRETS=$(curl -s ${AGENT_ADDR}/v1/secret/data/b2share/internal/dev/application | jq .data.data)

  echo ${SECRETS} | jq -r .POSTGRES_DB > /run/secrets/db
  echo ${SECRETS} | jq -r .POSTGRES_USER > /run/secrets/user
  echo ${SECRETS} | jq -r .POSTGRES_PASSWORD > /run/secrets/passwd

  echo -e "\nDone!\n"
fi
