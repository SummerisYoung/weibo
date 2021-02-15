from pyquery import PyQuery as Pq
from sklearn.datasets._base import Bunch
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB  # 导入多项式贝叶斯算法
import re
import jieba
import os
import pickle
jieba.setLogLevel(jieba.logging.INFO)


# 获取热榜详情页的内容
def get_content(url, file_path=''):
    content_html = Pq(url=url)
    # 获取首条卡片
    content = content_html('.content')[0]
    # 获取卡片内容
    text_html = Pq(content).children('.txt')
    # 如果有两个卡片内容，那么说明有展开全文，需要获取后一个，全部文字版的
    text = Pq(text_html[0]).text() if text_html.length == 1 else Pq(text_html[1]).text()
    # 删除一些尾部文字、换行、空格
    text = text.replace('收起全文d', '').replace('O抽奖详情', '').replace('0网页链接', '').replace('\n', '').replace(' ', '')
    # 视频类内容删除尾部视频链接文字
    text = re.sub(r'L.*?的微博视频|L.*?的秒拍视频', '', text)
    txt = ' '.join(jieba.cut(text, cut_all=False, HMM=True))
    print(text)
    print(txt)
    print('\n')
    # 第二个参数传了就保存文本到文件
    if file_path != '':
        with open(file_path, "wb") as fp:
            fp.write(txt.encode())


# 读取文件
def readfile(path):
    with open(path, "rb") as fp:
        content = fp.read()
    return content


# 读取bunch文件
def readbunchobj(path):
    with open(path, "rb") as file_obj:
        bunch = pickle.load(file_obj)
    return bunch


# 写入bunch文件
def writebunchobj(path, bunchobj):
    with open(path, "wb") as file_obj:
        pickle.dump(bunchobj, file_obj)


# 构建一个TF-IDF词向量空间
def vector_space(stopword_path, bunch_path, space_path, train_tfidf_path=None):
    stpwrdlst = readfile(stopword_path).splitlines()
    bunch = readbunchobj(bunch_path)
    tfidfspace = Bunch(target_name=bunch.target_name, label=bunch.label, filenames=bunch.filenames, tdm=[],
                       vocabulary={})

    if train_tfidf_path is not None:
        trainbunch = readbunchobj(train_tfidf_path)
        tfidfspace.vocabulary = trainbunch.vocabulary
        vectorizer = TfidfVectorizer(stop_words=stpwrdlst, sublinear_tf=True, max_df=0.5,
                                     vocabulary=trainbunch.vocabulary)
        tfidfspace.tdm = vectorizer.fit_transform(bunch.contents)

    else:
        vectorizer = TfidfVectorizer(stop_words=stpwrdlst, sublinear_tf=True, max_df=0.5)
        tfidfspace.tdm = vectorizer.fit_transform(bunch.contents)
        tfidfspace.vocabulary = vectorizer.vocabulary_

    writebunchobj(space_path, tfidfspace)
    print("if-idf词向量空间实例创建成功！！！")


# 数据转为bunch类型
def corpus2Bunch(wordbag_path, seg_path):
    catelist = os.listdir(seg_path)  # 获取seg_path下的所有子目录，也就是分类信息
    # 创建一个Bunch实例
    bunch = Bunch(target_name=[], label=[], filenames=[], contents=[])
    bunch.target_name.extend(catelist)
    # 获取每个目录下所有的文件
    for mydir in catelist:
        class_path = seg_path + mydir + "/"  # 拼出分类子目录的路径

        file_list = os.listdir(class_path)  # 获取class_path下的所有文件
        for file_path in file_list:  # 遍历类别目录下文件
            fullname = class_path + file_path  # 拼出文件名全路径
            bunch.label.append(mydir)
            bunch.filenames.append(fullname)
            bunch.contents.append(readfile(fullname))  # 读取文件内容
            '''append(element)是python list中的函数，意思是向原来的list中添加element，注意与extend()函数的区别'''
            # 将bunch存储到wordbag_path路径中
            with open(wordbag_path, "wb") as file_obj:
                pickle.dump(bunch, file_obj)


# 对单条文本进行分类预测
def weibo_category(contents):
    # 生成一个bunch类型
    bunch = Bunch(target_name=[], label=[], filenames=[], contents=[])
    # 添加文本
    bunch.contents.append(contents)
    # 获取停用词过滤掉文本中的垃圾词汇
    stpwrdlst = readfile("stopwords.txt").splitlines()
    # 获取训练集模型
    train_set = readbunchobj("train_word_bag/tfdifspace.dat")
    # 使用TfidfVectorizer初始化向量空间模型
    vectorizer = TfidfVectorizer(stop_words=stpwrdlst, sublinear_tf=True, max_df=0.5, vocabulary=train_set.vocabulary)
    # tdm里面存储的就是if-idf权值矩阵
    tdm = vectorizer.fit_transform(bunch.contents)
    # 训练分类器：输入词袋向量和分类标签，alpha:0.001 alpha越小，迭代次数越多，精度越高
    clf = MultinomialNB(alpha=0.001).fit(train_set.tdm, train_set.label)
    # 预测分类结果
    predicted = clf.predict(tdm)
    return predicted[0]
