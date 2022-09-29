#!/bin/bash
PROJECT_NAME=jmyrberg-website
WEBSITE_BUCKET_NAME=jmyrberg
FOOD_RECOMMENDER_BUCKET_NAME=jmyrberg-food-recommender
REGION=us-east1

# Website bucket
gsutil mb -p $PROJECT_NAME -c Standard -l $REGION -b on gs://$WEBSITE_BUCKET_NAME/
gsutil web set -m index.html -e 404.html gs://$WEBSITE_BUCKET_NAME
gsutil iam ch allUsers:objectViewer gs://$WEBSITE_BUCKET_NAME

# Food recommender bucket
gsutil mb -p $PROJECT_NAME -c Standard -l $REGION -b on gs://$FOOD_RECOMMENDER_BUCKET_NAME/
