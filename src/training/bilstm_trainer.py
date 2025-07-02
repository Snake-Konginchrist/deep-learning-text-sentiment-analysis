# -*- coding: utf-8 -*-
"""
BiLSTM模型训练器
用途：专门负责BiLSTM模型的训练、验证和保存
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from sklearn.metrics import accuracy_score, classification_report
import numpy as np
from typing import Dict, List, Tuple, Any
from pathlib import Path
import json
from tqdm import tqdm

from ..utils.config import Config
from ..architectures.bilstm import BiLSTM


class BiLSTMTrainer:
    """
    BiLSTM训练器类
    用途：专门处理BiLSTM模型的训练流程
    """
    
    def __init__(self, language: str = "chinese", vocab: Dict[str, int] = None):
        """
        初始化BiLSTM训练器
        参数：
            language: 语言类型
            vocab: 词汇表
        """
        self.language = language
        self.vocab = vocab
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.optimizer = None
        self.criterion = None
        
        # 训练历史记录
        self.history = {
            'train_loss': [],
            'train_acc': [],
            'val_loss': [],
            'val_acc': []
        }
        
        print(f"初始化BiLSTM训练器 ({language}), 设备: {self.device}")
    
    def create_model(self) -> nn.Module:
        """
        创建BiLSTM模型
        返回值：BiLSTM模型实例
        """
        if self.vocab is None:
            raise ValueError("词汇表不能为空")
        
        vocab_size = len(self.vocab)
        self.model = BiLSTM.create_model(vocab_size)
        self.model.to(self.device)
        
        # 初始化优化器和损失函数
        self.optimizer = optim.Adam(
            self.model.parameters(), 
            lr=Config.TRAINING_CONFIG['learning_rate']
        )
        self.criterion = nn.CrossEntropyLoss()
        
        print(f"BiLSTM模型创建完成，词汇表大小: {vocab_size}")
        return self.model
    
    def train_epoch(self, train_loader: DataLoader) -> Tuple[float, float]:
        """
        训练一个epoch
        参数：
            train_loader: 训练数据加载器
        返回值：(平均损失, 准确率)
        """
        self.model.train()
        total_loss = 0.0
        correct_predictions = 0
        total_predictions = 0
        
        progress_bar = tqdm(train_loader, desc="训练中")
        
        for batch in progress_bar:
            input_ids = batch['input_ids'].to(self.device)
            labels = batch['labels'].to(self.device)
            
            # 前向传播
            self.optimizer.zero_grad()
            outputs = self.model(input_ids)
            loss = self.criterion(outputs, labels)
            
            # 反向传播
            loss.backward()
            
            # 梯度裁剪（对RNN模型很重要）
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=5.0)
            
            self.optimizer.step()
            
            # 统计
            total_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total_predictions += labels.size(0)
            correct_predictions += (predicted == labels).sum().item()
            
            # 更新进度条
            current_acc = correct_predictions / total_predictions
            progress_bar.set_postfix({
                'Loss': f'{loss.item():.4f}',
                'Acc': f'{current_acc:.4f}'
            })
        
        avg_loss = total_loss / len(train_loader)
        accuracy = correct_predictions / total_predictions
        
        return avg_loss, accuracy
    
    def validate_epoch(self, val_loader: DataLoader) -> Tuple[float, float]:
        """
        验证一个epoch
        参数：
            val_loader: 验证数据加载器
        返回值：(平均损失, 准确率)
        """
        self.model.eval()
        total_loss = 0.0
        correct_predictions = 0
        total_predictions = 0
        
        with torch.no_grad():
            for batch in tqdm(val_loader, desc="验证中"):
                input_ids = batch['input_ids'].to(self.device)
                labels = batch['labels'].to(self.device)
                
                outputs = self.model(input_ids)
                loss = self.criterion(outputs, labels)
                
                total_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                total_predictions += labels.size(0)
                correct_predictions += (predicted == labels).sum().item()
        
        avg_loss = total_loss / len(val_loader)
        accuracy = correct_predictions / total_predictions
        
        return avg_loss, accuracy
    
    def train(self, train_loader: DataLoader, val_loader: DataLoader, 
              epochs: int = 10, save_best: bool = True) -> Dict[str, Any]:
        """
        完整训练流程
        参数：
            train_loader: 训练数据加载器
            val_loader: 验证数据加载器
            epochs: 训练轮数
            save_best: 是否保存最佳模型
        返回值：训练结果字典
        """
        print(f"开始训练BiLSTM模型，共{epochs}轮...")
        
        best_val_acc = 0.0
        best_model_state = None
        patience_counter = 0
        patience = Config.TRAINING_CONFIG.get('early_stopping_patience', 3)
        
        for epoch in range(epochs):
            print(f"\n=== Epoch {epoch + 1}/{epochs} ===")
            
            # 训练
            train_loss, train_acc = self.train_epoch(train_loader)
            
            # 验证
            val_loss, val_acc = self.validate_epoch(val_loader)
            
            # 记录历史
            self.history['train_loss'].append(train_loss)
            self.history['train_acc'].append(train_acc)
            self.history['val_loss'].append(val_loss)
            self.history['val_acc'].append(val_acc)
            
            print(f"训练损失: {train_loss:.4f}, 训练准确率: {train_acc:.4f}")
            print(f"验证损失: {val_loss:.4f}, 验证准确率: {val_acc:.4f}")
            
            # 保存最佳模型和早停检查
            if save_best and val_acc > best_val_acc:
                best_val_acc = val_acc
                best_model_state = self.model.state_dict().copy()
                patience_counter = 0
                print(f"★ 新的最佳模型！验证准确率: {val_acc:.4f}")
            else:
                patience_counter += 1
                if patience_counter >= patience:
                    print(f"早停触发！已连续{patience}轮无改善")
                    break
        
        # 恢复最佳模型权重
        if save_best and best_model_state is not None:
            self.model.load_state_dict(best_model_state)
            print(f"\n恢复最佳模型权重，验证准确率: {best_val_acc:.4f}")
        
        # 保存模型
        model_path = self.save_model()
        
        return {
            'model_type': 'bilstm',
            'language': self.language,
            'epochs': epoch + 1,  # 实际训练轮数
            'best_val_accuracy': best_val_acc,
            'final_train_accuracy': self.history['train_acc'][-1],
            'final_val_accuracy': self.history['val_acc'][-1],
            'model_path': str(model_path),
            'history': self.history,
            'early_stopped': patience_counter >= patience
        }
    
    def save_model(self) -> Path:
        """
        保存训练好的模型
        返回值：模型保存路径
        """
        model_path = Config.get_model_path('bilstm', self.language)
        
        # 确保目录存在
        model_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 保存模型和相关信息
        checkpoint = {
            'model_state_dict': self.model.state_dict(),
            'vocab': self.vocab,
            'model_config': Config.MODEL_CONFIGS['bilstm'],
            'language': self.language,
            'history': self.history
        }
        
        torch.save(checkpoint, model_path)
        print(f"模型已保存到: {model_path}")
        
        return model_path
    
    def evaluate(self, test_loader: DataLoader) -> Dict[str, Any]:
        """
        评估模型性能
        参数：
            test_loader: 测试数据加载器
        返回值：评估结果字典
        """
        self.model.eval()
        all_predictions = []
        all_labels = []
        
        with torch.no_grad():
            for batch in tqdm(test_loader, desc="评估中"):
                input_ids = batch['input_ids'].to(self.device)
                labels = batch['labels'].to(self.device)
                
                outputs = self.model(input_ids)
                _, predicted = torch.max(outputs.data, 1)
                
                all_predictions.extend(predicted.cpu().numpy())
                all_labels.extend(labels.cpu().numpy())
        
        # 计算指标
        accuracy = accuracy_score(all_labels, all_predictions)
        report = classification_report(all_labels, all_predictions, output_dict=True)
        
        results = {
            'accuracy': accuracy,
            'classification_report': report,
            'total_samples': len(all_labels)
        }
        
        print(f"测试准确率: {accuracy:.4f}")
        return results 