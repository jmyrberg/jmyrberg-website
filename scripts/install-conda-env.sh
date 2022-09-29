#!/bin/bash

echo Installing...
NAME=jmyrberg-website
conda env remove -n $NAME -y
conda create -n $NAME python=3.10 -y && \  # Not GCP, but 3.7. causes problems with OS
conda activate $NAME && \
pip install -r ./functions/doc_context_similarity/requirements.txt \
            -r ./functions/get_food_recommender/requirements.txt \
            -r ./functions/post_food_recommender/requirements.txt \
            -r ./functions/maximum_flows/requirements.txt \
            -r ./functions/contact/requirements.txt \
            -r ./functions/finscraper/requirements.txt \
            -r ./functions/requirements-dev.txt
echo Installation done!
