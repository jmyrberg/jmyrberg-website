#!/bin/bash
#
# Steps: https://devopsdirective.com/posts/2020/10/gcs-cloudflare-hosting
# 
# Updated to use CloudFlare to avoid GCP load balancer costs
# 
# Cloudflare DNS:
#     A: www          | 192.0.2.1
# CNAME: jmyrberg.com | c.storage.googleapis.com
# 
# Cloudflare Page Rules:
# www.jmyrberg.com/* -> https://jmyrberg.com/$1 / Forwarding URL / 301
#
PROJECT_ID=jmyrberg-website
WEBSITE_BUCKET_NAME=jmyrberg.com
FOOD_RECOMMENDER_BUCKET_NAME=jmyrberg-food-recommender
BUCKET_REGION=europe-west1

# Create website bucket
gsutil mb -p $PROJECT_ID -c Standard -l $BUCKET_REGION -b on gs://$WEBSITE_BUCKET_NAME
gsutil web set -m index.html -e 404.html gs://$WEBSITE_BUCKET_NAME
gsutil iam ch allUsers:legacyObjectReader gs://$WEBSITE_BUCKET_NAME

# Food recommender bucket
gsutil mb -p $PROJECT_ID -c Standard -l $BUCKET_REGION -b on gs://$FOOD_RECOMMENDER_BUCKET_NAME
