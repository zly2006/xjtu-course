import base64
import encodings
import json
import os
import time

import requests
import requests.utils
from Crypto.Cipher import AES
from requests import Session

from main import get_data


def encode_password(p: str) -> str:
    key = b'0725@pwdorgopenp'  # 你这加密和加了似的
    aes = AES.new(key, AES.MODE_ECB)
    [bs, count] = encodings.utf_8.encode(p)
    ba = bytearray(bs)
    padding = (AES.block_size - count % AES.block_size).to_bytes(1, byteorder='little')[0]
    for i in range(padding):
        ba.append(padding)
    return base64.b64encode(aes.encrypt(ba)).decode()


def login(endpoint: str) -> tuple[Session, str]:
    opener = requests.Session()
    opener.headers = {
        'User-Agent': 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
    }

    if not os.path.exists('accounts.txt'):
        with open('accounts.txt', 'w') as f:
            f.write('<number>\n')
            f.write('<password>\n')
        print('Please fill in your account and password in accounts.txt')
        exit(0)
    with open('accounts.txt', 'r') as f:
        user = f.readline().strip()
        password = f.readline().strip()
        token_key = f.readline().strip()
        member_id = f.readline().strip()
    print('member_id or token_key is empty, login start')
    body = opener.get(endpoint)
    print('redirect done', body.url, 'cookies', opener.cookies.get_dict())
    body = opener.get(
        'https://org.xjtu.edu.cn/openplatform/g/admin/getAppNameAndAdminContent?_=1709023016389&__={0}'.format(
            int(time.time() * 1000)),
    )
    app_name = get_data(body.text)['appName']
    print('app_name: {0}'.format(app_name))
    # Login
    body = opener.post('http://org.xjtu.edu.cn/openplatform/g/admin/login', json={
        'jcaptchaCode': '',
        'loginType': 1,
        'username': user,
        'pwd': encode_password(password),
    }, )
    login_data = get_data(body.text)
    member_id = login_data['orgInfo']['memberId']
    token_key = login_data['tokenKey']
    opener.cookies.update({
        'open_Platform_User': token_key,
        'memberId': str(member_id)
    })
    body = opener.get(
        f'http://org.xjtu.edu.cn/openplatform/oauth/auth/getRedirectUrl?userType=1&personNo={user}&_={int(time.time() * 1000)}')
    redirect_url = get_data(body.text)
    opener.get(redirect_url)
    with open('accounts.txt', 'w') as f:
        f.write('{0}\n{1}\n{2}\n{3}\n'.format(user, password, token_key, member_id))
    with open('cookie.json', 'w') as f:
        f.write(json.dumps(requests.utils.dict_from_cookiejar(opener.cookies)))
    print('Login success')

    return opener, user
