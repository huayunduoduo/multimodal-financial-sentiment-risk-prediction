import pandas as pd
import re
import jieba
from datetime import datetime, timedelta
import os

# 获取当前脚本所在的目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 加载 A 股企业名单
a_share_companies_file_path = os.path.join(current_dir, 'A股所有上市公司名称.txt')
try:
    with open(a_share_companies_file_path, 'r', encoding='utf-8') as f:
        A_SHARE_COMPANIES = [line.strip() for line in f.readlines()]
except FileNotFoundError:
    print(f"未找到文件: {a_share_companies_file_path}")
    import sys
    sys.exit(1)

# 加载停用词
stopwords_file_path = os.path.join(current_dir, 'cn_stopwords.txt')
try:
    with open(stopwords_file_path, encoding='utf-8') as f:
        STOPWORDS = set(f.read().splitlines())
except FileNotFoundError:
    print(f"未找到文件: {stopwords_file_path}")
    import sys
    sys.exit(1)

# 添加 A 股企业名称到分词词典
for company in A_SHARE_COMPANIES:
    jieba.add_word(company, freq=100000, tag='n')

def clean_text(text):
    """智能文本清洗（保留企业名称不分词）"""
    if pd.isnull(text):
        return ""
    original_text = text.strip()
    cleaned_text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9%.]+', ' ', original_text)
    words = jieba.lcut(cleaned_text)
    final_words = []
    for word in words:
        if word in A_SHARE_COMPANIES:
            final_words.append(word)
        elif word not in STOPWORDS and len(word) > 1:
            final_words.append(word)
    result = ' '.join(final_words)
    return result

def convert_relative_time(time_str):
    """精确时间转换（返回纯日期）"""
    try:
        dt = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
        return dt.strftime('%Y-%m-%d')
    except Exception as e:
        print(f"时间解析失败：{time_str} | 错误：{str(e)}")
        return None

# 主处理流程
if __name__ == "__main__":
    # 构建数据文件的绝对路径
    data_file_path = os.path.join(current_dir, 'cnstock_data.csv')
    try:
        # 加载数据，跳过表头
        data = pd.read_csv(data_file_path, names=['link', 'title', 'node_name', 'tag_name', 'pub_date'], header=0)
    except FileNotFoundError:
        print(f"未找到文件: {data_file_path}")
        import sys
        sys.exit(1)

    # 自定义时间段
    start_date = '2025-01-01'
    end_date = '2025-03-09'
    base_time = datetime(2025, 3, 9)

    # 清洗标题
    data['cleaned-title'] = data['title'].apply(clean_text)

    # 转换时间
    data['cleaned-pub_date'] = data['pub_date'].apply(convert_relative_time)

    # 构建保存结果文件的绝对路径
    output_file_path = os.path.join(current_dir, 'cnstock清洗数据.csv')
    # 保存结果，保留指定的列
    data[['link', 'title', 'cleaned-title', 'node_name', 'tag_name', 'cleaned-pub_date']].to_csv(output_file_path, index=False)
    print("清洗完成，数据已保存。")
    if len(data) > 0:
        print("示例结果：")
        print(data[['link', 'title', 'cleaned-title', 'node_name', 'tag_name', 'cleaned-pub_date']].head(3).to_csv(sep='\t', na_rep='nan'))