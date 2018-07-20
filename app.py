import os
import requests


def get_ip():
    '''
    Search my public IP address
    '''
    r = requests.get('http://dyn.value-domain.com/cgi-bin/dyn.fcg?ip')
    ip = r.text
    return ip


def coreserver_ssh(SERVER_NAME, ACCOUNT, API_KEY):
    '''
    SSH connection IP permission to CORE SERVER
    '''
    IP = get_ip()
    URL = 'https://api.coreserver.jp/v1/tool/ssh_ip_allow'

    payload = {
        'account': ACCOUNT,
        'server_name': SERVER_NAME,
        'api_secret_key': API_KEY,
        'param[addr]': IP
    }
    
    r = requests.post(URL, data=payload)
    print(r.text)


if __name__ == '__main__':
    SERVER_NAME = 'x0000.coreserver.jp'
    ACCOUNT = 'xxx'
    API_KEY = os.environ['CORESERVER_API_KEY']

    coreserver_ssh(SERVER_NAME, ACCOUNT, API_KEY)