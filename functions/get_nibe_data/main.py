'''Module for getting Nibe myUplink data.'''


import json
import os
import tempfile
import time
import requests

from datetime import datetime
from pathlib import Path

from google.cloud.storage.client import Client


HOME_DATA_BUCKET_NAME = os.environ['HOME_DATA_BUCKET_NAME']
NIBE_CLIENT_ID = os.environ['NIBE_CLIENT_ID']
NIBE_CLIENT_SECRET = os.environ['NIBE_CLIENT_SECRET']
NIBE_DEVICE_ID = os.environ['NIBE_DEVICE_ID']
NIBE_PARAMETER_IDS = [
    '40004',  # Nykyi­nen ulkoläm­pötila (BT1)
    '40008',  # Meno­johto (BT2)
    '40012',  # Return line (BT3)
    '40013',  # Käyttö­vesi yläosa (BT7)
    '40014',  # Käyttö­vesi lataus (BT6)
    '40020',  # Höy­rystin (BT16)
    '40023',  # Kompres­sorin anturi (BT18)
    '40024',  # Sähkö­vastus­anturi (BT19)
    '40025',  # Poisto­ilma (BT20)
    '40026',  # Ulos­puhal­lusilma (BT21)
    '40033',  # Huone­lämpö­tila (BT50)
    '40067',  # Keski­ulkoläm­pötila (BT1)
    '40072',  # Virtaus­anturi (BF1)
    '40075',  # Supply air (BT22)
    '40079',  # Virta (BE3)
    '40081',  # Virta (BE2)
    '40083',  # Virta (BE1)
    '42096',  # Supply air fan speed
    '42770',  # Haluttu ilman­kosteus
    '43009',  # Lasket­tu meno­lämpö­tila lämmi­tyksen alajako­piiri 1
    '43066',  # Sulatus­aika
    '43081',  # Aika­kerroin lisä­lämmön­lähde
    '43108',  # Nykyi­nen puhalti­men tila
    '43109',  # Nykyi­nen lämmin­vesitila
    '43416',  # Kompr. käynnis­tyksiä
    '43420',  # Käynti­aika
    '43424',  # Käyttö­veden tuotanto­aika
    '43427',  # Tila kompres­sori
    '47015',  # lämmitysjärjestelmä
    '50221',  # Exhaust air fan speed
]

storage_client = None


class Nibe:

    BASE_URL = 'https://api.myuplink.com'

    def __init__(self):
        self.access_token = self.get_access_token()

        self.sess = requests.Session()
        self.sess.headers.update({
            'Authorization': f'Bearer {self.access_token}',
            'Accept-Language': 'fi-FI'
        })

    def get_access_token(self):
        return requests.post(
            f'{self.BASE_URL}/oauth/token',
            auth=(NIBE_CLIENT_ID, NIBE_CLIENT_SECRET),
            data={
                'grant_type': 'client_credentials',
                'scope': 'READSYSTEM'
            }
        ).json()['access_token']

    def save_json(self, data, blob_name):
        if os.getenv('ENV', 'production') == 'local':
            expected_path = (Path(tempfile.gettempdir())
                             / HOME_DATA_BUCKET_NAME / blob_name)
            expected_path.parent.mkdir(exist_ok=True, parents=True)
            with open(expected_path, 'w') as f:
                data = json.dump(data, f)
                print(f'Saved {len(data)} points into {str(expected_path)}!')
        else:
            global storage_client
            if not storage_client:
                storage_client = Client()
            blob = storage_client.bucket(HOME_DATA_BUCKET_NAME).blob(blob_name)
            blob.upload_from_string(json.dumps(data),
                                    content_type='application/json')

            print(f'Saved {len(data)} points into {blob_name}!')


    def get_points(self):
        now_timestamp = int(time.time())
        resp = self.sess.get(
            f'{self.BASE_URL}/v2/devices/{NIBE_DEVICE_ID}/points',
            params={'parameters': ','.join(NIBE_PARAMETER_IDS)}
        )
        if not resp.ok:
            raise ValueError(f'Response status code: {resp.status_code}')

        points = [{
            'metric': p['parameterId'],
            'timestamp': int(datetime.fromisoformat(p['timestamp']).timestamp()),
            'value': p['value']
        } for p in resp.json()]

        assert len(points) > 0, 'Something wrong with the response :('
    
        self.save_json(points, blob_name=f'nibe/points/{now_timestamp}.json')

        return points


def get_nibe_data(data, context):
    '''Get points from Nibe myUplink.'''
    nibe = Nibe()
    data = nibe.get_points()
    return {'status': 'success',
            'message': 'Nibe data saved successfully',
            'data': data}, 200
