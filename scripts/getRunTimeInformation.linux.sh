#!/bin/bash

JS_FILE=$1
RUNTIME_INFO=$2
TIMEOUT_SECONDS=$3

ROOT_PROJECT_PATH=$(dirname "${JS_FILE}")
JS_FILE_NAME=$(basename "${JS_FILE}")

SCRIPT_PATH="$( cd "$(dirname "$0")" ; pwd -P )"

if [ "${ROOT_PROJECT_PATH:0:1}" = "/" ]; then
	ABS_ROOT_PROJECT_PATH=$ROOT_PROJECT_PATH
else
	ABS_ROOT_PROJECT_PATH="$(pwd)/$ROOT_PROJECT_PATH"
fi

FILE_IN_CONTAINER="/tmp/runtimeAnalysis"

CONTAINER_NAME=$(LC_ALL=C tr -dc A-Za-z0-9 </dev/urandom | head -c 20 ; echo)

docker rm $CONTAINER_NAME > /dev/null 2>&1
timeout -k $TIMEOUT_SECONDS $TIMEOUT_SECONDS docker run \
	--name $CONTAINER_NAME \
	-v $ABS_ROOT_PROJECT_PATH:$FILE_IN_CONTAINER  \
	-v $SCRIPT_PATH/blacklistedModules.json:/tmp/blacklistedModules.json \
	master-mind-wp3 \
	$FILE_IN_CONTAINER/$JS_FILE_NAME \
	/tmp/blacklistedModules.json \
	1> /tmp/runtimeinfo

LINE_NUMBER="$(grep /tmp/runtimeinfo -ne "^{$" | cut -f1 -d:)"
LINE_NUMBER="$(($LINE_NUMBER-1))"

if [ "$LINE_NUMBER" -gt "1" ]; then
	sed -e "1,${LINE_NUMBER}d" /tmp/runtimeinfo > $RUNTIME_INFO
else
	cp /tmp/runtimeinfo $RUNTIME_INFO
fi

docker rm $CONTAINER_NAME > /dev/null 2>&1