import json
import time

import login

user: str = ''
password: str = ''
member_id: str = ''
token_key: str = ''


def get_data(s: str) -> json:
    o = json.loads(s)
    if int(o['code']) not in (0, 1):
        raise Exception('error code: {0}\n{1}'.format(o['code'], o))
    return o['data']


if __name__ == '__main__':
    opener = login.login('http://xkfw.xjtu.edu.cn/xsxkapp/sys/xsxkapp/*default/index.do')
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
    if body.json()['code'] == '2':
        print('选课平台register失败')
    body = opener.get(f'https://xkfw.xjtu.edu.cn/xsxkapp/sys/xsxkapp/elective/courseResult.do?studentCode={user}&electiveBatchCode={code}', headers={
        'token': token
    })
    print(body.text)
