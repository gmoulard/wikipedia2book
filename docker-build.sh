#!/bin/sh
docker build \
  --build-arg GIT_COMMIT="$(git log -1 --format=%H)" \
  --build-arg GIT_DATE="$(git log -1 --format=%ci)" \
  --build-arg GIT_AUTHOR="$(git log -1 --format=%an)" \
  -t wikipedia2book .
