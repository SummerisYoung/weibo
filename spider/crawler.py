from bomb import *
import time
from utils import *
jieba.setLogLevel(jieba.logging.INFO)
bomb = Bmob("06ea4aea72a65ff8d70acb12b7493c37", "00bccc9915e86a66f95f7f30482ea41f")


# 查询url是否存在表中
def is_exist_url(url):
    find_url = bomb.find("weibo", BmobQuerier().addWhereEqualTo('url', url)).jsonData
    return find_url['results']


# 获取热榜详情页的内容
def get_content(url):
    # 初始化详情页链接
    link = ''
    # 查询下数据库中是否已经有这个热搜的数据了
    urls = is_exist_url(url)
    # # 有了就拿取里面的详情页链接
    if len(urls) > 0:
        exist_resou = urls[0]
        link = exist_resou['link']
    else:  # 没有就从热搜页拿取置顶微博
        resou_html = Pq(url=url)
        # 获取首条卡片
        content = resou_html('.content')
        if len(content) == 0:
            return None
        content = content[0]
        # 获取来源标签
        detail_url = Pq(content).children('.from').children('a').attr('href')
        # 拼接首条微博详情页链接
        link = 'https:' + detail_url
        print(link)
    # noinspection PyBroadException
    try:
        # 详情页html
        detail_html = Pq(url=link, headers={'user-agent': 'Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)'})
        # 获取作者
        author = Pq(Pq(detail_html('.WB_info')).children('a')[0]).text()
        # 获取文本父类
        content = Pq(detail_html('.WB_text')).text()
        # 删除尾部空行、赘余文字
        content = content.replace('收起全文d', '').replace('O抽奖详情', '').replace('0网页链接', '').replace('\n', '').replace(' ', '')
        # 视频类内容删除尾部视频链接文字
        content = re.sub(r'L.*?的微博视频|L.*?的秒拍视频', '', content)
        # 预测分类
        category = weibo_category(content)
        # 获取转发数
        repost = Pq(detail_html('.ficon_forward').siblings()[0]).text()
        repost = int(repost) if repost != '转发' else 0
        # 获取评论数
        comment = Pq(detail_html('.ficon_repeat').siblings()[0]).text()
        comment = int(comment) if comment != '评论' else 0
        # 获取点赞数
        like = Pq(detail_html('.ficon_praised').siblings()[0]).text()
        like = int(like) if like != '赞' else 0
        # 将数据放在对象中返回
        resou_detail = {
            'content': content,
            'author': author,
            'link': link,
            'repost': repost,
            'comment': comment,
            'like': like,
            'category': category
        }
        return resou_detail

    except:
        return None


# 获取热搜数据
def get_data():
    # 获取微博热搜榜源代码
    html = Pq(url='https://s.weibo.com/top/summary')
    timestamp = str(int(time.time()))  # 热搜时间戳

    # 获取热搜排名
    rank = html('.td-01.ranktop')
    # 获取热搜标题（带热度）
    title = html('.td-02')[1:]

    for i in range(len(rank)):
        href = Pq(title[i]).children('a').attr('href') if not Pq(title[i]).children('a').attr('href_to') else Pq(
            title[i]).children('a').attr('href_to')
        resou = {
            "rank": int(Pq(rank[i]).text()),  # 热搜排名
            "title": Pq(title[i]).children('a').text(),  # 热搜标题
            "url": 'https://s.weibo.com' + href,
            "weight": int(Pq(title[i]).children('span').text()),  # 热搜热度
            "time": timestamp
        }
        resou_detail = get_content('https://s.weibo.com' + href)
        if resou_detail is not None:
            # resou字典合并resou_detail字典
            resou.update(resou_detail)
            # 数据存入数据库
            print(bomb.insert('weibo', resou).jsonData)


if __name__ == '__main__':
    get_data()
