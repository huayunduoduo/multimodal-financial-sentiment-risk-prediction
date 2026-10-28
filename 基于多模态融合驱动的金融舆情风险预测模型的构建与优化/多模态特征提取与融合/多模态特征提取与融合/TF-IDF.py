import os
import re
import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd

# 设置文件夹路径
input_folder = r"C:\Users\happyLi\Desktop\srtp文本"
output_folder = r"C:\Users\happyLi\Desktop\srtp结果"

# 确保输出文件夹存在
os.makedirs(output_folder, exist_ok=True)

# 读取文件夹中的所有文本文件
files = []
file_names = []
for filename in os.listdir(input_folder):
    if filename.endswith(".csv"):
        file_path = os.path.join(input_folder, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            # 去除网址
            content = re.sub(r'https?://\S+|www\.\S+', '', content)
            # 去除多余的空格和换行符
            content = re.sub(r'\s+', ' ', content)
            # 对中文文本进行分词处理
            words = jieba.lcut(content)
            # 将分词结果合并为字符串
            content = " ".join(words)
            files.append(content)
            file_names.append(filename)

# 使用TF-IDF模型计算关键词的重要性
vectorizer = TfidfVectorizer(max_features=2000, max_df=0.8, min_df=3)
tfidf_matrix = vectorizer.fit_transform(files)

# 获取词汇表和TF-IDF权重矩阵
feature_names = vectorizer.get_feature_names_out()
tfidf_weights = tfidf_matrix.toarray()

# 设置筛选阈值
threshold = 0.01

# 创建一个字典来存储所有文件的TF-IDF结果
tfidf_results_dict = {file_name: {} for file_name in file_names}

# 遍历每个文件的TF-IDF权重
for i in range(len(file_names)):
    # 遍历词汇和权重
    for word, weight in zip(feature_names, tfidf_weights[i]):
        # 如果权重大于阈值，保留该词汇和权重
        if weight > threshold:
            tfidf_results_dict[file_names[i]][word] = weight

# 将字典转换为DataFrame
tfidf_results = pd.DataFrame.from_dict(tfidf_results_dict, orient='index')

# 填充缺失值为0
tfidf_results.fillna(0, inplace=True)

# 保存结果到CSV文件
output_file = os.path.join(output_folder, "tfidf_features.csv")
tfidf_results.to_csv(output_file, index=True, encoding="utf-8-sig")

print("TF-IDF结果已保存到指定文件夹。")