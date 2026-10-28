import torch
import torch.nn as nn
import math

class MultiModalFinancialModel(nn.Module):
    def __init__(self, input_dim, hidden_dim=64, num_layers=2, nhead=4, dropout=0.2):
        super(MultiModalFinancialModel, self).__init__()
        
        # LSTM部分 - 处理时间序列数据
        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0
        )
        
        # Transformer部分 - 处理当前特征数据
        self.input_projection = nn.Linear(input_dim, hidden_dim)
        
        # Transformer编码器层
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=hidden_dim,
            nhead=nhead,
            dim_feedforward=hidden_dim * 4,
            dropout=dropout,
            batch_first=True
        )
        self.transformer_encoder = nn.TransformerEncoder(
            encoder_layer=encoder_layer,
            num_layers=num_layers
        )
        
        # 融合层
        self.fusion_layer = nn.Linear(hidden_dim * 2, hidden_dim)
        
        # 输出层 - 使用Tanh激活函数确保输出在[-1, 1]范围内
        self.output_layer = nn.Sequential(
            nn.Linear(hidden_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Tanh()
        )
        
        # 初始化权重
        self._init_weights()
    
    def _init_weights(self):
        # 初始化线性层的权重
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
    
    def forward(self, seq_features, current_features):
        # LSTM前向传播
        # seq_features形状: [batch_size, seq_length, input_dim]
        lstm_out, _ = self.lstm(seq_features)
        # 取最后一个时间步的输出
        lstm_last_hidden = lstm_out[:, -1, :]  # [batch_size, hidden_dim]
        
        # Transformer前向传播
        # current_features形状: [batch_size, input_dim]
        # 增加一个维度以匹配Transformer的输入要求
        transformed_features = self.input_projection(current_features)
        transformed_features = transformed_features.unsqueeze(1)  # [batch_size, 1, hidden_dim]
        
        # 创建自注意力掩码（这里不使用掩码）
        mask = None
        
        # Transformer编码
        transformer_out = self.transformer_encoder(transformed_features, mask)
        transformer_out = transformer_out.squeeze(1)  # [batch_size, hidden_dim]
        
        # 融合两种特征表示
        combined_features = torch.cat([lstm_last_hidden, transformer_out], dim=1)
        fused_features = self.fusion_layer(combined_features)
        fused_features = nn.functional.relu(fused_features)
        
        # 输出预测结果
        output = self.output_layer(fused_features)  # [batch_size, 1]
        
        return output.squeeze(1)  # [batch_size] - 移除最后一个维度以匹配标签形状

if __name__ == "__main__":
    # 测试模型
    input_dim = 3763  # 特征维度（除去日期列）
    model = MultiModalFinancialModel(input_dim)
    
    # 创建测试输入
    batch_size = 32
    seq_length = 3
    seq_features = torch.randn(batch_size, seq_length, input_dim)
    current_features = torch.randn(batch_size, input_dim)
    
    # 前向传播
    output = model(seq_features, current_features)
    print(f"Model output shape: {output.shape}")
    print(f"Output range: [{output.min().item():.4f}, {output.max().item():.4f}]")