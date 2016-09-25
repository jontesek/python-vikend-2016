import json

import requests


class SmsMailer(object):

    def __init__(self, client_id, client_secret):
        post_data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'client_credentials',
        }
        a_token = requests.post('https://app.gosms.cz/oauth/v2/token', post_data).text
        self.a_token = json.loads(a_token)['access_token']

    def send_sms(self, msg, to_mobile, test_mode=True):
        post_data = {
            'message': msg,
            'recipients': to_mobile,
            'channel': 185270,
            #'expectedSendStart': ''
        }
        endpoint_url = 'https://app.gosms.cz/api/v1/messages/test' if test_mode else 'https://app.gosms.cz/api/v1/messages'
        result = requests.post('{0}?access_token={1}'.format(endpoint_url, self.a_token), json.dumps(post_data))
        return result.status_code
