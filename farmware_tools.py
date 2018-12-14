#!/usr/bin/env python

# Copied from https://github.com/FarmBot-Labs/farmware-tools

'''Farmware Tools.'''

import os
import json
import requests
from time import sleep
debug = False

def send_celery_script(command):
    'Send a celery script command.'
    #start debug
    if debug == True:
        print(command)
        if command["kind"] == "wait":
            sleep(command["args"]["milliseconds"]//1000)
        return
    #end debug
    try:
        url = os.environ['FARMWARE_URL']
        token = os.environ['FARMWARE_TOKEN']
    except KeyError:
        print(command)
    else:
        ret = requests.post(
            url + 'api/v1/celery_script',
            headers={'Authorization': 'Bearer ' + token,
                     'content-type': 'application/json'},
            data=json.dumps(command))
        
        return 0

def log(message, message_type='info'):
    'Send a send_message command to post a log to the Web App.'
    send_celery_script({
        'kind': 'send_message',
        'args': {
            'message': message,
            'message_type': message_type}})

if __name__ == '__main__':
    log('Hello World!', 'success')
