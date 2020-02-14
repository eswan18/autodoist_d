#!/bin/bash

docker run \
    -e EMAIL_ADDR -e EMAIL_PW -e TODOIST_API_TOKEN \
    -d \
    --restart always \
    --mount type=bind,source=$PWD/config,target=/autodoist_d/config \
    autodoist
