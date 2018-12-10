#!/usr/bin/env python

# Copied from https://github.com/FarmBot-Labs/farmware-tools

'''Farmware Tools.'''

import os
import json
import requests
from time import sleep

debug = False

"""
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
        requests.post(
            url + 'api/v1/celery_script',
            #headers={'Authorization': 'Bearer ' + token,
                     #'content-type': 'application/json'},
            headers = {'Authorization': 'bearer {}'.format(token),
                       'content-type': "application/json"},
            data=json.dumps(command))
    return True
"""

def send_celery_script(ret):
        try:
            status_code = ret.status_code
        except:
            status_code = -1
        try:
            text = ret.text[:100]
        except:
            text = ret
        if status_code == -1 or status_code == 200:
            if self.input_debug >= 1: log("{} -> {}".format(status_code,text), message_type='debug', title="jhempbot")
        else:
            log("{} -> {}".format(status_code,text), message_type='error', title="jhempbot")
            raise

def log(message, message_type='info'):
    'Send a send_message command to post a log to the Web App.'
    send_celery_script({
        'kind': 'send_message',
        'args': {
            'message': message,
            'message_type': message_type}})

if __name__ == '__main__':
    log('Hello World!', 'success')
