"""Module for finscraper demonstration."""


import base64
import functools
import io
import os

from flask import jsonify
from itsdangerous import Signer

from finscraper.spiders import ISArticle, ILArticle, VauvaPage, Suomi24Page, \
    ToriDeal


SPIDERS = [
    # TODO: Not working fully with finscraper==0.2.1
    # {
    #     'text': 'YLE news articles',
    #     'value': 'ylearticle',
    #     'class': YLEArticle
    # },
    {
        'text': 'Ilta-Sanomat news articles',
        'value': 'isarticle',
        'class': ISArticle
    },
    {
        'text': 'Iltalehti news articles',
        'value': 'ilarticle',
        'class': ILArticle
    },
    {
        'text': 'Vauva.fi discussion threads',
        'value': 'vauvapage',
        'class': VauvaPage
    },
    {
        'text': 'Suomi24 discussion threads',
        'value': 'suomi24page',
        'class': Suomi24Page
    },
    {
        'text': 'Tori deals',
        'value': 'torideal',
        'class': ToriDeal
    }
]


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


@request_wrapper(allowed_methods=['OPTIONS', 'POST', 'GET'])
def finscraper(request):
    """Scrape content from popular Finnish websites with finscraper."""
    if request.method == 'GET':
        print('Returning spider metadata...')
        return {'status': 'success',
                'message': 'Spider metadata obtained successfully!',
                'data': [{'text': s['text'], 'value': s['value']}
                         for s in SPIDERS]}, 200
    elif request.method == 'POST':
        print('Fetching content with finscraper...')
        data = request.get_json()['data']
        print(f'Parameters:\n{data}')
        spider_cls = [s['class'] for s in SPIDERS
                      if s['value'] == data['spider']][0]
        spider = (spider_cls(progress_bar=False, log_level='info')
                  .scrape(data['nItems'], timeout=data['timeout']))
        items = spider.get('list')
        print('Converting Excel...')
        buffer = io.BytesIO()
        spider.get().to_excel(buffer, index=False)
        buffer.seek(0)
        excel_b64 = base64.b64encode(buffer.read()).decode('utf-8')
        print('Results ready!')
        return {'status': 'success',
                'message': 'Scraped items obtained successfully!',
                'data': {'items': items, 'excel': excel_b64}}, 200
