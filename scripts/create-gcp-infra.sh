#!/bin/bash
# To build the infra, follow this tutorial:
# https://cloud.google.com/storage/docs/hosting-static-website
# 
# One can also use the commands below, apart from:
# - Buying a domain
# - Setting up nameservers and A/CNAME records
# - HTTP -> HTTPS redirection
PROJECT_NAME=jmyrberg-website
DOMAIN=jmyrberg.com
FOOD_RECOMMENDER_BUCKET_NAME=jmyrberg-food-recommender
WEBSITE_BUCKET_NAME=jmyrberg
BUCKET_REGION=us-east1
API_REGION=europe-west1

# Website bucket
gsutil mb -p $PROJECT_NAME -c Standard -l $BUCKET_REGION -b on gs://$WEBSITE_BUCKET_NAME/
gsutil web set -m index.html -e 404.html gs://$WEBSITE_BUCKET_NAME
gsutil iam ch allUsers:objectViewer gs://$WEBSITE_BUCKET_NAME

# Food recommender bucket
gsutil mb -p $PROJECT_NAME -c Standard -l $BUCKET_REGION -b on gs://$FOOD_RECOMMENDER_BUCKET_NAME/

# Network stuff
# IP
gcloud compute addresses create $WEBSITE_BUCKET_NAME-ip \
    --network-tier=PREMIUM \
    --ip-version=IPV4 \
    --global

IP_ADDRESS=gcloud compute addresses describe $WEBSITE_BUCKET_NAME-ip \
    --format="get(address)" \
    --global

# UI LB backend under $DOMAIN
gcloud compute backend-buckets create $WEBSITE_BUCKET_NAME-lb-backend \
    --gcs-bucket-name=$WEBSITE_BUCKET_NAME

# Load balancer url-map
gcloud compute url-maps create $WEBSITE_BUCKET_NAME-url-map \
    --default-backend-bucket=$WEBSITE_BUCKET_NAME-lb-backend

# API LB Backend under $DOMAIN/api/<function>
gcloud compute network-endpoint-groups create api-neg \
    --region=$API_REGION \
    --network-endpoint-type=serverless \
    --cloud-function-url-mask="/api/<function>"
gcloud compute backend-services create api-lb-backend \
    --load-balancing-scheme=EXTERNAL_MANAGED \
    --global
gcloud compute backend-services add-backend api-lb-backend \
    --network-endpoint-group=api-neg \
    --network-endpoint-group-region=$API_REGION \
    --global
gcloud compute url-maps add-path-matcher $WEBSITE_BUCKET_NAME-url-map \
    --path-matcher-name=api-path-matcher \
    --default-backend-bucket=$WEBSITE_BUCKET_NAME-lb-backend \
    --backend-service-path-rules='/api/*=api-lb-backend' \
    --new-hosts="$DOMAIN,*.$DOMAIN"

# SSL certificates
gcloud compute ssl-certificates create $WEBSITE_BUCKET_NAME-ssl \
       --domains $DOMAIN

# HTTPS load balancer
gcloud compute target-https-proxies create $WEBSITE_BUCKET_NAME-lb-proxy \
       --ssl-certificates=$WEBSITE_BUCKET_NAME-ssl \
       --url-map=$WEBSITE_BUCKET_NAME-url-map
gcloud compute forwarding-rules create $WEBSITE_BUCKET_NAME-forwarding-rule \
    --load-balancing-scheme=EXTERNAL_MANAGED \
    --network-tier=PREMIUM \
    --address=$WEBSITE_BUCKET_NAME-ip \
    --target-https-proxy=$WEBSITE_BUCKET_NAME-lb-proxy \
    --global \
    --ports=443

# HTTP -> HTTPS redirection cannot be done fully in gcloud:
# https://cloud.google.com/load-balancing/docs/https/setting-up-http-https-redirect#partial-http-lb