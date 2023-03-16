from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import requests
import base64
import hashlib
import random
import re
import string
import webbrowser

Session = requests.Session()
Retrier = Retry(total=3, read=3, connect=3, backoff_factor=0.3, status_forcelist=(500, 502, 504))
adapter = HTTPAdapter(max_retries=Retrier)
Session.mount('http://', adapter)
Session.mount('https://', adapter)
JWToken = re.compile(r'(eyJhbGciOiJIUzI1NiJ9\.[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*)')
ClientID = '71b963c1b7b6d119'

class Login(object):
    def __init__(self):
        self.session_token = self.login()

    def rand(self):
        return ''.join(random.choice(string.ascii_letters) for _ in range(50))

    def hash(self, text):
        text = hashlib.sha256(text.encode()).digest()
        text = base64.urlsafe_b64encode(text).decode()
        return text.replace('=', '')

    def login(self):
        verifier = self.rand()
        headers = {
            'Accept-Encoding': 'gzip',
            'User-Agent': 'OnlineLounge/1.0.4 NASDKAPI Android'
        }
        url = 'https://accounts.nintendo.com/connect/1.0.0/authorize'
        payload = {
            'client_id'                           : ClientID,
            'redirect_uri'                        : 'npf{}://auth'.format(ClientID),
            'response_type'                       : 'session_token_code',
            'scope'                               : 'openid user user.birthday user.mii user.screenName',
            'session_token_code_challenge'        : self.hash(verifier),
            'session_token_code_challenge_method' : 'S256',
            'state'                               : self.rand(),
            'theme'                               : 'login_form'
        }
        content = requests.Request('GET', url, params=payload, headers=headers).prepare()
        webbrowser.open(content.url)


        token_code = JWToken.findall(input('Please paste the link of "Use this account" button here after login:\n'))[0]
        url = 'https://accounts.nintendo.com/connect/1.0.0/api/session_token'
        payload = {
            'client_id': ClientID,
            'session_token_code': token_code,
            'session_token_code_verifier': verifier
        }
        content = Session.post(url, data=payload, headers=headers).json()
        return content['session_token']
