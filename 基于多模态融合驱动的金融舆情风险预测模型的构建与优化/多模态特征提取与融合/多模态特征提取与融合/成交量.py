import os
import pandas as pd

# 定义文件夹路径
folder_path = r"C:\Users\happyLi\Desktop\srtP"

# 获取文件夹中所有CSV文件
csv_files = [file for file in os.listdir(folder_path) if file.endswith('.csv')]

# 创建一个空的DataFrame用于存储所有文件的成交量变化数据
all_volume_changes = pd.DataFrame()

# 创建一个空的日期列表用于存储所有日期
all_dates = []

# 遍历每个CSV文件
for file in csv_files:
    file_path = os.path.join(folder_path, file)
    # 读取CSV文件
    df = pd.read_csv(file_path)

    # 确保'成交量'列和'日期'列存在
    if '成交量' not in df.columns or '日期' not in df.columns:
        print(f"文件 {file} 中缺少'成交量'或'日期'列，跳过该文件。")
        continue

    # 提取所有日期并添加到日期列表中
    all_dates.extend(df['日期'].tolist())

    # 计算成交量变化（当前成交量 - 前一天成交量）
    df['成交量变化'] = df['成交量'].diff()

    # 选择日期和成交量变化列，并重命名成交量变化列为文件名
    df = df[['日期', '成交量变化']].rename(columns={'成交量变化': file})

    # 如果all_volume_changes为空，则直接赋值
    if all_volume_changes.empty:
        all_volume_changes = df
    else:
        # 否则，按日期合并
        all_volume_changes = pd.merge(all_volume_changes, df, on='日期', how='outer')

# 删除第一行（因为diff()会导致第一行为NaN）
all_volume_changes = all_volume_changes.dropna(subset=['日期']).reset_index(drop=True)

# 确保所有日期都在最终结果中
all_dates = sorted(set(all_dates))  # 去重并排序
all_dates_df = pd.DataFrame(all_dates, columns=['日期'])

# 将所有日期与成交量变化数据合并
final_result = pd.merge(all_dates_df, all_volume_changes, on='日期', how='left')

# 保存到新的CSV文件
output_file = os.path.join(folder_path, '成交量变化汇总.csv')
final_result.to_csv(output_file, index=False, encoding='utf-8-sig')

print(f"所有文件的成交量变化已保存到 {output_file}")