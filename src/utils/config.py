# -*- coding: utf-8 -*-
"""
项目配置管理模块
用途：统一管理项目中的各种配置参数，包括模型参数、路径配置、API配置等
"""

import os
from pathlib import Path

class Config:
    """
    项目配置类
    用途：集中管理项目的所有配置参数
    """
    
    # 项目根目录路径
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    
    # 数据相关配置
    DATASETS_DIR = PROJECT_ROOT / "datasets"  # 数据集存储目录
    MODELS_DIR = PROJECT_ROOT / "models"      # 模型存储目录
    LOGS_DIR = PROJECT_ROOT / "logs"          # 日志存储目录
    
    # 数据集配置
    DATASETS = {
        "chinese": "seamew/ChnSentiCorp",  # 中文情感数据集
        "english": "imdb"  # 英文电影评论数据集
    }
    
    # 模型配置
    MODEL_CONFIGS = {
        "textcnn": {
            "embedding_dim": 300,  # 词嵌入维度
            "num_filters": 100,    # 卷积核数量
            "filter_sizes": [3, 4, 5],  # 卷积核尺寸
            "dropout": 0.5,        # dropout概率
            "max_seq_length": 256  # 最大序列长度
        },
        "bilstm": {
            "embedding_dim": 300,  # 词嵌入维度
            "hidden_dim": 128,     # LSTM隐藏层维度
            "num_layers": 2,       # LSTM层数
            "dropout": 0.5,        # dropout概率
            "max_seq_length": 256  # 最大序列长度
        },
        "bert": {
            "model_name": "bert-base-chinese",  # BERT模型名称
            "max_seq_length": 512,  # 最大序列长度
            "learning_rate": 2e-5,  # 学习率
            "num_epochs": 3         # 训练轮数
        }
    }
    
    # 训练配置
    TRAINING_CONFIG = {
        "batch_size": 32,      # 批次大小
        "learning_rate": 1e-3, # 学习率
        "num_epochs": 10,      # 训练轮数
        "validation_split": 0.2,  # 验证集比例
        "early_stopping_patience": 3,  # 早停耐心值
        "save_best_model": True  # 是否保存最佳模型
    }
    
    # API配置
    API_CONFIG = {
        "host": "0.0.0.0",     # API服务器地址
        "port": 5000,          # API服务器端口
        "debug": True,         # 调试模式
        "cors_origins": ["http://localhost:5173"]  # 允许的跨域来源
    }
    
    # 日志配置
    LOGGING_CONFIG = {
        "level": "INFO",       # 日志级别
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # 日志格式
        "file_handler": True   # 是否写入文件
    }
    
    @classmethod
    def create_directories(cls):
        """
        创建必要的目录结构
        用途：确保项目运行所需的目录存在
        """
        directories = [cls.DATASETS_DIR, cls.MODELS_DIR, cls.LOGS_DIR]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_model_path(cls, model_name: str, language: str = "chinese") -> Path:
        """
        获取模型保存路径
        参数：
            model_name: 模型名称 (textcnn/bilstm/bert)
            language: 语言类型 (chinese/english)
        返回值：模型文件路径
        使用场景：保存和加载训练好的模型
        """
        return cls.MODELS_DIR / f"{model_name}_{language}.pth" 