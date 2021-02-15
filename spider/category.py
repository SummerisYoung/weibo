from utils import *
from sklearn.naive_bayes import MultinomialNB  # 导入多项式贝叶斯算法
from sklearn import metrics


# Bunch化操作
def train():
    # 对训练集进行Bunch化操作：
    wordbag_path = "train_word_bag/train_set.dat"  # Bunch存储路径
    seg_path = "train_corpus/"  # 分词后分类语料库路径
    corpus2Bunch(wordbag_path, seg_path)

    # 对测试集进行Bunch化操作：
    wordbag_path = "test_word_bag/test_set.dat"  # Bunch存储路径
    seg_path = "test_corpus/"  # 分词后分类语料库路径
    corpus2Bunch(wordbag_path, seg_path)


# tf-idf向量
def tf_idf():
    stopword_path = "stopwords.txt"
    bunch_path = "train_word_bag/train_set.dat"
    space_path = "train_word_bag/tfdifspace.dat"
    vector_space(stopword_path, bunch_path, space_path)

    bunch_path = "test_word_bag/test_set.dat"
    space_path = "test_word_bag/testspace.dat"
    train_tfidf_path = "train_word_bag/tfdifspace.dat"
    vector_space(stopword_path, bunch_path, space_path, train_tfidf_path)


# 预测分类结果
def predict():
    # 导入训练集
    trainpath = "train_word_bag/tfdifspace.dat"
    train_set = readbunchobj(trainpath)

    # 导入测试集
    testpath = "test_word_bag/testspace.dat"
    test_set = readbunchobj(testpath)

    # 训练分类器：输入词袋向量和分类标签，alpha:0.001 alpha越小，迭代次数越多，精度越高
    clf = MultinomialNB(alpha=0.001).fit(train_set.tdm, train_set.label)

    # 预测分类结果
    predicted = clf.predict(test_set.tdm)

    for file_name, expct_cate in zip(test_set.filenames, predicted):
        # if flabel != expct_cate:
        print(file_name, " -->预测类别:", expct_cate)
    print("预测完毕!!!")
    print("精度:{0:.3f}".format(metrics.precision_score(test_set.label, predicted, average='weighted')))


if __name__ == '__main__':
    train()
    tf_idf()
    predict()
