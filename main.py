import json
import time
import traceback
from datetime import datetime

import requests


def on_danmu_get(user, text, create_at):
    print(f'{create_at}({create_at.timestamp()}) {user}: {text}')


def main():
    print('检查cookie中')
    with open('cookie.txt', 'r', encoding='utf-8') as f:
        cookie = f.read()

    if len(cookie) < 10:
        notify_set_cookie()
        return

    header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36',
        'cookie': cookie
    }
    proxies = {"http": None, "https": None}

    try:
        resp = requests.get('https://weibo.com/easonch', headers=header, proxies=proxies)
    except:
        notify_set_cookie()
        return
    if 'Sina Visitor System' in resp.text:
        notify_set_cookie()
        return

    print('cookie检验完成')
    print('请输入mid：')
    mid = input()

    max_id = '0'
    retry = 0
    while True:
        uri = f'https://weibo.com/ajax/statuses/buildComments?flow=1&is_reload=1&id={mid}' \
              f'&is_show_bulletin=2&is_mix=0&count=20&max_id={max_id}&fetch_level=0'
        if retry > 5:
            break
        try:
            time.sleep(1)
            resp = requests.get(uri, headers=header, proxies=proxies, verify=False)
            json_root = json.loads(resp.text)
            data = json_root['data']
            for comment in data:
                text = replace_emoji_and_at(comment['text'])
                create_at = comment['created_at']
                create_at = datetime.strptime(create_at, '%a %b %d %H:%M:%S %z %Y')
                user = comment['user']['screen_name']
                on_danmu_get(user, text, create_at)

            if 'max_id' in json_root:
                max_id = json_root['max_id']
                retry = 0
        except KeyboardInterrupt:
            break
        except:
            traceback.print_exc()
            retry += 1


def replace_emoji_and_at(text: str) -> str:
    while '<img' in text or '</a' in text:
        img_index = text.find('<img')
        a_index = text.find('<a')
        if img_index != -1 and a_index == -1:
            # 只包含Emoji
            text = replace_img(text)
        elif img_index == -1 and a_index != -1:
            # 只包含@
            text = replace_a(text)
        else:
            # 既包含Emoji又包含@
            if img_index < a_index:
                # Emoji在前面
                text = replace_img(text)
            else:
                # @在前面
                text = replace_a(text)
    return text


def replace_img(text: str) -> str:
    img = text[text.find('<img'):text.find('/>')+2]
    if 'title="' in img:
        emoji = img[img.find('title="')+7:]
        emoji = emoji[:emoji.find('"')]
        return text.replace(img, emoji)
    elif 'title=\\"' in img:
        emoji = img[img.find('title=\\"') + 8:]
        emoji = emoji[:emoji.find('\\"')]
        return text.replace(img, emoji)
    else:
        return text.replace(img, '')


def replace_a(text: str) -> str:
    a = text[text.find('<a'):text.find('/a>')+3]
    if '@' in a:
        at = a[a.find('>')+1:a.find('/a>')]
        return text.replace(a, at)
    else:
        return text.replace(a, '')


def notify_set_cookie():
    print('请设置 cookie.txt')
    print('具体做法：')
    print('1. 使用 Chrome 或 Edge 等带开发者工具的浏览器打开微博(https://weibo.com)，注意不是.cn而是.com')
    print('2. 登录网页版微博，建议使用小号，虽然目前没有因使用本工具被封号的案例，但以防万一')
    print('3. 登录后，回到微博主页(https://weibo.com)')
    print('4. 按键盘上的 F12 按键，打开开发者工具')
    print('5. 在弹出的页面上方的标签 [元素(Elements)][命令行(Console)][...][网络(Network)] 中，选择[网络(Network)]')
    print('6. 刷新网页')
    print('7. 能看到网络(Network)标签下的抓包列表中，滑到最上面，点击第一个(weibo.cn)，在右方下滑找到 cookie，将其内容复制到 cookie.txt 中')
    print('8. 重新启动该软件')


if __name__ == '__main__':
    main()
