"""Module for maximum flows."""


import functools
import os
import smtplib

from flask import jsonify
from itsdangerous import Signer


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
            elif request.method == 'POST':
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
def contact(request):
    """Send contact email."""    
    print('Starting to send contact email...')
    
    data = request.get_json()['data']
    
    _from = os.environ['MAIL_USERNAME']
    to = os.environ['MAIL_TO']
    subject = f"Message from {data['name']} (jmyrberg-website)"
    content = (f"Name: {data['name']}\n\n"
               f"Email: {data['email']}\n\n"
               f"Message:\n{data['message']}")
    _message = f'From: {_from}\nTo: {to}\nSubject: {subject}\n\n{content}'

    try:
        server = smtplib.SMTP(os.environ['MAIL_SERVER'])
        server.ehlo()
        server.starttls()
        server.login(os.environ['MAIL_USERNAME'], os.environ['MAIL_PASSWORD'])
        server.sendmail(_from, to, _message)
        server.close()
        status = 'success'
        message = 'Email sent successfully'
        status_code = 200
    except Exception as e:
        status = 'error'
        message = str(e)
        status_code = 500

    return {'status': status, 'message': message, 'data': None}, status_code
