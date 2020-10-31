"""Module for fetching Nibe Uplink data."""


import functools
import json
import os
import re
import tempfile
import time
import traceback

from pathlib import Path

import bs4
import requests

from google.cloud.storage.client import Client


HOME_DATA_BUCKET_NAME = os.environ['HOME_DATA_BUCKET_NAME']

storage_client = None


class Nibe:

    BASE_URL = 'https://www.nibeuplink.com'
    
    def __init__(self, email, password, hpid):
        """Fetching data from Nibe Uplink."""
        self.email = email
        self.password = password
        self.hpid = hpid
        
        self.sess = requests.Session()
        
        data = {'Email': self.email, 'Password': self.password}
        self.sess.post(f'{self.BASE_URL}/LogIn', data)
        
    def get_previous_history_timestamp(self):
        timestamp = None
        if os.getenv('ENV', 'production') == 'local':
            expected_path = (Path(tempfile.gettempdir())
                             / HOME_DATA_BUCKET_NAME /
                             'nibe/history/previous_timestamp.txt')
            if expected_path.exists():
                with open(expected_path, 'r') as f:
                    timestamp = int(json.load(f)[0])
        else:
            global storage_client
            if not storage_client:
                storage_client = Client()
            blob_name = 'nibe/history/previous_timestamp.txt'
            blob = (storage_client.bucket(HOME_DATA_BUCKET_NAME)
                    .get_blob(blob_name))
            if blob:
                timestamp = int(json.loads(blob.download_as_string())[0])

        return timestamp
    
    def save_json(self, data, blob_name):
        if os.getenv('ENV', 'production') == 'local':
            expected_path = (Path(tempfile.gettempdir())
                             / HOME_DATA_BUCKET_NAME / blob_name)
            expected_path.parent.mkdir(exist_ok=True, parents=True)
            with open(expected_path, 'w') as f:
                data = json.dump(data, f)
                print(f'Saved into {str(expected_path)}!')
        else:
            global storage_client
            if not storage_client:
                storage_client = Client()
            blob = storage_client.bucket(HOME_DATA_BUCKET_NAME).blob(blob_name)
            blob.upload_from_string(json.dumps(data),
                                    content_type='application/json')
            print(f'Saved into {blob_name}!')
        
    def get_available_history_metrics(self):
        page = self.sess.get(f'{self.BASE_URL}/System/{self.hpid}/History').text
        btns = bs4.BeautifulSoup(page, 'html.parser').find_all('input')
        metrics = [btn.attrs.get('id') for btn in btns
                   if btn.attrs.get('id').isnumeric()]
        return metrics

    def get_metric_history(self, metric, start, end, resolution=1000):
        data = {
            'hpid': self.hpid,
            'variableId': metric,
            'startDate': start,
            'stopDate': end,
            'resolution': resolution
        }
        res = self.sess.post(f'{self.BASE_URL}/PrivateAPI/History', data).json()

        return res
    
    def get_history(self):
        end = int(time.time())
        start = (self.get_previous_history_timestamp()
                 or (end - 60 * 60 * 24 * 366))
        start += 1
        metrics = self.get_available_history_metrics()
        
        print(f'Fetching history from {start} to {end} for {metrics}...')
        
        data = []
        for metric in metrics:
            metric_dict = self.get_metric_history(metric, start, end)
            for timestamp, value in metric_dict['data']:
                timestamp = int(timestamp // 1000)
                if (timestamp >= start) and (timestamp <= end):
                    data.append({
                        'metric': metric,
                        'timestamp': timestamp,
                        'value': value,
                        'label': metric_dict['label'],
                        'unit': metric_dict['unit']
                    })
        
        if len(data) > 0:
            self.save_json(data, f'nibe/history/{start}-{end}.json')
            self.save_json([end], f'nibe/history/previous_timestamp.txt')
        else:
            print('Nothing to write :(')

        return data
    
    def get_status(self):
        timestamp = int(time.time())
        
        print(f'Fetching status for {timestamp}...')
        
        resp = self.sess.get(
            f'{self.BASE_URL}/System/{self.hpid}/Status/ServiceInfo')
        soup = bs4.BeautifulSoup(resp.content, 'html.parser')
        
        data = []
        for tr in soup.find_all('tr'):
            try:
                metric = tr.find('span', {'class': lambda x: 'ID' in x}).attrs['class'][1][2:]
                label = re.sub(r'\s+', ' ', tr.find('td').text).strip()
                value_text = tr.find('span', {'class': lambda x: 'AutoUpdate' in x}).text
                if any(c.isnumeric() for c in value_text):
                    value = re.sub(r'[^0-9\.]', '', value_text)
                    value = float(value) if len(value) else None
                    unit = re.sub(r'[0-9\.]', '', value_text)
                else:
                    value = value_text
                    unit = ''
                data.append({
                    'metric': metric,
                    'timestamp': timestamp,
                    'value': value,
                    'label': label,
                    'unit': unit
                })
            except Exception as e:
                pass

        if len(data) > 0:        
            self.save_json(data, f'nibe/status/{timestamp}.json')
        else:
            print('Nothing to write :(')

        return data


def get_nibe_data(data, context):
    """Get status and history datasets from Nibe Uplink."""
    nibe = Nibe(
        email=os.environ['NIBE_EMAIL'],
        password=os.environ['NIBE_PASSWORD'],
        hpid=os.environ['NIBE_HPID']
    )
    status = nibe.get_status()
    history = nibe.get_history()

    return {'status': 'success',
            'message': 'Nibe data saved successfully',
            'data': {'status': status, 'history': history}}, 200
