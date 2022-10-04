"""Module for getting food recommender data."""


import functools
import json
import os
import tempfile
import uuid

from pathlib import Path

from google.cloud.storage.client import Client
from flask import jsonify
from itsdangerous import Signer


storage_client = None


def request_wrapper(original_func=None,
                    allowed_methods=frozenset(['GET', 'PUT', 'OPTIONS', 'POST',
                                               'DELETE'])):
    def _decorate(func):
        @functools.wraps(func)
        def wrapped_func(request):
            # Allowed methods
            if request.method not in allowed_methods:
                return jsonify({'status': 'error',
                                'message': 'Method not allowed',
                                'data': None}), 403

            # CORS
            CORS_ORIGINS = os.environ['CORS_ORIGINS'].split(';')
            origin = request.headers.get('origin')
            headers = {}
            if '*' in CORS_ORIGINS:
                headers['Access-Control-Allow-Origin'] = '*'
            elif origin and origin in CORS_ORIGINS:
                headers['Access-Control-Allow-Origin'] = origin
            if len(CORS_ORIGINS) > 1 and '*' not in CORS_ORIGINS:
                headers['Vary'] = 'Origin'

            if request.method == 'OPTIONS':
                headers = {
                    **headers,
                    'Access-Control-Allow-Methods': allowed_methods,
                    'Access-Control-Allow-Headers': ['Content-Type',
                                                     'x-api-key'],
                    'Access-Control-Max-Age': '3600'
                }
                return ('', 204, headers)

            # API token
            api_key = request.headers.get('X-API-KEY')
            if api_key is None:
                return jsonify({'status': 'error',
                                'message': 'Missing "x-api-key" header',
                                'data': None}), 401

            try:
                Signer(os.environ['SECRET_KEY']).unsign(api_key)
            except Exception:
                return jsonify({'status': 'error',
                                'message': 'Invalid access token',
                                'data': None}), 401

            # Run function
            try:
                resp, status = func(request)
                return jsonify(resp), status, headers
            except Exception as e:
                return jsonify({'status': 'error',
                                'message': str(e),
                                'data': None}), 500, headers

        return wrapped_func

    if original_func:
        return _decorate(original_func)

    return _decorate


@request_wrapper(allowed_methods=['POST', 'OPTIONS'])
def post_food_recommender(request):
    """Get existing food recommender list."""
    data = request.get_json()['data']
    list_id = request.args.get('listId') or str(uuid.uuid4())
    data['listId'] = list_id

    if os.getenv('ENV', 'production') == 'local':
        expected_path = (
            Path(tempfile.gettempdir()) / 'jmyrberg-food-recommender' /
            'data' / f'{list_id}.json')
        expected_path.parent.mkdir(exist_ok=True, parents=True)
        with open(expected_path, 'w') as f:
            json.dump(data, f)
        return {'status': 'success',
                'message': 'Food recommender list saved successfully',
                'data': {'listId': list_id}}, 200
    else:
        global storage_client
        if not storage_client:
            storage_client = Client()
        bucket_name = os.getenv('FOOD_RECOMMENDER_BUCKET_NAME',
                                'jmyrberg-food-recommender')
        blob_name = f'data/{list_id}.json'
        new_blob = storage_client.bucket(bucket_name).blob(blob_name)
        new_blob.upload_from_string(json.dumps(data))
        return {'status': 'success',
                'message': 'Food recommender list saved successfully',
                'data': {'listId': list_id}}, 200
