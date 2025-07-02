# -*- coding: utf-8 -*-
"""
训练管理器
用途：统一管理三种模型（TextCNN、BiLSTM、BERT）的训练流程
"""

import torch
from torch.utils.data import Dataset, DataLoader
from typing import Dict, List, Tuple, Any, Optional, Callable
from pathlib import Path
import json
from collections import Counter
from tqdm import tqdm

from ..utils.config import Config
from ..utils.text_processor import TextProcessor
from ..scripts.dataset_loader import DatasetLoader
from .textcnn_trainer import TextCNNTrainer
from .bilstm_trainer import BiLSTMTrainer
from .bert_trainer import BertTrainer


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


class TrainerManager:
    """
    训练管理器类
    用途：统一管理不同模型的训练流程
    """
    
    def __init__(self, model_type: str, language: str = "chinese", 
                 progress_callback: Optional[Callable] = None):
        """
        初始化训练管理器
        参数：
            model_type: 模型类型 (textcnn/bilstm/bert)
            language: 语言类型 (chinese/english)
            progress_callback: 进度回调函数
        """
        self.model_type = model_type
        self.language = language
        self.progress_callback = progress_callback
        self.text_processor = TextProcessor(language)
        
        # 数据相关
        self.vocab = None
        self.train_loader = None
        self.val_loader = None
        self.test_loader = None
        
        # 训练器
        self.trainer = None
        
        # 确保支持的模型类型
        if model_type not in ["textcnn", "bilstm", "bert"]:
            raise ValueError(f"不支持的模型类型: {model_type}")
        
        print(f"初始化训练管理器: {model_type} ({language})")
    
    def _update_progress(self, progress: int, message: str) -> None:
        """
        更新训练进度
        参数：
            progress: 进度百分比
            message: 进度消息
        """
        if self.progress_callback:
            self.progress_callback(progress, message)
    
    def build_vocab(self, dataset, min_freq: int = 2) -> Dict[str, int]:
        """
        构建词汇表（仅用于传统模型）
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
        self._update_progress(20, "准备训练数据...")
        
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
        from ..architectures.bert_model import BertTokenizerWrapper
        
        # 初始化BERT tokenizer
        model_name = "bert-base-chinese" if self.language == "chinese" else "bert-base-uncased"
        tokenizer = BertTokenizerWrapper(model_name)
        
        # 处理各个数据集
        train_encoded = self._encode_bert_dataset(train_data, tokenizer, max_length)
        val_encoded = self._encode_bert_dataset(val_data, tokenizer, max_length)
        test_encoded = self._encode_bert_dataset(test_data, tokenizer, max_length)
        
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
    
    def _encode_bert_dataset(self, dataset, tokenizer, max_length: int) -> List[Dict]:
        """
        编码BERT数据集
        """
        texts = [example["text"] for example in dataset]
        labels = [example["label"] for example in dataset]
        
        # 使用tokenizer编码
        encoded = tokenizer.encode_texts(texts, max_length=max_length)
        
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
    
    def train(self, epochs: int = None, learning_rate: float = None, 
              batch_size: int = None) -> Dict[str, Any]:
        """
        启动训练流程
        参数：
            epochs: 训练轮数
            learning_rate: 学习率
            batch_size: 批次大小
        返回值：训练结果字典
        """
        self._update_progress(30, "创建训练器...")
        
        # 使用默认参数
        if epochs is None:
            epochs = Config.TRAINING_CONFIG['num_epochs']
            # BERT通常需要较少的轮数
            if self.model_type == "bert":
                epochs = min(epochs, 3)
        
        # 创建对应的训练器
        if self.model_type == "textcnn":
            self.trainer = TextCNNTrainer(self.language, self.vocab)
        elif self.model_type == "bilstm":
            self.trainer = BiLSTMTrainer(self.language, self.vocab)
        elif self.model_type == "bert":
            self.trainer = BertTrainer(self.language)
        
        # 创建模型
        self._update_progress(40, "创建模型...")
        model = self.trainer.create_model()
        
        # 开始训练
        self._update_progress(50, "开始训练...")
        results = self.trainer.train(
            self.train_loader, 
            self.val_loader, 
            epochs=epochs, 
            save_best=True
        )
        
        # 测试模型
        self._update_progress(90, "测试模型...")
        test_results = self.trainer.evaluate(self.test_loader)
        results['test_results'] = test_results
        
        self._update_progress(100, "训练完成")
        
        return results
    
    def load_data(self, max_samples: int = None) -> Tuple:
        """
        加载训练数据
        参数：
            max_samples: 最大样本数量
        返回值：(train_data, val_data, test_data)
        """
        self._update_progress(10, "加载数据集...")
        
        # 智能加载数据（优先使用已下载的数据集）
        loader = DatasetLoader(language=self.language)
        train_data, val_data, test_data = loader.get_or_download_data(max_samples)
        
        return train_data, val_data, test_data
    
    def full_training_pipeline(self, epochs: int = None, learning_rate: float = None, 
                              batch_size: int = None, max_samples: int = None) -> Dict[str, Any]:
        """
        完整的训练流水线
        参数：
            epochs: 训练轮数
            learning_rate: 学习率
            batch_size: 批次大小
            max_samples: 最大样本数量
        返回值：训练结果字典
        """
        try:
            # 加载数据
            train_data, val_data, test_data = self.load_data(max_samples)
            
            # 准备数据
            self.prepare_data(train_data, val_data, test_data)
            
            # 训练模型
            results = self.train(epochs, learning_rate, batch_size)
            
            return results
            
        except Exception as e:
            error_msg = f"训练过程中发生错误: {str(e)}"
            print(error_msg)
            self._update_progress(-1, error_msg)
            raise e 