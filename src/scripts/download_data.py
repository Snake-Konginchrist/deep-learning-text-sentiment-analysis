# -*- coding: utf-8 -*-
"""
数据集下载命令行工具
用途：下载和预处理情感分析数据集（ChnSentiCorp和IMDb）
使用方法：python -m src.scripts.download_data [language]
"""

import sys
import argparse
from pathlib import Path

from .dataset_loader import DatasetLoader
from ..utils.config import Config

def download_dataset(language: str = "chinese", max_samples: int = None) -> None:
    """
    下载指定语言的数据集
    参数：
        language: 语言类型 ("chinese" 或 "english")
        max_samples: 最大样本数量，用于快速测试
    使用场景：命令行下载和预处理数据集
    """
    print(f"开始下载 {language} 数据集...")
    
    try:
        # 创建数据加载器
        loader = DatasetLoader(language=language)
        
        # 下载和预处理数据
        train_data, val_data, test_data = loader.get_processed_data(max_samples=max_samples)
        
        print(f"\n数据集下载和处理完成！")
        print(f"训练集: {len(train_data)} 条")
        print(f"验证集: {len(val_data)} 条")
        print(f"测试集: {len(test_data)} 条")
        
        # 保存数据统计信息
        save_stats(language, train_data, val_data, test_data)
        
    except Exception as e:
        print(f"下载数据集失败: {str(e)}")
        raise

def save_stats(language: str, train_data, val_data, test_data) -> None:
    """
    保存数据集统计信息
    参数：
        language: 语言类型
        train_data, val_data, test_data: 数据集
    使用场景：生成数据集统计报告
    """
    try:
        stats = {
            "language": language,
            "train_size": len(train_data),
            "val_size": len(val_data),
            "test_size": len(test_data),
            "total_size": len(train_data) + len(val_data) + len(test_data)
        }
        
        # 计算标签分布
        train_labels = train_data["label"]
        stats["train_label_distribution"] = {
            "positive": sum(train_labels),
            "negative": len(train_labels) - sum(train_labels)
        }
        
        print(f"\n数据集统计信息:")
        print(f"语言: {stats['language']}")
        print(f"总计: {stats['total_size']} 条")
        print(f"正面样本: {stats['train_label_distribution']['positive']} 条")
        print(f"负面样本: {stats['train_label_distribution']['negative']} 条")
        
    except Exception as e:
        print(f"保存统计信息时出错: {str(e)}")

def main():
    """
    主函数：解析命令行参数并下载数据集
    使用场景：作为命令行工具的入口点
    """
    parser = argparse.ArgumentParser(description="下载情感分析数据集")
    parser.add_argument(
        "language", 
        nargs="?", 
        default="chinese",
        choices=["chinese", "english", "both"],
        help="要下载的数据集语言 (chinese/english/both，默认: chinese)"
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=None,
        help="限制样本数量（用于快速测试）"
    )
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("情感分析数据集下载工具")
    print("=" * 50)
    
    # 确保数据目录存在
    Config.create_directories()
    
    try:
        if args.language == "both":
            # 下载中英文数据集
            download_dataset("chinese", args.max_samples)
            print("\n" + "-" * 30)
            download_dataset("english", args.max_samples)
        else:
            # 下载指定语言数据集
            download_dataset(args.language, args.max_samples)
        
        print("\n" + "=" * 50)
        print("所有数据集下载完成！")
        
    except KeyboardInterrupt:
        print("\n下载被用户中断")
        return 1
    except Exception as e:
        print(f"\n下载过程中出现错误: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 