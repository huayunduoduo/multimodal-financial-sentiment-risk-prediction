import pandas as pd
import nltk
from nltk.corpus import stopwords
import jieba
import re

nltk.download('stopwords')

# 获取中文的停用词列表
stop_words = set(stopwords.words('chinese'))

file_path = '上证指数吧.csv'
data = pd.read_csv(file_path)

# 中文分词并去停用词、去特殊字符的函数
def clean_text(text):
    # 使用jieba进行中文分词
    words = jieba.cut(text)
    # 去除停用词和特殊字符
    cleaned_words = [word for word in words if word not in stop_words and word.strip() != '' and re.match(r'[\u4e00-\u9fa5a-zA-Z0-9]+', word)]
    return ' '.join(cleaned_words)

# 应用分词清洗“标题”列
data['清洗后的标题'] = data['标题'].apply(clean_text)

# 处理“阅读数”列，将其转换为数值型
def process_view_count(view_count):
    if isinstance(view_count, str):
        if '万' in view_count:
            return float(view_count.replace('万', '')) * 10000
        elif ',' in view_count:
            return int(view_count.replace(',', ''))
        try:
            return float(view_count)
        except ValueError:
            return None
    return view_count

data['阅读数'] = data['阅读数'].apply(process_view_count)

data['评论数'] = pd.to_numeric(data['评论数'], errors='coerce')

data_cleaned = data.dropna()

data_cleaned = data_cleaned[(data_cleaned['阅读数'] >= 0) & (data_cleaned['评论数'] >= 0)]

# 打印清洗后的数据
print(data_cleaned[['阅读数', '评论数', '清洗后的标题', '最后更新时间']].head())

output_file_path = '清洗后的数据(2).csv'
data_cleaned.to_csv(output_file_path, index=False, encoding='utf-8-sig')