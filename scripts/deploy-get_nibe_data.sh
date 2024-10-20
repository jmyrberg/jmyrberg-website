#!/bin/bash
# Set variables into './functions/.env.production' before running
API_REGION=europe-west1

gcloud functions deploy get_nibe_data \
    --project jmyrberg-website \
    --gen2 \
    --runtime python312 \
    --trigger-topic get-nibe-data \
    --retry \
    --ingress-settings internal-only \
    --memory 128Mi \
    --source ./functions/get_nibe_data \
    --region $API_REGION \
    --max-instances 1 \
    --timeout 60 \
    --set-env-vars "$(paste -d, -s ./functions/.env.production)"
