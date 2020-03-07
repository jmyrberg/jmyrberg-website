"""Module for getting food recommender data."""


import functools
import json
import os
import tempfile

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
            # Request legitimity
            headers = None
            if request.method not in allowed_methods:
                return jsonify({'status': 'error',
                                'message': 'Method not allowed',
                                'data': None}), 403
            if request.method == 'OPTIONS':
                headers = {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': allowed_methods,
                    'Access-Control-Allow-Headers': ['Content-Type',
                                                     'x-api-key'],
                    'Access-Control-Max-Age': '3600',
                }
                return ('', 204, headers)
            else:
                headers = {'Access-Control-Allow-Origin': '*'}
            # Token
            api_key = request.headers.get('X-API-KEY')
            if not api_key:
                return jsonify({'status': 'error',
                                'message': 'Missing "x-api-key" header',
                                'data': None}), 401
            else:
                try:
                    Signer(os.environ['SECRET_KEY']).unsign(api_key)
                except Exception:
                    return jsonify({'status': 'error',
                                    'message': 'Invalid access token',
                                    'data': None}), 401
            # Function call or error
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


@request_wrapper(allowed_methods=['GET', 'OPTIONS'])
def get_food_recommender(request):
    """Get existing food recommender list."""
    list_id = request.args.get('listId')
    if not list_id:
        raise ValueError('Query parameter "listId" must be provided')

    if os.getenv('ENV', 'production') == 'local':
        expected_path = (
            Path(tempfile.gettempdir()) / 'jmyrberg-food-recommender' /
            'data' / f'{list_id}.json')
        if expected_path.exists():
            with open(expected_path, 'r') as f:
                data = json.load(f)
            return {'status': 'success',
                    'message': 'Food recommender list fetched successfully',
                    'data': data}, 200
        else:
            return {'status': 'error',
                    'message': (f'Food recommender list "{list_id}"'
                                ' could not be found'),
                    'data': None}, 404
    else:
        global storage_client
        if not storage_client:
            storage_client = Client()
        bucket_name = os.getenv('FOOD_RECOMMENDER_BUCKET_NAME',
                                'jmyrberg-food-recommender')
        blob_name = f'/data/{list_id}.json'
        blob = storage_client.bucket(bucket_name).get_blob(blob_name)
        if blob:
            data = json.loads(blob.download_as_string())
            return {'status': 'success',
                    'message': 'Food recommender list fetched successfully',
                    'data': data}, 200
        else:
            return {'status': 'error',
                    'message': (f'Food recommender list "{list_id}"'
                                ' could not be found'),
                    'data': None}, 404
