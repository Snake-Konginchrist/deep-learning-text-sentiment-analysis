# -*- coding: utf-8 -*-
"""
TextCNN情感分析模型
用途：基于卷积神经网络的文本分类模型，适合短文本情感分析
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Any

class TextCNN(nn.Module):
    """
    TextCNN模型类
    用途：使用多种尺寸的卷积核提取文本特征进行情感分类
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化TextCNN模型
        参数：
            config: 模型配置字典，包含以下参数：
                - vocab_size: 词汇表大小
                - embedding_dim: 词嵌入维度  
                - num_filters: 每种卷积核的数量
                - filter_sizes: 卷积核尺寸列表
                - dropout: dropout概率
                - num_classes: 分类数量（默认2，正负情感）
        """
        super(TextCNN, self).__init__()
        
        # 从配置中获取参数
        self.vocab_size = config['vocab_size']
        self.embedding_dim = config['embedding_dim']
        self.num_filters = config['num_filters']
        self.filter_sizes = config['filter_sizes']
        self.dropout = config['dropout']
        self.num_classes = config.get('num_classes', 2)
        
        # 词嵌入层
        self.embedding = nn.Embedding(
            num_embeddings=self.vocab_size,
            embedding_dim=self.embedding_dim,
            padding_idx=0  # 0作为padding标记
        )
        
        # 多个不同尺寸的卷积层
        self.convs = nn.ModuleList([
            nn.Conv2d(
                in_channels=1,  # 输入通道数（词嵌入看作单通道图像）
                out_channels=self.num_filters,  # 输出通道数（卷积核数量）
                kernel_size=(filter_size, self.embedding_dim)  # 卷积核尺寸
            )
            for filter_size in self.filter_sizes
        ])
        
        # Dropout层防止过拟合
        self.dropout_layer = nn.Dropout(self.dropout)
        
        # 全连接分类层
        self.fc = nn.Linear(
            in_features=len(self.filter_sizes) * self.num_filters,  # 所有卷积特征拼接
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
        
        # 添加通道维度用于卷积：(batch_size, seq_length, embedding_dim) -> (batch_size, 1, seq_length, embedding_dim)
        embedded = embedded.unsqueeze(1)
        
        # 对每个卷积核尺寸进行卷积和池化
        conv_outputs = []
        for conv in self.convs:
            # 卷积操作：(batch_size, 1, seq_length, embedding_dim) -> (batch_size, num_filters, conv_seq_length, 1)
            conv_out = F.relu(conv(embedded))
            
            # 去除最后一个维度：(batch_size, num_filters, conv_seq_length, 1) -> (batch_size, num_filters, conv_seq_length)
            conv_out = conv_out.squeeze(3)
            
            # 最大池化：(batch_size, num_filters, conv_seq_length) -> (batch_size, num_filters, 1)
            pooled = F.max_pool1d(conv_out, kernel_size=conv_out.size(2))
            
            # 去除池化维度：(batch_size, num_filters, 1) -> (batch_size, num_filters)
            pooled = pooled.squeeze(2)
            
            conv_outputs.append(pooled)
        
        # 拼接所有卷积特征：(batch_size, len(filter_sizes) * num_filters)
        concatenated = torch.cat(conv_outputs, dim=1)
        
        # 应用dropout
        dropped = self.dropout_layer(concatenated)
        
        # 全连接分类：(batch_size, len(filter_sizes) * num_filters) -> (batch_size, num_classes)
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
    def create_model(cls, vocab_size: int, config_name: str = "textcnn"):
        """
        创建TextCNN模型实例
        参数：
            vocab_size: 词汇表大小
            config_name: 配置名称
        返回值：TextCNN模型实例
        使用场景：根据预定义配置快速创建模型
        """
        from ..utils.config import Config
        
        # 获取模型配置
        model_config = Config.MODEL_CONFIGS[config_name].copy()
        model_config['vocab_size'] = vocab_size
        
        return cls(model_config) 