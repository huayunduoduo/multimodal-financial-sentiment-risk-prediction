import akshare as ak
import pandas as pd
import os
import re

# 获取 A 股所有上市公司的代码和名称
stock_info_a_code_name_df = ak.stock_info_a_code_name()

# 深度清理股票代码格式：去除所有非数字字符，并补足6位
stock_info_a_code_name_df['code'] = (
    stock_info_a_code_name_df['code']
    .astype(str)  # 强制转为字符串
    .str.replace(r'[^0-9]', '', regex=True)  # 清除所有非数字字符（包括大括号、引号等）
    .str.zfill(6)  # 补足前导零至6位
)

# 指定日期范围
start_date = "20250401"
end_date = "20250501"

# 创建新文件夹
output_folder = "/Users/30600/Desktop/CHIMI/数据收集与预处理/市场数据/A股历史数据"
os.makedirs(output_folder, exist_ok=True)

for index, row in stock_info_a_code_name_df.iterrows():
    # 二次清洗确保代码格式正确
    stock_code = re.sub(r'[^0-9]', '', str(row['code'])).zfill(6)
    stock_name = re.sub(r'[\\/*?:"<>|]', "", row['name'])
    
    # 判断交易所
    if stock_code.startswith(('6', '9')):
        exchange_suffix = 'SH'
    elif stock_code.startswith(('0', '3', '2')):
        exchange_suffix = 'SZ'
    else:
        print(f"未知交易所代码：{stock_code}，跳过")
        continue
    
    filename = f"{stock_name}_{stock_code}.{exchange_suffix}.csv"
    full_path = os.path.join(output_folder, filename)
    
    try:
        df = ak.stock_zh_a_hist(
            symbol=stock_code,
            period="daily",
            start_date=start_date,
            end_date=end_date
        )
        df.to_csv(full_path, index=False)
        print(f"成功保存 {index+1}/{len(stock_info_a_code_name_df)}：{filename}")
    except Exception as e:
        print(f"获取 {stock_name}({stock_code}) 失败，错误信息：{str(e)}")