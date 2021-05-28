#!/bin/bash
gcloud run services delete picky-eater
gcloud container images delete gcr.io/${GOOGLE_CLOUD_PROJECT}/picky-eater
