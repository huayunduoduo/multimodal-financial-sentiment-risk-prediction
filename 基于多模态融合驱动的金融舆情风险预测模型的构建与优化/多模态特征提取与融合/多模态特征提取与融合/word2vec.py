import os
import re
import jieba
import logging
from gensim.models import Word2Vec
from gensim.models.word2vec import LineSentence
import pandas as pd
import numpy as np

# 配置日志记录
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

def preprocess_text(text):
    """
    对文本进行预处理，包括去除无关字符、数字、分词等操作。
    """
    # 去除无关字符和标点符号
    text = re.sub(r'[^\w\s]', '', text)
    # 去除数字
    text = re.sub(r'\d+', '', text)
    # 转换为小写
    text = text.lower()
    # 使用结巴分词进行中文分词
    words = jieba.lcut(text)
    return words

def train_word2vec_model(input_folder, output_model_path='word2vec_model.model', output_vector_path='word2vec_vectors.csv'):
    """
    训练 Word2Vec 模型并保存。
    """
    # 存储所有文件的分词后文本
    processed_texts = []
    file_names = []

    # 遍历文件夹中的所有文件
    for filename in os.listdir(input_folder):
        file_path = os.path.join(input_folder, filename)
        if os.path.isfile(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    text = file.read()
                    # 预处理文本
                    processed_text = preprocess_text(text)
                    processed_texts.append(processed_text)
                    file_names.append(filename)
            except Exception as e:
                logging.error(f"读取文件 {filename} 时出错: {e}")

    # 检查是否有足够的数据来训练模型
    if not processed_texts:
        logging.error("没有足够的训练数据，训练终止。")
        return None

    # 训练 Word2Vec 模型
    logging.info("开始训练 Word2Vec 模型")
    model = Word2Vec(
        sentences=processed_texts,
        vector_size=200,  # 词向量的维度
        window=10,       # 上下文窗口大小
        min_count=10,    # 忽略总频率低于此阈值的词
        workers=4,       # 训练时使用的线程数
        sg=1,            # 使用 Skip-Gram 模型（sg=0 为 CBOW）
        epochs=30        # 训练的轮数
    )

    # 保存模型
    model.save(output_model_path)
    logging.info(f"模型训练完成，已保存为 {output_model_path}")

    # 计算每个文档的向量
    doc_vectors = []
    for doc in processed_texts:
        doc_vector = np.zeros(model.vector_size)
        word_count = 0
        for word in doc:
            if word in model.wv:
                doc_vector += model.wv[word]
                word_count += 1
        if word_count > 0:
            doc_vector /= word_count
        doc_vectors.append(doc_vector)

    # 创建一个 DataFrame 来存储文档向量
    df_doc_vectors = pd.DataFrame(doc_vectors, index=file_names)
    df_doc_vectors.to_csv(output_vector_path)
    logging.info(f"文档向量已保存为 {output_vector_path}")

    return model

if __name__ == "__main__":
    input_folder = r"C:\Users\happyLi\Desktop\srtp文本"  # 输入文件夹路径
    output_model_path = r"C:\Users\happyLi\Desktop\srtp结果\word2vec_model.model"  # 输出模型路径
    output_vector_path = r"C:\Users\happyLi\Desktop\srtp结果\word2vec_features.csv"  # 输出文档向量路径

    # 训练模型并生成文档向量
    model = train_word2vec_model(input_folder, output_model_path, output_vector_path)