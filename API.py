import os
import sys
import json
import base64
import requests
import CeleryPy
import re

from CeleryPy import log

class API():     

    def api_setup(self):
         # API requests setup
        try:
            api_token = os.environ['API_TOKEN']
        except KeyError:
            api_token = 'Not Set'
            log('API_TOKEN not set', message_type='error', title='Class API:api_setup')

        try:
            encoded_payload = api_token.split('.')[1]
            encoded_payload += '=' * (4 - len(encoded_payload) % 4)
            json_payload = base64.b64decode(encoded_payload).decode('utf-8')
            server = json.loads(json_payload)['iss']
        except:  
            server = '//my.farmbot.io'

        self.api_url = 'http{}:{}/api/'.format(
            's' if 'localhost' not in server and not re.compile('^//((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)').match(server) else '', server)
        self.headers = {'Authorization': 'Bearer {}'.format(api_token),
                        'content-type': "application/json"}
        
        if self.farmware.input_debug >= 1: log(self.api_url, message_type='debug', title='Class API:api_setup')
        if self.farmware.input_debug >= 1: log(self.headers, message_type='debug', title='Class API:api_setup')
        if self.farmware.input_debug >= 1: log(json_payload, message_type='debug', title='Class API:api_setup')

    def __init__(self,farmware):
        self.farmware = farmware
        self.farmwarename = farmware.farmwarename
        self.api_setup()

    def api_get(self, endpoint):
        """GET from an API endpoint."""
        response = requests.get(self.api_url + endpoint, headers=self.headers)
        self.api_response_error_collector(response)
        self.api_response_error_printer()
        return response.json()
    
    def api_post(self, endpoint, data):
        """POST to an API endpoint."""
        response = requests.post(self.api_url + endpoint, headers=self.headers, json=json.dumps(data))
        self.api_response_error_collector(response)
        self.api_response_error_printer()
        return response.json()

    def api_put(self, endpoint, data):
        response = requests.put(self.api_url + endpoint, headers=self.headers, data=json.dumps(data))
        self.api_response_error_collector(response)
        self.api_response_error_printer()
        return response.json()


    def api_response_error_collector(self, response):
        """Catch and log errors from API requests."""
        self.errors = {}  # reset
        if response.status_code != 200:
            try:
                self.errors[str(response.status_code)] += 1
            except KeyError:
                self.errors[str(response.status_code)] = 1

    def api_response_error_printer(self):
        """Print API response error output."""
        error_string = ''
        for key, value in self.errors.items():
            error_string += '{} {} errors '.format(value, key)
        if error_string != '':
            log(error_string, message_type='error', title='Class API:api_response_error_printer')