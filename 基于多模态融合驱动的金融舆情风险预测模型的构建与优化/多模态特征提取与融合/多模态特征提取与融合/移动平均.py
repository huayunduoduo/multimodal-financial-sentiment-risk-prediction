import pandas as pd
import os

# 文件夹路径
folder_path = r'C:\Users\happyLi\Desktop\srtP'

# 用于存储每个公司的移动平均数据
sma_data = {}

# 遍历文件夹中的所有文件
for filename in os.listdir(folder_path):
    # 检查文件是否为 CSV 文件
    if filename.endswith('.csv'):
        file_path = os.path.join(folder_path, filename)
        try:
            # 提取公司名，假设文件名中包含公司名
            company_name = os.path.splitext(filename)[0]

            # 读取 CSV 文件
            df = pd.read_csv(file_path)

            # 计算 5 日简单移动平均线
            sma = df['收盘'].rolling(window=5).mean()

            # 存储该公司的移动平均数据
            sma_data[company_name] = sma

        except Exception as e:
            print(f"处理文件 {filename} 时出现错误: {e}")

# 将字典转换为 DataFrame
result_df = pd.DataFrame(sma_data)

# 保存最终结果到新的 CSV 文件
output_file = os.path.join(folder_path, 'combined_sma_data.csv')
result_df.to_csv(output_file)

print(f"所有文件处理完成，结果已保存到 {output_file}")