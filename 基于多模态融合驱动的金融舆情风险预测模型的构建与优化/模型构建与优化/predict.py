import torch
import numpy as np
import pandas as pd
from model import MultiModalFinancialModel
import os

# 检查是否有GPU可用
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

class FinancialPredictor:
    def __init__(self, model_path, input_dim=3763, hidden_dim=64, num_layers=2, nhead=4, dropout=0.2):
        # 初始化模型
        self.model = MultiModalFinancialModel(
            input_dim, hidden_dim, num_layers, nhead, dropout
        ).to(device)
        
        # 加载模型权重
        if os.path.exists(model_path):
            self.model.load_state_dict(torch.load(model_path, map_location=device))
            self.model.eval()
            print(f"Model loaded successfully from {model_path}")
        else:
            raise FileNotFoundError(f"Model file not found: {model_path}")
    
    def predict(self, seq_features, current_features):
        """
        进行预测
        
        参数:
        seq_features: 时间序列特征，形状为 [seq_length, input_dim]
        current_features: 当前特征，形状为 [input_dim]
        
        返回:
        预测的金融影响指标，范围在[-1, 1]
        """
        # 转换为张量
        seq_tensor = torch.tensor(seq_features, dtype=torch.float32).unsqueeze(0).to(device)  # [1, seq_length, input_dim]
        current_tensor = torch.tensor(current_features, dtype=torch.float32).unsqueeze(0).to(device)  # [1, input_dim]
        
        # 前向传播
        with torch.no_grad():
            output = self.model(seq_tensor, current_tensor)
        
        # 获取预测结果
        prediction = output.item()
        return prediction
    
    def predict_from_csv(self, file_path, seq_length=3, start_date=None):
        """
        从CSV文件中读取数据并进行预测
        
        参数:
        file_path: CSV文件路径
        seq_length: 时间序列长度
        start_date: 开始预测的日期（可选）
        
        返回:
        包含日期和预测结果的列表
        """
        # 读取CSV文件
        df = pd.read_csv(file_path)
        dates = df['date'].values
        features = df.iloc[:, 1:].values.astype(np.float32)
        
        # 如果指定了开始日期，找到对应的索引
        start_idx = 0
        if start_date is not None:
            start_idx = np.where(dates == start_date)[0]
            if len(start_idx) == 0:
                print(f"Start date {start_date} not found in dataset")
                return []
            start_idx = start_idx[0]
            
        # 确保有足够的数据进行预测
        results = []
        for i in range(start_idx, len(features) - seq_length + 1):
            # 获取时间序列特征和当前特征
            seq_feat = features[i:i+seq_length]
            current_feat = features[i+seq_length-1]
            
            # 进行预测
            pred = self.predict(seq_feat, current_feat)
            
            # 记录结果
            result_date = dates[i+seq_length-1]
            results.append((result_date, pred))
        
        return results

def main():
    # 配置参数
    model_path = r'd:\srtp03\saved_model.pth'
    file_path = r'd:\srtp03\dataset\combined_features_unified_vector.csv'
    
    try:
        # 创建预测器实例
        predictor = FinancialPredictor(model_path)
        
        # 从CSV文件中进行预测
        print("Predicting from CSV file...")
        predictions = predictor.predict_from_csv(file_path)
        
        # 打印预测结果
        print("Prediction results:")
        for date, pred in predictions[-5:]:  # 只打印最后5个结果
            impact = "Positive" if pred > 0 else "Negative" if pred < 0 else "Neutral"
            print(f"Date: {date}, Predict   ion: {pred:.4f} ({impact})")
            
        # 如果用户想要测试特定的输入特征
        # 这里可以添加交互式输入或从其他来源获取特征的代码
        
    except Exception as e:
        print(f"Error during prediction: {e}")

if __name__ == "__main__":
    main()