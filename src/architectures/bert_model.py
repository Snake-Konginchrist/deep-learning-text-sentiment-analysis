# -*- coding: utf-8 -*-
"""
BERT情感分析模型
用途：基于预训练BERT模型的文本分类，利用Transformer架构进行情感分析
"""

import torch
import torch.nn as nn
from transformers import AutoModel, AutoTokenizer
from typing import Dict, Any, Optional

class BertSentimentModel(nn.Module):
    """
    BERT情感分析模型类
    用途：使用预训练BERT模型进行文本情感分类
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化BERT模型
        参数：
            config: 模型配置字典，包含以下参数：
                - model_name: BERT模型名称（如"bert-base-chinese"）
                - num_classes: 分类数量（默认2，正负情感）
                - dropout: dropout概率
                - freeze_bert: 是否冻结BERT参数
        """
        super(BertSentimentModel, self).__init__()
        
        # 从配置中获取参数
        self.model_name = config['model_name']
        self.num_classes = config.get('num_classes', 2)
        self.dropout_rate = config.get('dropout', 0.1)
        self.freeze_bert = config.get('freeze_bert', False)
        
        # 加载预训练BERT模型
        self.bert = AutoModel.from_pretrained(self.model_name)
        
        # 获取BERT隐藏层维度
        self.bert_hidden_size = self.bert.config.hidden_size
        
        # 冻结BERT参数（可选）
        if self.freeze_bert:
            for param in self.bert.parameters():
                param.requires_grad = False
        
        # Dropout层
        self.dropout = nn.Dropout(self.dropout_rate)
        
        # 分类头
        self.classifier = nn.Linear(self.bert_hidden_size, self.num_classes)
        
        # 初始化分类头权重
        nn.init.normal_(self.classifier.weight, std=0.02)
        nn.init.zeros_(self.classifier.bias)
    
    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor = None, 
                token_type_ids: torch.Tensor = None) -> torch.Tensor:
        """
        前向传播
        参数：
            input_ids: 输入token的ID序列，形状为 (batch_size, seq_length)
            attention_mask: 注意力掩码，形状为 (batch_size, seq_length)
            token_type_ids: token类型ID，形状为 (batch_size, seq_length)
        返回值：分类logits，形状为 (batch_size, num_classes)
        """
        # BERT编码
        # outputs包含：last_hidden_state, pooler_output等
        outputs = self.bert(
            input_ids=input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids
        )
        
        # 使用[CLS]标记的表示作为句子表示
        # pooler_output是[CLS]标记经过线性层和tanh激活后的输出
        pooled_output = outputs.pooler_output  # (batch_size, bert_hidden_size)
        
        # 应用dropout
        pooled_output = self.dropout(pooled_output)
        
        # 分类
        logits = self.classifier(pooled_output)  # (batch_size, num_classes)
        
        return logits
    
    def predict(self, input_ids: torch.Tensor, attention_mask: torch.Tensor = None, 
                token_type_ids: torch.Tensor = None) -> torch.Tensor:
        """
        预测函数，返回概率分布
        参数：
            input_ids, attention_mask, token_type_ids: 同forward方法
        返回值：概率分布，形状为 (batch_size, num_classes)
        使用场景：模型推理时获取预测概率
        """
        with torch.no_grad():
            logits = self.forward(input_ids, attention_mask, token_type_ids)
            probabilities = torch.softmax(logits, dim=1)
            return probabilities
    
    def get_embeddings(self, input_ids: torch.Tensor, attention_mask: torch.Tensor = None,
                      token_type_ids: torch.Tensor = None) -> torch.Tensor:
        """
        获取BERT编码的文本表示
        参数：
            input_ids, attention_mask, token_type_ids: 同forward方法
        返回值：文本向量表示，形状为 (batch_size, bert_hidden_size)
        使用场景：获取文本的向量表示用于其他任务
        """
        with torch.no_grad():
            outputs = self.bert(
                input_ids=input_ids,
                attention_mask=attention_mask,
                token_type_ids=token_type_ids
            )
            return outputs.pooler_output
    
    @classmethod
    def create_model(cls, language: str = "chinese", config_name: str = "bert"):
        """
        创建BERT模型实例
        参数：
            language: 语言类型，影响模型选择
            config_name: 配置名称
        返回值：BertSentimentModel模型实例
        使用场景：根据语言和配置快速创建模型
        """
        from ..utils.config import Config
        
        # 获取基础配置
        model_config = Config.MODEL_CONFIGS[config_name].copy()
        
        # 根据语言选择合适的BERT模型
        if language == "chinese":
            model_config['model_name'] = "bert-base-chinese"
        else:
            model_config['model_name'] = "bert-base-uncased"
        
        return cls(model_config)

class BertTokenizerWrapper:
    """
    BERT分词器包装类
    用途：统一BERT模型的文本预处理接口
    """
    
    def __init__(self, model_name: str):
        """
        初始化分词器
        参数：
            model_name: BERT模型名称
        """
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model_name = model_name
    
    def encode_texts(self, texts: list, max_length: int = 512, 
                    padding: bool = True, truncation: bool = True) -> Dict[str, torch.Tensor]:
        """
        编码文本列表
        参数：
            texts: 文本列表
            max_length: 最大序列长度
            padding: 是否填充
            truncation: 是否截断
        返回值：包含input_ids、attention_mask等的字典
        使用场景：将文本转换为BERT输入格式
        """
        # 使用tokenizer编码文本
        encoded = self.tokenizer(
            texts,
            max_length=max_length,
            padding=padding,
            truncation=truncation,
            return_tensors="pt"
        )
        
        return encoded
    
    def decode_tokens(self, token_ids: torch.Tensor) -> list:
        """
        解码token ID为文本
        参数：
            token_ids: token ID张量
        返回值：解码后的文本列表
        使用场景：将模型输出的token ID转换回文本
        """
        return self.tokenizer.batch_decode(token_ids, skip_special_tokens=True) 