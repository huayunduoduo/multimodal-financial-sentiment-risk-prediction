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

def process_view_count(view_count):
    """支持多种数字格式转换"""
    try:
        if pd.isnull(view_count) or str(view_count).strip() in ['', '-', 'N/A']:
            return None
        str_count = str(view_count).strip().replace(',', '')
        unit_multipliers = {
            '万': 10000,
            '千': 1000,
            'w': 10000,
            'k': 1000
        }
        for unit, mult in unit_multipliers.items():
            if unit in str_count.lower():
                num = re.search(r'[\d\.]+', str_count).group()
                return int(float(num) * mult)
        return int(float(str_count))  # 将结果转换为整数
    except Exception as e:
        print(f"数值转换失败：{view_count} | 错误：{str(e)}")
        return None

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

def convert_relative_time(time_str, base_time):
    """精确时间转换（返回纯日期）"""
    try:
        time_str = str(time_str).strip()
        absolute_patterns = [
            (r'(\d{4})年(\d{1,2})月(\d{1,2})日 (\d{1,2}):(\d{1,2})', '%Y年%m月%d日 %H:%M'),
            (r'(\d{4})-(\d{1,2})-(\d{1,2}) (\d{1,2}):(\d{1,2})', '%Y-%m-%d %H:%M'),
            (r'(\d{4})-(\d{1,2})-(\d{1,2}) (\d{1,2}):(\d{1,2}):(\d{1,2})', '%Y-%m-%d %H:%M:%S'),
            (r'(\d{4})-(\d{1,2})-(\d{1,2})', '%Y-%m-%d'),
            (r'(\d{2})-(\d{2}) (\d{1,2}):(\d{1,2})', '%m-%d %H:%M')
        ]
        for pattern, time_format in absolute_patterns:
            if re.match(pattern, time_str):
                if time_format == '%m-%d %H:%M':
                    time_str = f'2025-{time_str}'
                    time_format = '%Y-%m-%d %H:%M'
                dt = datetime.strptime(time_str, time_format)
                result = dt.strftime('%Y-%m-%d')
                print(f"转换时间: {time_str} -> {result}")  # 添加调试信息
                return result
        relative_patterns = [
            (r'(\d+)小时前', 'hours'),
            (r'(\d+)天前', 'days')
        ]
        for pattern, unit in relative_patterns:
            match = re.match(pattern, time_str)
            if match:
                value = int(match.group(1))
                if unit == 'hours':
                    result = base_time.strftime('%Y-%m-%d')
                    print(f"转换时间: {time_str} -> {result}")  # 添加调试信息
                    return result
                delta = timedelta(**{unit: value})
                result = (base_time - delta).strftime('%Y-%m-%d')
                print(f"转换时间: {time_str} -> {result}")  # 添加调试信息
                return result
        print(f"未知时间格式：{time_str}")
        return None
    except Exception as e:
        print(f"时间解析失败：{time_str} | 错误：{str(e)}")
        return None

# 主处理流程
if __name__ == "__main__":
    # 构建数据文件的绝对路径
    data_file_path = os.path.join(current_dir, '上证指数吧.csv')
    try:
        # 加载数据
        data = pd.read_csv(data_file_path)
    except FileNotFoundError:
        print(f"未找到文件: {data_file_path}")
        import sys
        sys.exit(1)

    # 自定义时间段
    start_date = '2025-01-01'
    end_date = '2025-03-09'
    base_time = datetime(2025, 3, 9)

    # 转换时间
    data['清洗后的时间'] = data['最后更新时间'].apply(lambda x: convert_relative_time(x, base_time))

    # 筛选指定时间段内的数据
    print(f"筛选前数据量: {len(data)}")  # 添加调试信息
    data = data[(data['清洗后的时间'] >= start_date) & (data['清洗后的时间'] <= end_date)]
    print(f"筛选后数据量: {len(data)}")  # 添加调试信息

    # 清洗阅读数
    data['清洗后的阅读数'] = data['阅读数'].apply(process_view_count)
    # 清洗标题
    data['清洗后的标题'] = data['标题'].apply(clean_text)

    # 构建保存结果文件的绝对路径
    output_file_path = os.path.join(current_dir, '上证指数吧清洗数据.csv')
    # 保存结果，保留指定的列
    data[['清洗后的阅读数', '评论数', '标题', '清洗后的标题', '作者', '清洗后的时间']].to_csv(output_file_path, index=False)
    print("清洗完成，数据已保存。")
    if len(data) > 0:
        print("示例结果：")
        print(data[['清洗后的阅读数', '评论数', '标题', '清洗后的标题', '作者', '清洗后的时间']].head(3).to_csv(sep='\t', na_rep='nan'))