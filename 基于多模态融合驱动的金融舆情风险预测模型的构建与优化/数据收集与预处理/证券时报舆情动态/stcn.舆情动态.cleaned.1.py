import pandas as pd
import re
import jieba
from datetime import datetime, timedelta
import os
import sys

# 第二步：加载数据与初始化
# ----------------------
# 加载停用词
import os
# 获取当前脚本所在的目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 构建A股企业名单文件的绝对路径
a_share_companies_file_path = os.path.join(current_dir, 'A股所有上市公司名称.txt')
try:
    with open(a_share_companies_file_path, 'r', encoding='utf-8') as f:
        A_SHARE_COMPANIES = [line.strip() for line in f.readlines()]
except FileNotFoundError:
    print(f"未找到文件: {a_share_companies_file_path}")
    import sys
    sys.exit(1)

# 构建停用词文件的绝对路径
stopwords_file_path = os.path.join(current_dir, 'cn_stopwords.txt')
try:
    with open(stopwords_file_path, encoding='utf-8') as f:
        STOPWORDS = set(f.read().splitlines())
except FileNotFoundError:
    print(f"未找到文件: {stopwords_file_path}")
    import sys
    sys.exit(1)

# 添加到分词词典
for company in A_SHARE_COMPANIES:
    jieba.add_word(company, freq=100000, tag='n')

def clean_text(text):
    """智能文本清洗（保留企业名称不分词）"""
    if pd.isnull(text):
        return ""
    
    original_text = text.strip()
    # 修改正则表达式，添加小数点
    cleaned_text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9%.]+', ' ', original_text)
    words = jieba.lcut(cleaned_text)
    
    # 过滤处理
    final_words = []
    for word in words:
        if word in A_SHARE_COMPANIES:
            final_words.append(word)
        else:
            if len(word) > 1:
                final_words.append(word)
    
    result = ' '.join(final_words)
    return result

def convert_relative_time(time_str, base_time):
    """精确时间转换（返回纯日期）"""
    try:
        time_str = str(time_str).strip()
        
        # 处理绝对时间
        absolute_patterns = [
            (r'(\d{4})年(\d{1,2})月(\d{1,2})日 (\d{1,2}):(\d{1,2})', '%Y年%m月%d日 %H:%M'),
            (r'(\d{4})-(\d{1,2})-(\d{1,2}) (\d{1,2}):(\d{1,2})', '%Y-%m-%d %H:%M'),
            (r'(\d{4})-(\d{1,2})-(\d{1,2}) (\d{1,2}):(\d{1,2}):(\d{1,2})', '%Y-%m-%d %H:%M:%S'),
            (r'(\d{4})-(\d{1,2})-(\d{1,2})', '%Y-%m-%d'),
            # 添加对 03-06 20:02 格式的支持
            (r'(\d{2})-(\d{2}) (\d{1,2}):(\d{1,2})', '%m-%d %H:%M')
        ]
        
        for pattern, time_format in absolute_patterns:
            if re.match(pattern, time_str):
                # 对于 03-06 20:02 格式，手动添加年份
                if time_format == '%m-%d %H:%M':
                    time_str = f'2025-{time_str}'
                    time_format = '%Y-%m-%d %H:%M'
                dt = datetime.strptime(time_str, time_format)
                return dt.strftime('%Y-%m-%d')  # 只返回日期部分
                
        # 处理相对时间
        relative_patterns = [
            (r'(\d+)小时前', 'hours'),
            (r'(\d+)天前', 'days')
        ]
        
        for pattern, unit in relative_patterns:
            match = re.match(pattern, time_str)
            if match:
                value = int(match.group(1))
                if unit == 'hours':
                    # 如果是几小时前，直接返回base_time的日期部分
                    return base_time.strftime('%Y-%m-%d')
                delta = timedelta(**{unit: value})
                return (base_time - delta).strftime('%Y-%m-%d')  # 只返回日期部分
                
        print(f"未知时间格式：{time_str}")
        return None
    except Exception as e:
        print(f"时间解析失败：{time_str} | 错误：{str(e)}")
        return None

# 主处理流程
if __name__ == "__main__":
    # 自定义日期范围
    start_date = '2025-01-01'
    end_date = '2025-03-09'
    
    # 构建数据文件的绝对路径
    data_file_path = os.path.join(current_dir, 'stcn舆情动态.csv')
    try:
        # 加载数据
        data = pd.read_csv(data_file_path)
    except FileNotFoundError:
        print(f"未找到文件: {data_file_path}")
        import sys
        sys.exit(1)

    # 清洗标题
    data['清洗后的标题'] = data['标题'].apply(clean_text)
    # 清洗正文
    data['清洗后的正文'] = data['正文'].apply(clean_text)

    # 假设当前日期为2025-03-08
    base_time = datetime(2025, 3, 9)
    # 清洗时间
    data['清洗后的时间'] = data['时间'].apply(lambda x: convert_relative_time(x, base_time))

    # 筛选指定时间段内的数据
    data = data[(data['清洗后的时间'] >= start_date) & (data['清洗后的时间'] <= end_date)]

    # 构建保存结果文件的绝对路径
    output_file_path = os.path.join(current_dir, 'stcn舆情动态清洗数据.csv')
    # 保存结果，保留指定的列
    data[['标题', '清洗后的标题', '链接', '正文', '清洗后的正文', '标签', '清洗后的时间']].to_csv(output_file_path, index=False)
    print("清洗完成，数据已保存。")
    if len(data) > 0:
        print("示例结果：")
        # 修改打印示例结果的列
        print(data[['标题', '清洗后的标题', '链接', '正文', '清洗后的正文', '标签', '清洗后的时间']].head(3).to_csv(sep='\t', na_rep='nan'))