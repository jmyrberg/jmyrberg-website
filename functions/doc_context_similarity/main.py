"""Module for Next Sentence Prediction."""


import functools
import os

from flask import jsonify
from itsdangerous import Signer

import torch
import transformers


model = None

tokenizer = None


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


@request_wrapper(allowed_methods=['OPTIONS', 'POST'])
def doc_context_similarity(request):
    """Predict probability of two documents appearing in the same context."""
    print('Starting document context similarity prediction...')
    global model, tokenizer

    # If ENV == 'local', assume model downloaded under ./ext/model from
    # https://huggingface.co/TurkuNLP/bert-base-finnish-cased-v1/tree/main
    if not tokenizer:
        print('Loading tokenizer...')
        if os.getenv('ENV', '') == 'local':
            # TODO: Think about whether to keep the cased or uncased?
            tokenizer = transformers.BertTokenizer(
                './ext/model/vocab.txt', do_lower_case=False)
        else:
            tokenizer = (transformers.BertTokenizer.from_pretrained(
                'TurkuNLP/bert-base-finnish-cased-v1'))
        print('Tokenizer loaded!')

    if not model:
        print('Loading model...')
        model_path = ('./ext/model' if os.getenv('ENV', '') == 'local'
                      else 'TurkuNLP/bert-base-finnish-cased-v1')
        model = (transformers.BertForNextSentencePrediction
                 .from_pretrained(model_path))
        model.eval()
        print('Model loaded!')

    print('Predicting...')
    data = request.get_json()['data']

    # Parse data
    doc1 = data['doc1']
    doc2 = data['doc2']

    print(f'Document 1:\n{str(doc1)}')
    print(f'Document 2:\n{str(doc2)}')

    # Inference
    tokens1 = ['[CLS]'] + tokenizer.tokenize(doc1) + ['[SEP]']
    tokens2 = tokenizer.tokenize(doc2) + ['[SEP]']
    tokens = tokens1 + tokens2

    indexed_tokens = tokenizer.convert_tokens_to_ids(tokens)
    segments_ids = [0] * len(tokens1) + [1] * len(tokens2)

    tokens_tensor = torch.tensor([indexed_tokens])
    segments_tensors = torch.tensor([segments_ids])

    pred = model(tokens_tensor, token_type_ids=segments_tensors)[0]
    probability = float(torch.nn.Softmax(dim=1)(pred).data.numpy()[0][0])
    print(f'Probability: {probability}')

    print('Prediction done!')
    return {'status': 'success',
            'message': 'Prediction obtained successfully!',
            'data': {'probability': probability}}, 200
