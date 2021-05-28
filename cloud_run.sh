#!/bin/bash
gcloud run deploy picky-eater --image gcr.io/${GOOGLE_CLOUD_PROJECT}/picky-eater --service-account apis-aag3@${GOOGLE_CLOUD_PROJECT}.iam.gserviceaccount.com --update-env-vars "YELP_API_KEY=$YELP_API_KEY","MAP_KEY=$MAP_KEY" --platform="managed" --allow-unauthenticated --region="us-west1"

