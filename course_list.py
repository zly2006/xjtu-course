import login

if __name__ == "__main__":
    opener = login.login('https://ehall.xjtu.edu.cn/jwapp/sys/wdkb/*default/index.do')
    body = opener.post("https://ehall.xjtu.edu.cn/jwapp/sys/wdkb/modules/xskcb/xskcb.do")
    print(body.text)

