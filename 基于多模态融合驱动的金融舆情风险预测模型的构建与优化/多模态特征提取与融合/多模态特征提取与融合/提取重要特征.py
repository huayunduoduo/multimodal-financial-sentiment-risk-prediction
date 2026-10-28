import os
import pandas as pd
from collections import Counter

# 定义文件夹路径和保存结果的路径
folder_path = r'C:\Users\happyLi\Desktop\srtp文本'
save_path = r'C:\Users\happyLi\Desktop\srtp结果\金融风险关键词结果.csv'

# 金融风险相关关键词列表
risk_keywords = [
    "市场风险", "信用风险", "流动性风险", "操作风险",
    "系统性风险", "违约风险", "利率风险", "波动性",
    "杠杆", "不良贷款", "金融危机", "风险敞口",
    "对手方风险", "汇率风险", "风险管理", "坏账",
    "证监会", "IPO", "外资", "投行", "量化", "券商", "A股", "上市公司"
]

# 用于存储所有文件的结果
all_results = []

# 遍历文件夹中的所有文件
for filename in os.listdir(folder_path):
    if filename.endswith('.csv'):
        file_path = os.path.join(folder_path, filename)
        try:
            # 读取 CSV 文件所有内容
            df = pd.read_csv(file_path)
            all_text = []
            for col in df.columns:
                all_text.extend(df[col].dropna().astype(str).tolist())

            all_text_str = ' '.join(all_text)

            # 简单分词（按空格分割）
            words = all_text_str.split()

            # 统计词频
            word_freq = Counter(words)

            # 输出当前文件的前20个高频词
            print(f"文件 {filename} 的前20个高频词:")
            print(word_freq.most_common(20))


            # 定义函数从文本中提取金融风险关键词
            def extract_risk_text(text):
                for keyword in risk_keywords:
                    if keyword in text:
                        return keyword
                return None


            keyword_results = []
            for text in all_text:
                keyword = extract_risk_text(text)
                if keyword:
                    keyword_results.append({
                        '文件名': filename,
                        '文本内容': text,
                        '金融风险关键词': keyword
                    })
            if keyword_results:
                result_df = pd.DataFrame(keyword_results)
                all_results.append(result_df)

        except FileNotFoundError:
            print(f"错误：未找到文件 {file_path}，请检查文件路径。")
        except Exception as e:
            print(f"错误：处理文件 {file_path} 时发生未知错误：{e}")

# 合并所有文件的结果
if all_results:
    final_result = pd.concat(all_results, ignore_index=True)
    try:
        # 保存最终结果到指定路径
        final_result.to_csv(save_path, index=False)
        print(f"结果已成功保存到 {save_path}")
    except PermissionError:
        print("错误：没有权限保存文件，请检查保存路径的权限设置。")
    except Exception as e:
        print(f"错误：保存文件时发生未知错误：{e}")
else:
    print("未找到包含金融风险关键词的有效数据。")
