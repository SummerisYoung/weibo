from bomb import *
import time
import jieba.analyse
from utils import *
jieba.setLogLevel(jieba.logging.INFO)
bomb = Bmob("06ea4aea72a65ff8d70acb12b7493c37", "00bccc9915e86a66f95f7f30482ea41f")


# 对句子进行分词
def seg_sentence(sentence):
    sentence_seged = jieba.cut(sentence, cut_all=False, HMM=True)
    stopwords = [line.strip() for line in open('.\\stopwords.txt', 'r', encoding='utf-8').readlines()]
    outstr = []
    for word in sentence_seged:
        if word not in stopwords:
            if word != '\t':
                outstr.append(word)
    return outstr


# 转评赞正则转数字
def none_to_num(text):
    if text == '' or text == []:
        return 0
    else:
        return int(text) if isinstance(text, str) else int(text[0])


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
    # 有了就拿取里面的详情页链接
    if len(urls) > 0:
        exist_resou = urls[0]
        link = exist_resou['link']
    else:  # 没有就从热搜页拿取置顶微博
        resou_html = Pq(url=url)
        # 获取首条卡片
        content = resou_html('.content')[0]
        # 获取来源标签
        detail_url = Pq(content).children('.from').children('a').attr('href')
        # 拼接首条微博详情页链接
        link = detail_url
    # 拼接成可访问的url
    link = 'https:' + link + '&type=comment'
    # 详情页html
    detail_html = Pq(url=link, headers={'user-agent': 'Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)'})
    print(detail_html)
    # 获取文本父类
    content_html = detail_html('.WB_text')
    # 用作者和文本拼接内容
    content = Pq(content_html).attr('nick-name') + '：' + Pq(content_html).text()
    # 删除尾部空行、赘余文字
    content = content.replace('收起全文d', '').replace('O抽奖详情', '').replace('0网页链接', '').replace('\n', '').replace(' ', '')
    # 视频类内容删除尾部视频链接文字
    content = re.sub(r'L.*?的微博视频|L.*?的秒拍视频', '', content)
    category = weibo_category(content)
    # 获取转发数
    repost = int(Pq(detail_html('.ficon_forward').siblings()[0]).text())
    # 获取评论数
    comment = int(Pq(detail_html('.ficon_repeat').siblings()[0]).text())
    # 获取点赞数
    like = int(Pq(detail_html('.ficon_praised').siblings()[0]).text())
    # 将数据放在对象中返回
    resou_detail = {
        'content': content,
        'link': link,
        'repost': repost,
        'comment': comment,
        'like': like,
        'category': category
    }
    return resou_detail


# 获取热搜数据
def get_data():
    # 获取微博热搜榜源代码
    html = Pq(url='https://s.weibo.com/top/summary')

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
            "time": str(int(time.time()))  # 热搜时间戳
        }
        resou_detail = get_content('https://s.weibo.com' + href)
        # resou字典合并resou_detail字典
        resou.update(resou_detail)
        # 数据存入数据库
        print(bomb.insert('weibo', resou).jsonData)


# 将数据存入bomb后端云数据库
def set_bomb(results):
    for result in results:
        print(bomb.insert('weibo', result).jsonData)


if __name__ == '__main__':
    get_data()
