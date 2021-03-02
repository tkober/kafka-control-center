#!/usr/bin/env bash

ENV_NAME="confluent-cli"

if [ -x "$(command -v conda)" ]; then
  source activate $ENV_NAME
fi

BASEDIR=$(dirname "$0")
python "$BASEDIR/app.py" $@