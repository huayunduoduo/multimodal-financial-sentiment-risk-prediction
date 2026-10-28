import torch
import numpy as np
import pandas as pd
from torch.utils.data import Dataset, DataLoader
import os

class FinancialDataset(Dataset):
    def __init__(self, file_path, seq_length=3):
        # 读取CSV文件
        self.df = pd.read_csv(file_path)
        self.seq_length = seq_length
        
        # 提取日期列
        self.dates = self.df['date'].values
        
        # 提取特征列（除去日期列）
        self.features = self.df.iloc[:, 1:].values.astype(np.float32)
        
        # 确保有足够的数据来创建时间序列
        self.num_samples = len(self.features) - self.seq_length
        
        # 为每个样本创建一个标签
        # 使用下一天的第一个特征作为标签的近似
        self.labels = []
        for i in range(self.seq_length, len(self.features)):
            # 计算一个[-1, 1]范围内的标签
            # 这里只是一个简单示例，实际应用中应该使用真实的标签数据
            label = 2 * (np.sum(self.features[i]) / len(self.features[i])) - 1
            self.labels.append(label)
        self.labels = np.clip(np.array(self.labels), -1, 1).astype(np.float32)
    
    def __len__(self):
        return self.num_samples
    
    def __getitem__(self, idx):
        # 获取时间序列特征（LSTM输入）
        seq_features = self.features[idx:idx + self.seq_length]
        
        # 获取当前特征（Transformer输入）
        current_features = self.features[idx + self.seq_length - 1]
        
        # 获取标签
        label = self.labels[idx]
        
        # 转换为张量
        seq_tensor = torch.tensor(seq_features)
        current_tensor = torch.tensor(current_features)
        label_tensor = torch.tensor(label)
        
        return seq_tensor, current_tensor, label_tensor

def create_data_loaders(file_path, seq_length=3, batch_size=32, train_ratio=0.8):
    # 创建数据集
    dataset = FinancialDataset(file_path, seq_length)
    
    # 划分训练集和测试集
    train_size = int(len(dataset) * train_ratio)
    test_size = len(dataset) - train_size
    train_dataset, test_dataset = torch.utils.data.random_split(
        dataset, [train_size, test_size]
    )
    
    # 创建数据加载器
    train_loader = DataLoader(
        train_dataset, batch_size=batch_size, shuffle=True
    )
    test_loader = DataLoader(
        test_dataset, batch_size=batch_size, shuffle=False
    )
    
    return train_loader, test_loader

if __name__ == "__main__":
    # 测试数据加载器
    file_path = r'd:\srtp03\dataset\combined_features_unified_vector.csv'
    train_loader, test_loader = create_data_loaders(file_path)
    
    # 查看数据形状
    for seq_features, current_features, labels in train_loader:
        print(f"Sequence features shape: {seq_features.shape}")
        print(f"Current features shape: {current_features.shape}")
        print(f"Labels shape: {labels.shape}")
        break