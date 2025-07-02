# -*- coding: utf-8 -*-
"""
模型训练器
用途：提供完整的模型训练、验证、评估和保存功能
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from pathlib import Path
import json
from tqdm import tqdm
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns

from ..utils.config import Config
from ..utils.text_processor import TextProcessor
from ..architectures.textcnn import TextCNN
from ..architectures.bilstm import BiLSTM
from ..architectures.bert_model import BertSentimentModel, BertTokenizerWrapper

class SentimentDataset(Dataset):
    """
    情感分析数据集类
    用途：将预处理后的数据转换为PyTorch Dataset格式
    """
    
    def __init__(self, data: List[Dict], vocab: Dict = None, is_bert: bool = False):
        """
        初始化数据集
        参数：
            data: 处理后的数据列表
            vocab: 词汇表（非BERT模型需要）
            is_bert: 是否为BERT模型
        """
        self.data = data
        self.vocab = vocab
        self.is_bert = is_bert
    
    def __len__(self) -> int:
        return len(self.data)
    
    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        item = self.data[idx]
        
        if self.is_bert:
            # BERT模型数据格式
            return {
                'input_ids': torch.tensor(item['input_ids'], dtype=torch.long),
                'attention_mask': torch.tensor(item['attention_mask'], dtype=torch.long),
                'labels': torch.tensor(item['label'], dtype=torch.long)
            }
        else:
            # 传统模型数据格式
            return {
                'input_ids': torch.tensor(item['input_ids'], dtype=torch.long),
                'labels': torch.tensor(item['label'], dtype=torch.long)
            }

class ModelTrainer:
    """
    模型训练器类
    用途：管理模型训练的完整流程
    """
    
    def __init__(self, model_type: str, language: str = "chinese"):
        """
        初始化训练器
        参数：
            model_type: 模型类型 (textcnn/bilstm/bert)
            language: 语言类型 (chinese/english)
        """
        self.model_type = model_type
        self.language = language
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # 初始化组件
        self.text_processor = TextProcessor(language)
        self.model = None
        self.vocab = None
        self.tokenizer = None
        self.train_loader = None
        self.val_loader = None
        self.test_loader = None
        
        # 训练历史
        self.training_history = {
            'train_loss': [],
            'train_acc': [],
            'val_loss': [],
            'val_acc': []
        }
        
        print(f"初始化训练器: {model_type} ({language}), 设备: {self.device}")

    def build_vocab(self, dataset, min_freq: int = 2) -> Dict[str, int]:
        """
        构建词汇表
        参数：
            dataset: 训练数据集
            min_freq: 最小词频阈值
        返回值：词汇表字典
        """
        print("构建词汇表...")
        word_counts = Counter()
        
        for example in tqdm(dataset, desc="统计词频"):
            tokens = self.text_processor.tokenize(example["text"])
            word_counts.update(tokens)
        
        # 创建词汇表
        vocab = {"<PAD>": 0, "<UNK>": 1}
        vocab_size = 2
        
        for word, count in word_counts.most_common():
            if count >= min_freq:
                vocab[word] = vocab_size
                vocab_size += 1
        
        print(f"词汇表构建完成，大小: {len(vocab)}")
        return vocab

    def prepare_data(self, train_data, val_data, test_data, max_length: int = None) -> None:
        """
        准备训练数据
        参数：
            train_data, val_data, test_data: 原始数据集
            max_length: 最大序列长度
        """
        print("准备训练数据...")
        
        if max_length is None:
            max_length = Config.MODEL_CONFIGS[self.model_type]['max_seq_length']
        
        if self.model_type == "bert":
            # BERT数据预处理
            self._prepare_bert_data(train_data, val_data, test_data, max_length)
        else:
            # 传统模型数据预处理
            self._prepare_traditional_data(train_data, val_data, test_data, max_length)
    
    def _prepare_bert_data(self, train_data, val_data, test_data, max_length: int) -> None:
        """
        准备BERT模型数据
        """
        # 初始化BERT tokenizer
        model_name = "bert-base-chinese" if self.language == "chinese" else "bert-base-uncased"
        self.tokenizer = BertTokenizerWrapper(model_name)
        
        # 处理各个数据集
        train_encoded = self._encode_bert_dataset(train_data, max_length)
        val_encoded = self._encode_bert_dataset(val_data, max_length)
        test_encoded = self._encode_bert_dataset(test_data, max_length)
        
        # 创建数据加载器
        batch_size = Config.TRAINING_CONFIG['batch_size']
        self.train_loader = DataLoader(
            SentimentDataset(train_encoded, is_bert=True),
            batch_size=batch_size, shuffle=True
        )
        self.val_loader = DataLoader(
            SentimentDataset(val_encoded, is_bert=True),
            batch_size=batch_size, shuffle=False
        )
        self.test_loader = DataLoader(
            SentimentDataset(test_encoded, is_bert=True),
            batch_size=batch_size, shuffle=False
        )
    
    def _prepare_traditional_data(self, train_data, val_data, test_data, max_length: int) -> None:
        """
        准备传统模型数据
        """
        # 构建词汇表
        self.vocab = self.build_vocab(train_data)
        
        # 编码数据集
        train_encoded = self._encode_traditional_dataset(train_data, max_length)
        val_encoded = self._encode_traditional_dataset(val_data, max_length)
        test_encoded = self._encode_traditional_dataset(test_data, max_length)
        
        # 创建数据加载器
        batch_size = Config.TRAINING_CONFIG['batch_size']
        self.train_loader = DataLoader(
            SentimentDataset(train_encoded, self.vocab),
            batch_size=batch_size, shuffle=True
        )
        self.val_loader = DataLoader(
            SentimentDataset(val_encoded, self.vocab),
            batch_size=batch_size, shuffle=False
        )
        self.test_loader = DataLoader(
            SentimentDataset(test_encoded, self.vocab),
            batch_size=batch_size, shuffle=False
        )

    def _encode_bert_dataset(self, dataset, max_length: int) -> List[Dict]:
        """
        编码BERT数据集
        """
        texts = [example["text"] for example in dataset]
        labels = [example["label"] for example in dataset]
        
        # 使用tokenizer编码
        encoded = self.tokenizer.encode_texts(texts, max_length=max_length)
        
        # 转换为列表格式
        encoded_data = []
        for i in range(len(texts)):
            encoded_data.append({
                'input_ids': encoded['input_ids'][i].tolist(),
                'attention_mask': encoded['attention_mask'][i].tolist(),
                'label': labels[i]
            })
        
        return encoded_data

    def _encode_traditional_dataset(self, dataset, max_length: int) -> List[Dict]:
        """
        编码传统模型数据集
        """
        encoded_data = []
        
        for example in tqdm(dataset, desc="编码数据"):
            tokens = self.text_processor.tokenize(example["text"])
            
            # 转换为ID序列
            token_ids = [self.vocab.get(token, self.vocab["<UNK>"]) for token in tokens]
            
            # 截断或填充
            if len(token_ids) > max_length:
                token_ids = token_ids[:max_length]
            else:
                token_ids = token_ids + [self.vocab["<PAD>"]] * (max_length - len(token_ids))
            
            encoded_data.append({
                'input_ids': token_ids,
                'label': example["label"]
            })
        
        return encoded_data

    def create_model(self) -> nn.Module:
        """
        创建模型
        返回值：初始化的模型
        """
        print(f"创建{self.model_type}模型...")
        
        if self.model_type == "bert":
            self.model = BertSentimentModel.create_model(self.language)
        elif self.model_type == "textcnn":
            vocab_size = len(self.vocab)
            self.model = TextCNN.create_model(vocab_size)
        elif self.model_type == "bilstm":
            vocab_size = len(self.vocab)
            self.model = BiLSTM.create_model(vocab_size)
        else:
            raise ValueError(f"不支持的模型类型: {self.model_type}")
        
        # 移动到设备
        self.model.to(self.device)
        
        # 打印模型信息
        total_params = sum(p.numel() for p in self.model.parameters())
        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        print(f"模型参数总数: {total_params:,}")
        print(f"可训练参数: {trainable_params:,}")
        
        return self.model 