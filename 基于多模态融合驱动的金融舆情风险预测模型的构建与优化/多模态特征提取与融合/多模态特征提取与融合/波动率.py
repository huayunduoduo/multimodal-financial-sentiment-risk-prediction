import os
import pandas as pd
import numpy as np

# 定义文件夹路径
folder_path = r"C:\Users\happyLi\Desktop\srtP"

# 获取文件夹中所有CSV文件
csv_files = [file for file in os.listdir(folder_path) if file.endswith('.csv')]

# 创建一个空的DataFrame用于存储所有文件的价格波动率
all_volatility = pd.DataFrame(columns=['文件名', '价格波动率'])

# 遍历每个CSV文件
for file in csv_files:
    file_path = os.path.join(folder_path, file)
    # 读取CSV文件
    df = pd.read_csv(file_path)

    # 确保'收盘'列和'日期'列存在
    if '收盘' not in df.columns or '日期' not in df.columns:
        print(f"文件 {file} 中缺少'收盘'或'日期'列，跳过该文件。")
        continue

    # 计算对数收益率
    df['对数收益率'] = np.log(df['收盘'] / df['收盘'].shift(1))

    # 计算价格波动率（对数收益率的标准差）
    volatility = df['对数收益率'].std() * np.sqrt(252)  # 年化波动率（假设一年有252个交易日）

    # 检查波动率是否有效
    if pd.isna(volatility):
        print(f"文件 {file} 的价格波动率计算结果为 NaN，跳过该文件。")
        continue

    # 将结果添加到汇总表中
    new_row = pd.DataFrame({'文件名': [file], '价格波动率': [volatility]})
    all_volatility = pd.concat([all_volatility, new_row], ignore_index=True)

# 保存到新的CSV文件
output_file = os.path.join(folder_path, '价格波动率汇总.csv')
all_volatility.to_csv(output_file, index=False, encoding='utf-8-sig')

print(f"所有文件的价格波动率已保存到 {output_file}")