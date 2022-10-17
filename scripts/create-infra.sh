#!/bin/bash
#
# Steps in CloudFlare:
#
# DNS:
#     A: www          | 192.0.2.1
# CNAME: jmyrberg.com | c.storage.googleapis.com
#
# Page Rules:
# www.jmyrberg.com/* -> https://jmyrberg.com/$1 / Forwarding URL / 301
#
# Service Worker:
# Name: 404-to-200 / Compute setting: Global / Code in scripts/cloudflare-service-worker.js
# 
# Workers Routes:
# Route: *jmyrberg.com/demo-projects/* / Service: 404-to-200 / Environment: production
# 
#
# Steps in Google (link + commands below):
# https://devopsdirective.com/posts/2020/10/gcs-cloudflare-hosting
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
