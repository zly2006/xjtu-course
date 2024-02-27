import base64
import encodings.utf_8
import json
import os
import time

import requests.cookies
import requests.utils
from Crypto.Cipher import AES

user: str = ''
password: str = ''
member_id: str = ''
token_key: str = ''

header = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.50'
}


def get_data(s: str) -> json:
    o = json.loads(s)
    if int(o['code']) not in (0, 1):
        raise Exception('error code: {0}\n{1}'.format(o['code'], o))
    return o['data']


def encode_password(p: str) -> str:
    key = b'0725@pwdorgopenp'  # 你这加密和加了似的
    aes = AES.new(key, AES.MODE_ECB)
    [bs, count] = encodings.utf_8.encode(p)
    ba = bytearray(bs)
    # padding
    padding = (AES.block_size - count % AES.block_size).to_bytes(1, byteorder='little')[0]
    for i in range(padding):
        ba.append(padding)
    return base64.b64encode(aes.encrypt(ba)).decode()


if __name__ == '__main__':
    jsonDecoder = json.JSONDecoder()
    opener = requests.Session()
    opener.headers.update(header)

    if not os.path.exists('accounts.txt'):
        with open('accounts.txt', 'w') as f:
            f.write('<number>\n')
            f.write('<password>\n')
    with open('accounts.txt', 'r') as f:
        user = f.readline().strip()
        password = f.readline().strip()
        token_key = f.readline().strip()
        member_id = f.readline().strip()
    if member_id == '' or token_key == '':
        print('member_id or token_key is empty, login start')
        body = opener.get('http://xkfw.xjtu.edu.cn/xsxkapp/sys/xsxkapp/*default/index.do', headers=header)
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
            f'http://org.xjtu.edu.cn/openplatform/oauth/auth/getRedirectUrl?userType=1&personNo={user}&_={int(time.time() * 1000)}',
            headers=header,
        )
        redirect_url = get_data(body.text)
        opener.get(redirect_url)
        with open('accounts.txt', 'w') as f:
            f.write('{0}\n{1}\n{2}\n{3}\n'.format(user, password, token_key, member_id))
        with open('cookie.json', 'w') as f:
            f.write(json.dumps(requests.utils.dict_from_cookiejar(opener.cookies)))
        print('Login success')
    else:
        opener.cookies = requests.utils.cookiejar_from_dict(json.loads(open('cookie.json', 'r').read()))
    # Query course
    body = opener.get(
        f'http://xkfw.xjtu.edu.cn/xsxkapp/sys/xsxkapp/elective/batch.do?timestamp={int(time.time() * 1000)}',
    )
    batchList = body.json()['dataList']  # 选课批次
    for i in range(len(batchList)):
        print(i, '->', batchList[i]['name'], batchList[i]['typeName'])
    code = batchList[int(input('选择选课批次 = '))]['code']
    body = opener.get(f'https://xkfw.xjtu.edu.cn/xsxkapp/sys/xsxkapp/student/register.do?number={user}')
    name = body.json()['data']['name']
    token = body.json()['data']['token']
    print(user, name, token)
    body = opener.post('https://xkfw.xjtu.edu.cn/xsxkapp/sys/xsxkapp/student/xkxf.do', data={
        'xklcdm': code,
        'xh': str(user),
        'xklclx': '01',  # 这是啥?
    }, headers={
        'token': token
    })
    data = get_data(body.text)
    print(data['collegeName'], data["campusName"], data["schoolClass"], data["schoolClassName"])
    print(body.text)
