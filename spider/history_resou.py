from urllib import parse
import requests
import json
from utils import *


# 获取往日热搜
def get_history_resou(date):
    url = 'https://google-api.zhaoyizhe.com/google-api/index/mon/sec?date=' + date
    header = {'Accept': 'application/json, text/plain, */*',
              'Accept-Encoding': 'gzip, deflate, br',
              'Accept-Language': 'zh-CN,zh;q=0.9',
              'Connection': 'keep-alive',
              'Host': 'google-api.zhaoyizhe.com',
              'Origin': 'https://weibo.zhaoyizhe.com',
              'Referer': 'https://weibo.zhaoyizhe.com/',
              'sec-ch-ua': '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
              'sec-ch-ua-mobile': '?0',
              'Sec-Fetch-Dest': 'empty',
              'Sec-Fetch-Mode': 'cors',
              'Sec-Fetch-Site': 'same-site',
              'user-agent': 'Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)'
              }
    html = requests.get(url=url, headers=header).content
    datas = json.loads(html.decode('utf-8'))['data']
    for i in range(len(datas)):
        url = 'https://s.weibo.com/weibo?q=' + parse.quote('#' + datas[i]['topic'] + '#')
        file_path = 'data/' + date + '/' + datas[i]['topic'] + '.txt'
        print(url)
        get_content(url, file_path)


if __name__ == '__main__':
    get_history_resou('2021-02-14')
