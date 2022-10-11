"""Module for forecaster.

Target: Keep it as simple and as fast as possible

Minimum inputs:
- Data contents
- Identify date column
- Identify frequency
- Identify numeric column (take first in first phase)

Forecasting steps:
1) User inputs an Excel or CSV file (UI)
2) Send content straight away to API `check_inputs`
    A): Try parse automatically and everything OK
        => respond to UI with "Configuration OK"
        => 
    B): Try parse automatically and fail / warnings
        => respond with noticed errors, ask user to provide inputs
3 A) Show "forecasting" view in UI
3 B) Show "configuration view" in UI and send data with given configuration
4)

TODO:
- Warnings
    - File size limit
    - Number of rows limit
- Ad-hoc tokenization / recaptcha based on time and data etc.
- xaxis label in wrong place?
- Fine-tune all formatting and responsiveness
"""


import base64
import functools
import io
import json
import os
import traceback

import numpy as np

from flask import jsonify
from itsdangerous import Signer

from statsforecast import StatsForecast
from statsforecast.models import AutoARIMA

from utils import *


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
                traceback.print_exc()
                return jsonify({'status': 'error',
                                'message': str(e),
                                'data': None}), 500, headers

        return wrapped_func

    if original_func:
        return _decorate(original_func)

    return _decorate


@request_wrapper(allowed_methods=['OPTIONS', 'POST'])
def forecaster(request):
    """TODO"""
    mode = request.form['mode']
    data = {}

    # Get sample file
    if mode == 'sampleFile':
        if os.getenv('ENV', 'production') == 'local':
            cur_dir = os.path.dirname(os.path.realpath(__file__))
            os.chdir(cur_dir)

        print('Converting Excel...')
        buffer = io.BytesIO()
        df = pd.read_excel('./sample-data.xlsx').to_excel(buffer, index=False)
        buffer.seek(0)
        excel_b64 = base64.b64encode(buffer.read()).decode('utf-8')
        return {'status': 'success',
                'message': 'Sample file obtained successfully!',
                'data': {'excel': excel_b64}}, 200

    # Read inputs as df
    file = request.files['inputFile']
    filename = file.filename
    df = read_file(file, filename)

    if mode == 'prepare':
        # Find date and numeric column
        df = convert_date_cols(df)
        freqs = find_freqs(df)
        df = convert_num_cols(df)

        # Format results
        cols = [{
            'value': col,
            'dtype': dt.name,
            'dtypeName': humanize_dtype(dt.name),
            'freq': freqs.get(col)
        } for col, dt in df.dtypes.to_dict().items()]
        data['columns'] = cols

        return {'status': 'success',
                'message': 'Solution obtained successfully!',
                'data': data}, 200
    elif mode == 'forecast':
        print('Parsing input data...')
        params = json.loads(request.files['params'].read())
        target_col = params['selectedForecastCol']
        date_col = params['selectedDateCol']
        freq = params['selectedDateColFreq']
        horizon = params['horizon']

        # Preprocess
        print('Preprocessing...')
        use_rank_idx = date_col == '(auto)'
        if use_rank_idx:  # Special, use index instead of date
            df[date_col] = np.arange(len(df))
        else:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')

        df = (
            df[[date_col, target_col]]
            .rename(columns={date_col: 'ds', target_col: 'y'})
            .assign(unique_id=0,
                    y=lambda df_: pd.to_numeric(df_['y'], errors='coerce'))
            [['unique_id', 'ds', 'y']]
        )

        # Forecast
        print('Forecasting...')
        models = [AutoARIMA()]
        model = StatsForecast(df=df,  models=models, freq=freq)
        yhat = (
            model.forecast(horizon, level=[90])
            .rename(columns={
                'AutoARIMA': 'forecast',
                'AutoARIMA-lo-90': 'lower_bound',
                'AutoARIMA-hi-90': 'upper_bound'
            })
            .reset_index()
        )

        # Postprocess
        print('Postprocess...')
        res = (
            pd.concat([df, yhat], axis=0)
            .rename(columns={'ds': date_col, 'y': target_col})
            .drop('unique_id', axis=1)
            .reset_index(drop=True)
        )

        # Format results with history
        print('Formatting...')
        dates = json.loads(
            res[date_col].to_json(orient='values', date_format='iso'))
        series = [
            {'name': target_col,
             'data': json.loads(res[target_col].to_json(orient='values'))},
            {'name': 'Forecast',
             'data': json.loads(res['forecast'].to_json(orient='values'))},
            {'name': 'Lower bound',
             'data': json.loads(res['lower_bound'].to_json(orient='values'))},
            {'name': 'Upper bound',
             'data': json.loads(res['upper_bound'].to_json(orient='values'))}
        ]
        data['forecast'] = {
            'series': series,
            'dates': dates,
            'xAxisType': 'numeric' if use_rank_idx else 'datetime'
        }

        return {'status': 'success',
                'message': 'Forecast obtained successfully!',
                'data': data}, 200
