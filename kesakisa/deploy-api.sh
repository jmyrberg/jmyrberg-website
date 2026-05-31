#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${PROJECT_ID:-jmyrberg-website}"
REGION="${REGION:-europe-west1}"
FUNCTION_NAME="${FUNCTION_NAME:-kesakisa_api}"
ENV_FILE="${ENV_FILE:-kesakisa/api/.env.production.yaml}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing env file: $ENV_FILE" >&2
  echo "Create it from kesakisa/api/.env.production.yaml.example before deploying." >&2
  exit 1
fi

gcloud functions deploy "$FUNCTION_NAME" \
  --project "$PROJECT_ID" \
  --region "$REGION" \
  --gen2 \
  --runtime python312 \
  --source kesakisa/api \
  --entry-point kesakisa_api \
  --trigger-http \
  --allow-unauthenticated \
  --min-instances 0 \
  --max-instances 1 \
  --memory 128Mi \
  --concurrency 1 \
  --timeout 30 \
  --env-vars-file "$ENV_FILE"

gcloud functions describe "$FUNCTION_NAME" \
  --project "$PROJECT_ID" \
  --region "$REGION" \
  --gen2 \
  --format="value(serviceConfig.uri)"
