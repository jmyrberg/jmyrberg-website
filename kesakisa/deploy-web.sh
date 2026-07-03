#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${PROJECT_ID:-jmyrberg-website}"
REGION="${REGION:-europe-west1}"
FUNCTION_NAME="${FUNCTION_NAME:-kesakisa_api}"
WEBSITE_BUCKET="${WEBSITE_BUCKET:-jmyrberg.com}"
API_URL="${API_URL:-}"

if [[ -z "$API_URL" ]]; then
  API_URL="$(gcloud functions describe "$FUNCTION_NAME" \
    --project "$PROJECT_ID" \
    --region "$REGION" \
    --gen2 \
    --format="value(serviceConfig.uri)")"
fi

if [[ -z "$API_URL" ]]; then
  echo "Could not resolve API_URL. Deploy the API function first or pass API_URL explicitly." >&2
  exit 1
fi

(
  cd kesakisa/web
  VITE_KESAKISA_API_BASE_URL="$API_URL" npm run build
)

gcloud storage rsync -r kesakisa/web/dist "gs://$WEBSITE_BUCKET/kesakisa"

gcloud storage objects update \
  --cache-control="no-cache, max-age=0, no-transform" \
  "gs://$WEBSITE_BUCKET/kesakisa/index.html" \
  "gs://$WEBSITE_BUCKET/kesakisa/admin/index.html" \
  "gs://$WEBSITE_BUCKET/kesakisa/sw.js" \
  "gs://$WEBSITE_BUCKET/kesakisa/manifest.webmanifest"

gcloud storage objects update \
  --cache-control="public, max-age=31536000, immutable" \
  "gs://$WEBSITE_BUCKET/kesakisa/assets/**"
