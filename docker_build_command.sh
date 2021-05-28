#!/bin/bash
# docker command to build and test locally
# Needs GOOGLE_APPLICATION_CREDENTIALS to be present lcoally.
# GOOGLE_APPLICATION_CREDENTIALS needs to be in same path for container mount and local path
docker run -p 8000:8000 --env PORT=8000 --env GOOGLE_APPLICATION_CREDENTIALS=/home/Downloads/cloud-f20-alec-greenaway-aag3-b4b21754994c.json -v $GOOGLE_APPLICATION_CREDENTIALS:/home/Downloads/cloud-f20-alec-greenaway-aag3-b4b21754994c.json:ro map
