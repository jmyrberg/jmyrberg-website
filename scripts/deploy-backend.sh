#!/bin/bash
# Set variables into './functions/.env.production' before running
API_REGION=europe-west1

gcloud functions deploy forecaster \
    --runtime python310 \
    --trigger-http \
    --allow-unauthenticated \
    --memory 512MB \
    --source ./functions/forecaster \
    --region $API_REGION \
    --max-instances 1 \
    --timeout 120 \
    --set-env-vars "$(paste -d, -s ./functions/.env.production)"

gcloud functions deploy disable_billing \
    --runtime python310 \
    --trigger-topic billing-information \
    --memory 128MB \
    --source ./functions/disable_billing \
    --region $API_REGION \
    --max-instances 1 \
    --timeout 60 \
    --set-env-vars "GCP_PROJECT=jmyrberg-website"

gcloud functions deploy contact \
    --runtime python310 \
    --trigger-http \
    --allow-unauthenticated \
    --memory 128MB \
    --source ./functions/contact \
    --region $API_REGION \
    --max-instances 1 \
    --timeout 60 \
    --set-env-vars "$(paste -d, -s ./functions/.env.production)"

gcloud functions deploy doc_context_similarity \
    --runtime python310 \
    --trigger-http \
    --allow-unauthenticated \
    --memory 2048MB \
    --source ./functions/doc_context_similarity \
    --region $API_REGION \
    --max-instances 1 \
    --timeout 60 \
    --set-env-vars "$(paste -d, -s ./functions/.env.production)"

gcloud functions deploy finscraper \
    --runtime python310 \
    --trigger-http \
    --allow-unauthenticated \
    --memory 1024MB \
    --source ./functions/finscraper \
    --region $API_REGION \
    --max-instances 1 \
    --timeout 60 \
    --set-env-vars "$(paste -d, -s ./functions/.env.production)"

gcloud functions deploy get_food_recommender \
    --runtime python310 \
    --trigger-http \
    --allow-unauthenticated \
    --memory 128MB \
    --source ./functions/get_food_recommender \
    --region $API_REGION \
    --max-instances 1 \
    --timeout 60 \
    --set-env-vars "$(paste -d, -s ./functions/.env.production)"

gcloud functions deploy maximum_flows \
    --runtime python310 \
    --trigger-http \
    --allow-unauthenticated \
    --memory 128MB \
    --source ./functions/maximum_flows \
    --region $API_REGION \
    --max-instances 1 \
    --timeout 60 \
    --set-env-vars "$(paste -d, -s ./functions/.env.production)"

gcloud functions deploy post_food_recommender \
    --runtime python310 \
    --trigger-http \
    --allow-unauthenticated \
    --memory 128MB \
    --source ./functions/post_food_recommender \
    --region $API_REGION \
    --max-instances 1 \
    --timeout 60 \
    --set-env-vars "$(paste -d, -s ./functions/.env.production)"
