# -*- coding: utf-8 -*-
"""
BiLSTM情感分析模型
用途：基于双向长短期记忆网络的文本分类模型，擅长捕获序列上下文信息
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Any

class BiLSTM(nn.Module):
    """
    BiLSTM模型类
    用途：使用双向LSTM捕获文本序列的前后文信息进行情感分类
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化BiLSTM模型
        参数：
            config: 模型配置字典，包含以下参数：
                - vocab_size: 词汇表大小
                - embedding_dim: 词嵌入维度
                - hidden_dim: LSTM隐藏层维度
                - num_layers: LSTM层数
                - dropout: dropout概率
                - num_classes: 分类数量（默认2，正负情感）
        """
        super(BiLSTM, self).__init__()
        
        # 从配置中获取参数
        self.vocab_size = config['vocab_size']
        self.embedding_dim = config['embedding_dim']
        self.hidden_dim = config['hidden_dim']
        self.num_layers = config['num_layers']
        self.dropout = config['dropout']
        self.num_classes = config.get('num_classes', 2)
        
        # 词嵌入层
        self.embedding = nn.Embedding(
            num_embeddings=self.vocab_size,
            embedding_dim=self.embedding_dim,
            padding_idx=0  # 0作为padding标记
        )
        
        # 双向LSTM层
        self.lstm = nn.LSTM(
            input_size=self.embedding_dim,
            hidden_size=self.hidden_dim,
            num_layers=self.num_layers,
            batch_first=True,  # 输入格式为(batch, seq, feature)
            bidirectional=True,  # 双向LSTM
            dropout=self.dropout if self.num_layers > 1 else 0  # 只有多层时才在LSTM间使用dropout
        )
        
        # Dropout层防止过拟合
        self.dropout_layer = nn.Dropout(self.dropout)
        
        # 全连接分类层
        # 双向LSTM输出维度是hidden_dim * 2
        self.fc = nn.Linear(
            in_features=self.hidden_dim * 2,
            out_features=self.num_classes
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        前向传播
        参数：
            x: 输入张量，形状为 (batch_size, seq_length)
        返回值：分类logits，形状为 (batch_size, num_classes)
        """
        # 词嵌入：(batch_size, seq_length) -> (batch_size, seq_length, embedding_dim)
        embedded = self.embedding(x)
        
        # LSTM处理序列
        # lstm_out: (batch_size, seq_length, hidden_dim * 2)
        # hidden: (num_layers * 2, batch_size, hidden_dim) - 最终隐藏状态
        # cell: (num_layers * 2, batch_size, hidden_dim) - 最终细胞状态
        lstm_out, (hidden, cell) = self.lstm(embedded)
        
        # 取最后一个时间步的输出作为序列表示
        # 由于是双向LSTM，需要拼接前向和后向的最后隐藏状态
        # hidden的形状：(num_layers * 2, batch_size, hidden_dim)
        
        # 前向LSTM的最后隐藏状态（最后一层）
        forward_hidden = hidden[-2, :, :]  # (batch_size, hidden_dim)
        
        # 后向LSTM的最后隐藏状态（最后一层）
        backward_hidden = hidden[-1, :, :]  # (batch_size, hidden_dim)
        
        # 拼接前向和后向隐藏状态
        final_hidden = torch.cat((forward_hidden, backward_hidden), dim=1)  # (batch_size, hidden_dim * 2)
        
        # 应用dropout
        dropped = self.dropout_layer(final_hidden)
        
        # 全连接分类：(batch_size, hidden_dim * 2) -> (batch_size, num_classes)
        logits = self.fc(dropped)
        
        return logits
    
    def forward_with_attention(self, x: torch.Tensor) -> torch.Tensor:
        """
        带注意力机制的前向传播（可选实现）
        参数：
            x: 输入张量，形状为 (batch_size, seq_length)
        返回值：分类logits，形状为 (batch_size, num_classes)
        使用场景：需要注意力权重的场景
        """
        # 词嵌入
        embedded = self.embedding(x)
        
        # LSTM处理
        lstm_out, _ = self.lstm(embedded)  # (batch_size, seq_length, hidden_dim * 2)
        
        # 简单的自注意力机制
        # 计算注意力分数
        attention_scores = torch.tanh(lstm_out)  # (batch_size, seq_length, hidden_dim * 2)
        attention_scores = torch.mean(attention_scores, dim=2)  # (batch_size, seq_length)
        
        # 应用softmax获得注意力权重
        attention_weights = F.softmax(attention_scores, dim=1)  # (batch_size, seq_length)
        
        # 加权求和得到序列表示
        # lstm_out: (batch_size, seq_length, hidden_dim * 2)
        # attention_weights: (batch_size, seq_length, 1)
        attention_weights = attention_weights.unsqueeze(2)  # (batch_size, seq_length, 1)
        
        # 加权平均
        weighted_output = torch.sum(lstm_out * attention_weights, dim=1)  # (batch_size, hidden_dim * 2)
        
        # Dropout和分类
        dropped = self.dropout_layer(weighted_output)
        logits = self.fc(dropped)
        
        return logits
    
    def predict(self, x: torch.Tensor) -> torch.Tensor:
        """
        预测函数，返回概率分布
        参数：
            x: 输入张量
        返回值：概率分布，形状为 (batch_size, num_classes)
        使用场景：模型推理时获取预测概率
        """
        with torch.no_grad():
            logits = self.forward(x)
            probabilities = F.softmax(logits, dim=1)
            return probabilities
    
    @classmethod
    def create_model(cls, vocab_size: int, config_name: str = "bilstm"):
        """
        创建BiLSTM模型实例
        参数：
            vocab_size: 词汇表大小
            config_name: 配置名称
        返回值：BiLSTM模型实例
        使用场景：根据预定义配置快速创建模型
        """
        from ..utils.config import Config
        
        # 获取模型配置
        model_config = Config.MODEL_CONFIGS[config_name].copy()
        model_config['vocab_size'] = vocab_size
        
        return cls(model_config) 