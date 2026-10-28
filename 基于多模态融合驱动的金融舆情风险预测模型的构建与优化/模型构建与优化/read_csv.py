import csv
import sys

file_path = r'd:\srtp03\dataset\combined_features_unified_vector.csv'

try:
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        # 读取前5行
        for i, row in enumerate(reader):
            if i < 5:
                print(f"Row {i+1}: {row[:10]}...")  # 只打印每行的前10个元素
                print(f"Total columns: {len(row)}")
            else:
                break
    print("Successfully read the CSV file.")
except Exception as e:
    print(f"Error reading CSV file: {e}")
    sys.exit(1)