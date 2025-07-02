# -*- coding: utf-8 -*-
"""
情感分析推理服务
用途：提供统一的情感分析接口，支持多种模型的推理和结果处理
"""

import torch
import numpy as np
from typing import Dict, List, Union, Tuple
from pathlib import Path

from ..utils.config import Config
from ..utils.text_processor import TextProcessor
from ..architectures.textcnn import TextCNN
from ..architectures.bilstm import BiLSTM
from ..architectures.bert_model import BertSentimentModel, BertTokenizerWrapper

class SentimentAnalyzer:
    """
    情感分析器类
    用途：统一管理多种模型的加载和推理，提供情感分析服务
    """
    
    def __init__(self, model_type: str = "bert", language: str = "chinese"):
        """
        初始化情感分析器
        参数：
            model_type: 模型类型，支持 "textcnn", "bilstm", "bert"
            language: 语言类型，支持 "chinese", "english"
        """
        self.model_type = model_type
        self.language = language
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # 初始化文本处理器
        self.text_processor = TextProcessor(language)
        
        # 模型和相关组件
        self.model = None
        self.vocab = None
        self.tokenizer = None
        
        # 情感标签映射
        self.label_map = {0: "负面", 1: "正面"}
        if language == "english":
            self.label_map = {0: "negative", 1: "positive"}
        
        print(f"初始化情感分析器: 模型={model_type}, 语言={language}, 设备={self.device}")
    
    def load_model(self, model_path: str = None) -> None:
        """
        加载训练好的模型
        参数：
            model_path: 模型文件路径，如果为None则使用默认路径
        使用场景：在推理前加载已训练的模型
        """
        if model_path is None:
            model_path = Config.get_model_path(self.model_type, self.language)
        
        model_path = Path(model_path)
        
        if not model_path.exists():
            raise FileNotFoundError(f"模型文件不存在: {model_path}")
        
        print(f"正在加载模型: {model_path}")
        
        # 根据模型类型加载
        if self.model_type == "bert":
            self._load_bert_model(model_path)
        else:
            self._load_traditional_model(model_path)
        
        # 移动到指定设备
        self.model.to(self.device)
        self.model.eval()
        
        print("模型加载完成")
    
    def _load_bert_model(self, model_path: Path) -> None:
        """
        加载BERT模型
        参数：
            model_path: 模型文件路径
        """
        # 创建BERT模型
        self.model = BertSentimentModel.create_model(self.language)
        
        # 加载模型权重
        checkpoint = torch.load(model_path, map_location=self.device)
        if 'model_state_dict' in checkpoint:
            self.model.load_state_dict(checkpoint['model_state_dict'])
        else:
            self.model.load_state_dict(checkpoint)
        
        # 初始化tokenizer
        model_name = "bert-base-chinese" if self.language == "chinese" else "bert-base-uncased"
        self.tokenizer = BertTokenizerWrapper(model_name)
    
    def _load_traditional_model(self, model_path: Path) -> None:
        """
        加载传统模型（TextCNN、BiLSTM）
        参数：
            model_path: 模型文件路径
        """
        # 加载checkpoint
        checkpoint = torch.load(model_path, map_location=self.device)
        
        # 获取词汇表
        if 'vocab' in checkpoint:
            self.vocab = checkpoint['vocab']
        else:
            raise ValueError("模型文件中缺少词汇表信息")
        
        # 创建模型
        vocab_size = len(self.vocab)
        if self.model_type == "textcnn":
            self.model = TextCNN.create_model(vocab_size)
        elif self.model_type == "bilstm":
            self.model = BiLSTM.create_model(vocab_size)
        else:
            raise ValueError(f"不支持的模型类型: {self.model_type}")
        
        # 加载模型权重
        if 'model_state_dict' in checkpoint:
            self.model.load_state_dict(checkpoint['model_state_dict'])
        else:
            self.model.load_state_dict(checkpoint)
    
    def predict_single(self, text: str, return_proba: bool = True) -> Dict[str, Union[str, float, Dict]]:
        """
        对单个文本进行情感分析
        参数：
            text: 待分析的文本
            return_proba: 是否返回概率分布
        返回值：包含预测结果的字典
        使用场景：分析单条文本的情感倾向
        """
        if self.model is None:
            raise ValueError("请先加载模型")
        
        # 预处理文本
        if self.model_type == "bert":
            inputs = self._preprocess_bert(text)
            with torch.no_grad():
                if return_proba:
                    probs = self.model.predict(**inputs)
                    predicted_class = torch.argmax(probs, dim=1).item()
                    confidence = probs[0][predicted_class].item()
                else:
                    logits = self.model(**inputs)
                    predicted_class = torch.argmax(logits, dim=1).item()
                    confidence = torch.softmax(logits, dim=1)[0][predicted_class].item()
        else:
            inputs = self._preprocess_traditional(text)
            with torch.no_grad():
                if return_proba:
                    probs = self.model.predict(inputs)
                    predicted_class = torch.argmax(probs, dim=1).item()
                    confidence = probs[0][predicted_class].item()
                else:
                    logits = self.model(inputs)
                    predicted_class = torch.argmax(logits, dim=1).item()
                    confidence = torch.softmax(logits, dim=1)[0][predicted_class].item()
        
        # 构造返回结果
        result = {
            "text": text,
            "sentiment": self.label_map[predicted_class],
            "confidence": round(confidence, 4),
            "predicted_class": predicted_class
        }
        
        if return_proba and self.model_type == "bert":
            result["probabilities"] = {
                self.label_map[0]: round(probs[0][0].item(), 4),
                self.label_map[1]: round(probs[0][1].item(), 4)
            }
        
        return result
    
    def predict_batch(self, texts: List[str], batch_size: int = 32) -> List[Dict]:
        """
        批量进行情感分析
        参数：
            texts: 文本列表
            batch_size: 批处理大小
        返回值：预测结果列表
        使用场景：处理大量文本的情感分析
        """
        if self.model is None:
            raise ValueError("请先加载模型")
        
        results = []
        
        # 分批处理
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            batch_results = self._predict_batch_internal(batch_texts)
            results.extend(batch_results)
        
        return results
    
    def _predict_batch_internal(self, texts: List[str]) -> List[Dict]:
        """
        内部批量预测方法
        参数：
            texts: 文本列表
        返回值：预测结果列表
        """
        if self.model_type == "bert":
            return self._predict_batch_bert(texts)
        else:
            return self._predict_batch_traditional(texts)
    
    def _predict_batch_bert(self, texts: List[str]) -> List[Dict]:
        """
        BERT模型批量预测
        """
        # 预处理所有文本
        inputs = self.tokenizer.encode_texts(texts)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            probs = self.model.predict(**inputs)
            predictions = torch.argmax(probs, dim=1)
            confidences = torch.max(probs, dim=1)[0]
        
        # 构造结果
        results = []
        for i, text in enumerate(texts):
            pred_class = predictions[i].item()
            confidence = confidences[i].item()
            
            result = {
                "text": text,
                "sentiment": self.label_map[pred_class],
                "confidence": round(confidence, 4),
                "predicted_class": pred_class,
                "probabilities": {
                    self.label_map[0]: round(probs[i][0].item(), 4),
                    self.label_map[1]: round(probs[i][1].item(), 4)
                }
            }
            results.append(result)
        
        return results
    
    def _predict_batch_traditional(self, texts: List[str]) -> List[Dict]:
        """
        传统模型批量预测
        """
        # 预处理文本
        processed_texts = []
        for text in texts:
            tokens = self.text_processor.tokenize(text)
            # 转换为词汇表索引
            token_ids = [self.vocab.get(token, self.vocab.get('<UNK>', 0)) for token in tokens]
            processed_texts.append(token_ids)
        
        # 填充序列
        max_len = max(len(seq) for seq in processed_texts) if processed_texts else 1
        max_len = min(max_len, 256)  # 限制最大长度
        
        padded_texts = []
        for seq in processed_texts:
            if len(seq) > max_len:
                seq = seq[:max_len]
            else:
                seq = seq + [0] * (max_len - len(seq))
            padded_texts.append(seq)
        
        # 转换为张量
        inputs = torch.tensor(padded_texts, dtype=torch.long).to(self.device)
        
        with torch.no_grad():
            probs = self.model.predict(inputs)
            predictions = torch.argmax(probs, dim=1)
            confidences = torch.max(probs, dim=1)[0]
        
        # 构造结果
        results = []
        for i, text in enumerate(texts):
            pred_class = predictions[i].item()
            confidence = confidences[i].item()
            
            result = {
                "text": text,
                "sentiment": self.label_map[pred_class],
                "confidence": round(confidence, 4),
                "predicted_class": pred_class
            }
            results.append(result)
        
        return results
    
    def _preprocess_bert(self, text: str) -> Dict[str, torch.Tensor]:
        """
        BERT模型文本预处理
        """
        inputs = self.tokenizer.encode_texts([text])
        return {k: v.to(self.device) for k, v in inputs.items()}
    
    def _preprocess_traditional(self, text: str) -> torch.Tensor:
        """
        传统模型文本预处理
        """
        tokens = self.text_processor.tokenize(text)
        token_ids = [self.vocab.get(token, self.vocab.get('<UNK>', 0)) for token in tokens]
        
        # 限制序列长度
        max_len = 256
        if len(token_ids) > max_len:
            token_ids = token_ids[:max_len]
        else:
            token_ids = token_ids + [0] * (max_len - len(token_ids))
        
        return torch.tensor([token_ids], dtype=torch.long).to(self.device) 