# -*- coding: utf-8 -*-
"""
BERT模型训练器
用途：专门负责BERT模型的训练、验证和保存
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
from transformers import get_linear_schedule_with_warmup

from ..utils.config import Config
from ..architectures.bert_model import BertSentimentModel, BertTokenizerWrapper


class BertTrainer:
    """
    BERT训练器类
    用途：专门处理BERT模型的训练流程
    """
    
    def __init__(self, language: str = "chinese"):
        """
        初始化BERT训练器
        参数：
            language: 语言类型
        """
        self.language = language
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.optimizer = None
        self.scheduler = None
        self.criterion = None
        self.tokenizer = None
        
        # 训练历史记录
        self.history = {
            'train_loss': [],
            'train_acc': [],
            'val_loss': [],
            'val_acc': [],
            'learning_rates': []
        }
        
        print(f"初始化BERT训练器 ({language}), 设备: {self.device}")
    
    def create_model(self) -> nn.Module:
        """
        创建BERT模型
        返回值：BERT模型实例
        """
        # 创建BERT模型
        self.model = BertSentimentModel.create_model(self.language)
        self.model.to(self.device)
        
        # 初始化tokenizer
        model_name = "bert-base-chinese" if self.language == "chinese" else "bert-base-uncased"
        self.tokenizer = BertTokenizerWrapper(model_name)
        
        # 初始化损失函数
        self.criterion = nn.CrossEntropyLoss()
        
        print(f"BERT模型创建完成")
        return self.model
    
    def setup_optimizer(self, train_loader: DataLoader, epochs: int, 
                       warmup_ratio: float = 0.1) -> None:
        """
        设置优化器和学习率调度器
        参数：
            train_loader: 训练数据加载器
            epochs: 训练轮数
            warmup_ratio: 预热比例
        """
        # 计算总步数
        total_steps = len(train_loader) * epochs
        warmup_steps = int(total_steps * warmup_ratio)
        
        # 为不同层设置不同的学习率
        no_decay = ['bias', 'LayerNorm.weight']
        optimizer_grouped_parameters = [
            {
                'params': [p for n, p in self.model.named_parameters() 
                          if not any(nd in n for nd in no_decay)],
                'weight_decay': 0.01
            },
            {
                'params': [p for n, p in self.model.named_parameters() 
                          if any(nd in n for nd in no_decay)],
                'weight_decay': 0.0
            }
        ]
        
        # 使用AdamW优化器
        self.optimizer = optim.AdamW(
            optimizer_grouped_parameters,
            lr=Config.TRAINING_CONFIG['learning_rate'],
            eps=1e-8
        )
        
        # 学习率调度器
        self.scheduler = get_linear_schedule_with_warmup(
            self.optimizer,
            num_warmup_steps=warmup_steps,
            num_training_steps=total_steps
        )
        
        print(f"优化器设置完成，总步数: {total_steps}, 预热步数: {warmup_steps}")
    
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
            attention_mask = batch['attention_mask'].to(self.device)
            labels = batch['labels'].to(self.device)
            
            # 前向传播
            self.optimizer.zero_grad()
            outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
            loss = self.criterion(outputs, labels)
            
            # 反向传播
            loss.backward()
            
            # 梯度裁剪
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            
            self.optimizer.step()
            self.scheduler.step()
            
            # 统计
            total_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total_predictions += labels.size(0)
            correct_predictions += (predicted == labels).sum().item()
            
            # 记录学习率
            current_lr = self.scheduler.get_last_lr()[0]
            
            # 更新进度条
            current_acc = correct_predictions / total_predictions
            progress_bar.set_postfix({
                'Loss': f'{loss.item():.4f}',
                'Acc': f'{current_acc:.4f}',
                'LR': f'{current_lr:.2e}'
            })
        
        avg_loss = total_loss / len(train_loader)
        accuracy = correct_predictions / total_predictions
        
        # 记录学习率
        self.history['learning_rates'].append(self.scheduler.get_last_lr()[0])
        
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
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['labels'].to(self.device)
                
                outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
                loss = self.criterion(outputs, labels)
                
                total_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                total_predictions += labels.size(0)
                correct_predictions += (predicted == labels).sum().item()
        
        avg_loss = total_loss / len(val_loader)
        accuracy = correct_predictions / total_predictions
        
        return avg_loss, accuracy
    
    def train(self, train_loader: DataLoader, val_loader: DataLoader, 
              epochs: int = 3, save_best: bool = True) -> Dict[str, Any]:
        """
        完整训练流程
        参数：
            train_loader: 训练数据加载器
            val_loader: 验证数据加载器
            epochs: 训练轮数（BERT通常需要较少的轮数）
            save_best: 是否保存最佳模型
        返回值：训练结果字典
        """
        print(f"开始训练BERT模型，共{epochs}轮...")
        
        # 设置优化器和调度器
        self.setup_optimizer(train_loader, epochs)
        
        best_val_acc = 0.0
        best_model_state = None
        patience_counter = 0
        patience = Config.TRAINING_CONFIG.get('early_stopping_patience', 2)  # BERT早停更激进
        
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
            print(f"当前学习率: {self.scheduler.get_last_lr()[0]:.2e}")
            
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
            'model_type': 'bert',
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
        model_path = Config.get_model_path('bert', self.language)
        
        # 确保目录存在
        model_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 保存模型和相关信息
        checkpoint = {
            'model_state_dict': self.model.state_dict(),
            'model_config': Config.MODEL_CONFIGS['bert'],
            'language': self.language,
            'history': self.history,
            'tokenizer_name': "bert-base-chinese" if self.language == "chinese" else "bert-base-uncased"
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
        all_probabilities = []
        
        with torch.no_grad():
            for batch in tqdm(test_loader, desc="评估中"):
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['labels'].to(self.device)
                
                outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
                probabilities = torch.softmax(outputs, dim=1)
                _, predicted = torch.max(outputs.data, 1)
                
                all_predictions.extend(predicted.cpu().numpy())
                all_labels.extend(labels.cpu().numpy())
                all_probabilities.extend(probabilities.cpu().numpy())
        
        # 计算指标
        accuracy = accuracy_score(all_labels, all_predictions)
        report = classification_report(all_labels, all_predictions, output_dict=True)
        
        results = {
            'accuracy': accuracy,
            'classification_report': report,
            'total_samples': len(all_labels),
            'predictions': all_predictions,
            'probabilities': all_probabilities
        }
        
        print(f"测试准确率: {accuracy:.4f}")
        return results 