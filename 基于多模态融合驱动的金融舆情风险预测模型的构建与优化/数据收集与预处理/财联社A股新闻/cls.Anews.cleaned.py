import pandas as pd
import re
import jieba
from datetime import datetime, timedelta

# 第二步：加载数据与初始化
# ----------------------
# 加载停用词
import os
# 获取当前脚本所在的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 构建停用词文件的绝对路径
stopwords_file_path = os.path.join(current_dir, 'cn_stopwords.txt')
try:
    with open(stopwords_file_path, encoding='utf-8') as f:
        STOPWORDS = set(f.read().splitlines())
except FileNotFoundError:
    print(f"未找到文件: {stopwords_file_path}")
    # 可以根据需要添加其他处理逻辑，例如退出程序
    import sys
    sys.exit(1)

# 构建A股企业名单文件的绝对路径
a_share_companies_file_path = os.path.join(current_dir, 'A股所有上市公司名称.txt')
try:
    with open(a_share_companies_file_path, 'r', encoding='utf-8') as f:
        A_SHARE_COMPANIES = [line.strip() for line in f if line.strip()]
except FileNotFoundError:
    print(f"未找到文件: {a_share_companies_file_path}")
    import sys
    sys.exit(1)

# 添加到分词词典
for company in A_SHARE_COMPANIES:
    jieba.add_word(company, freq=100000, tag='n')

# ----------------------
# 增强版数据处理函数
# ----------------------
def convert_relative_time(time_str, base_time):
    """精确时间转换（返回纯日期）"""
    try:
        time_str = str(time_str).strip()
        
        # 处理绝对时间
        absolute_patterns = [
            (r'(\d{4})年(\d{1,2})月(\d{1,2})日 (\d{1,2}):(\d{1,2})', '%Y年%m月%d日 %H:%M'),
            (r'(\d{4})-(\d{1,2})-(\d{1,2}) (\d{1,2}):(\d{1,2}):(\d{1,2})', '%Y-%m-%d %H:%M:%S'),
            (r'(\d{4})-(\d{1,2})-(\d{1,2})', '%Y-%m-%d')
        ]
        
        for pattern, time_format in absolute_patterns:
            if re.match(pattern, time_str):
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
def process_view_count(view_count):
    """支持多种数字格式转换"""
    try:
        if pd.isnull(view_count) or str(view_count).strip() in ['', '-', 'N/A']:
            return None
            
        str_count = str(view_count).strip().replace(',', '')
        
        # 处理中文单位
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
                
        return float(str_count)
    except Exception as e:
        print(f"数值转换失败：{view_count} | 错误：{str(e)}")
        return None

def clean_text(text):
    """智能文本清洗（保留企业名称不分词）"""
    if pd.isnull(text):
        return ""
    
    original_text = text.strip()
    cleaned_text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]+', ' ', original_text)
    words = jieba.lcut(cleaned_text)
    
    # 双重检测机制
    has_company = any(company in original_text for company in A_SHARE_COMPANIES)
    has_company_in_words = any(word in A_SHARE_COMPANIES for word in words)
    
    # 过滤处理
    final_words = []
    for word in words:
        if word in A_SHARE_COMPANIES:
            final_words.append(word)
        else:
            if word not in STOPWORDS and len(word) > 1:
                final_words.append(word)
    
    result = ' '.join(final_words)
    

    
    return result

# ----------------------
# 主处理流程
# ----------------------
if __name__ == "__main__":
    # 获取当前脚本所在的目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 构建数据文件的绝对路径
    data_file_path = os.path.join(current_dir, '财联社A股新闻数据.csv')
    try:
        # 加载数据
        data = pd.read_csv(data_file_path)
    except FileNotFoundError:
        print(f"未找到文件: {data_file_path}")
        import sys
        sys.exit(1)

    # 预处理流程
    data['阅读数'] = data['阅读数'].apply(process_view_count)
    base_time = datetime(2025, 3, 9)  # 根据实际数据调整
    data['具体更新时间'] = data['最后更新时间'].apply(
        lambda x: convert_relative_time(x, base_time))
    data['清洗标题'] = data['标题'].apply(clean_text)

    # 筛选特定时间段的数据
    start_date = '2025-01-01'
    end_date = '2025-03-09'
    filtered_data = data[(data['具体更新时间'] >= start_date) & (data['具体更新时间'] <= end_date)]

    # 构建保存结果文件的绝对路径
    output_file_path = os.path.join(current_dir, '财联社A股新闻清洗数据.csv')
    # 保存结果
    filtered_data.to_csv(output_file_path, index=False)
    print(f"清洗完成，特定时间段（{start_date} - {end_date}）有效数据量：{len(filtered_data)}")
    if len(filtered_data) > 0:
        print("示例结果：")
        print(filtered_data[['标题', '清洗标题']].head(3).to_string(index=False))