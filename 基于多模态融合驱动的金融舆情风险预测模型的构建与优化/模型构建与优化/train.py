import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import matplotlib.pyplot as plt
import os
from data_loader import create_data_loaders
from model import MultiModalFinancialModel

# 设置随机种子以保证结果可复现
seed = 42
torch.manual_seed(seed)
np.random.seed(seed)

# 检查是否有GPU可用
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

def train_model():
    # 配置参数
    file_path = r'd:\srtp03\dataset\combined_features_unified_vector.csv'
    seq_length = 3
    batch_size = 32
    input_dim = 3763  # 特征维度（除去日期列）
    hidden_dim = 64
    num_layers = 2
    nhead = 4
    dropout = 0.2
    learning_rate = 0.001
    num_epochs = 50
    
    # 创建数据加载器
    train_loader, test_loader = create_data_loaders(
        file_path, seq_length, batch_size
    )
    
    # 初始化模型
    model = MultiModalFinancialModel(
        input_dim, hidden_dim, num_layers, nhead, dropout
    ).to(device)
    
    # 定义损失函数和优化器
    criterion = nn.MSELoss()  # 对于回归任务，使用均方误差
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    
    # 学习率调度器
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='min', factor=0.5, patience=5, verbose=True
    )
    
    # 记录训练过程
    train_losses = []
    test_losses = []
    best_test_loss = float('inf')
    
    # 训练循环
    for epoch in range(num_epochs):
        model.train()
        train_loss = 0.0
        
        for seq_features, current_features, labels in train_loader:
            # 移至设备
            seq_features = seq_features.to(device)
            current_features = current_features.to(device)
            labels = labels.to(device)
            
            # 前向传播
            outputs = model(seq_features, current_features)
            loss = criterion(outputs, labels)
            
            # 反向传播和优化
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item() * seq_features.size(0)
        
        # 计算平均训练损失
        train_loss /= len(train_loader.dataset)
        train_losses.append(train_loss)
        
        # 在测试集上评估
        model.eval()
        test_loss = 0.0
        
        with torch.no_grad():
            for seq_features, current_features, labels in test_loader:
                # 移至设备
                seq_features = seq_features.to(device)
                current_features = current_features.to(device)
                labels = labels.to(device)
                
                # 前向传播
                outputs = model(seq_features, current_features)
                loss = criterion(outputs, labels)
                
                test_loss += loss.item() * seq_features.size(0)
        
        # 计算平均测试损失
        test_loss /= len(test_loader.dataset)
        test_losses.append(test_loss)
        
        # 更新学习率
        scheduler.step(test_loss)
        
        # 打印训练进度
        print(f'Epoch [{epoch+1}/{num_epochs}], Train Loss: {train_loss:.6f}, Test Loss: {test_loss:.6f}')
        
        # 保存最好的模型
        if test_loss < best_test_loss:
            best_test_loss = test_loss
            torch.save(model.state_dict(), r'd:\srtp03\saved_model.pth')
            print(f'Best model saved with test loss: {best_test_loss:.6f}')
    
    # 绘制损失曲线
    plt.figure(figsize=(10, 6))
    plt.plot(range(1, num_epochs+1), train_losses, label='Train Loss')
    plt.plot(range(1, num_epochs+1), test_losses, label='Test Loss')
    plt.title('Training and Testing Loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)
    plt.savefig(r'd:\srtp03\loss_curve.png')
    print('Loss curve saved as loss_curve.png')
    
if __name__ == "__main__":
    train_model()