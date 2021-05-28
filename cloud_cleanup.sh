#!/bin/bash
gcloud run services delete picky-eater --platform="managed" --region="us-west1" -q
gcloud container images delete gcr.io/${GOOGLE_CLOUD_PROJECT}/picky-eater --force-delete-tags -q
