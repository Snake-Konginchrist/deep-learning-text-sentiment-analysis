# -*- coding: utf-8 -*-
"""
深度学习文本情感分析系统快速启动脚本
用途：一键启动完整的情感分析系统演示
使用方法：python quick_start.py
"""

import sys
import os
import subprocess
import time
from pathlib import Path

def print_banner():
    """
    打印项目横幅
    """
    print("=" * 60)
    print("        深度学习文本情感分析系统")
    print("        基于TextCNN、BiLSTM和BERT的情感分类")
    print("=" * 60)

def check_dependencies():
    """
    检查项目依赖是否已安装
    """
    print("🔍 检查项目依赖...")
    
    required_packages = [
        "torch", "transformers", "datasets", "flask", 
        "jieba", "pandas", "numpy", "scikit-learn"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ 缺少依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    print("✅ 所有依赖包已安装")
    return True

def create_directories():
    """
    创建必要的目录结构
    """
    print("📁 创建项目目录...")
    
    directories = ["data", "models", "logs"]
    
    for dir_name in directories:
        dir_path = Path(dir_name)
        dir_path.mkdir(exist_ok=True)
        print(f"  ✓ {dir_name}/")
    
    print("✅ 目录结构创建完成")

def download_sample_data():
    """
    下载示例数据集
    """
    print("📥 下载示例数据集...")
    print("  注意：首次下载可能需要几分钟时间")
    
    try:
        # 下载少量中文数据用于演示
        result = subprocess.run([
            sys.executable, "-m", "src.scripts.download_data", "chinese", "--max-samples", "500"
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ 示例数据下载完成")
            return True
        else:
            print(f"❌ 数据下载失败: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ 数据下载超时，请检查网络连接")
        return False
    except Exception as e:
        print(f"❌ 数据下载出错: {str(e)}")
        return False

def train_demo_model():
    """
    训练演示模型
    """
    print("🚀 训练演示模型...")
    print("  这将训练一个小型TextCNN模型用于演示")
    
    try:
        result = subprocess.run([
            sys.executable, "scripts/demo_training.py"
        ], timeout=600)  # 10分钟超时
        
        if result.returncode == 0:
            print("✅ 演示模型训练完成")
            return True
        else:
            print("❌ 模型训练失败")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ 模型训练超时")
        return False
    except Exception as e:
        print(f"❌ 模型训练出错: {str(e)}")
        return False

def start_api_server():
    """
    启动API服务器
    """
    print("🌐 启动API服务器...")
    print("  服务器地址: http://localhost:5000")
    print("  按 Ctrl+C 停止服务器")
    print("-" * 40)
    
    try:
        # 启动Flask服务器
        subprocess.run([sys.executable, "run_server.py"])
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
    except Exception as e:
        print(f"❌ 启动服务器失败: {str(e)}")

def test_api():
    """
    测试API接口
    """
    print("🧪 测试API接口...")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "src.api.test_client"
        ], timeout=60)
        
        if result.returncode == 0:
            print("✅ API测试通过")
            return True
        else:
            print("❌ API测试失败")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ API测试超时")
        return False
    except Exception as e:
        print(f"❌ API测试出错: {str(e)}")
        return False

def show_usage_examples():
    """
    显示使用示例
    """
    print("\n📖 使用示例:")
    print("-" * 40)
    
    examples = [
        {
            "description": "启动API服务器",
            "command": "python run_server.py"
        },
        {
            "description": "下载完整数据集",
            "command": "python -m src.scripts.download_data both"
        },
        {
            "description": "训练演示模型",
            "command": "python scripts/demo_training.py"
        },
        {
            "description": "测试API接口",
            "command": "python -m src.api.test_client"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example['description']}")
        print(f"   {example['command']}")
        print()

def show_api_examples():
    """
    显示API使用示例
    """
    print("\n🔗 API使用示例:")
    print("-" * 40)
    
    api_examples = [
        {
            "name": "单文本分析",
            "method": "POST",
            "url": "http://localhost:5000/analyze",
            "body": '{"text": "这个电影真的很棒！"}'
        },
        {
            "name": "批量分析",
            "method": "POST", 
            "url": "http://localhost:5000/analyze/batch",
            "body": '{"texts": ["很好", "很差", "一般"]}'
        },
        {
            "name": "获取模型信息",
            "method": "GET",
            "url": "http://localhost:5000/models",
            "body": ""
        }
    ]
    
    for example in api_examples:
        print(f"• {example['name']}")
        print(f"  {example['method']} {example['url']}")
        if example['body']:
            print(f"  Body: {example['body']}")
        print()

def main():
    """
    主函数：执行快速启动流程
    """
    print_banner()
    
    print("\n🎯 快速启动选项:")
    print("1. 完整设置（下载数据 + 训练模型 + 启动服务器）")
    print("2. 仅启动服务器（需要已有模型）")
    print("3. 仅下载数据")
    print("4. 仅训练模型")
    print("5. 测试API")
    print("6. 显示使用说明")
    
    try:
        choice = input("\n请选择选项 (1-6): ").strip()
        
        if choice == "1":
            # 完整设置流程
            if not check_dependencies():
                return 1
            
            create_directories()
            
            if not download_sample_data():
                print("❌ 数据下载失败，无法继续")
                return 1
            
            if not train_demo_model():
                print("❌ 模型训练失败，无法继续")
                return 1
            
            print("\n🎉 设置完成！即将启动API服务器...")
            time.sleep(2)
            start_api_server()
            
        elif choice == "2":
            # 仅启动服务器
            if not check_dependencies():
                return 1
            create_directories()
            start_api_server()
            
        elif choice == "3":
            # 仅下载数据
            create_directories()
            download_sample_data()
            
        elif choice == "4":
            # 仅训练模型
            if not check_dependencies():
                return 1
            train_demo_model()
            
        elif choice == "5":
            # 测试API
            test_api()
            
        elif choice == "6":
            # 显示使用说明
            show_usage_examples()
            show_api_examples()
            
        else:
            print("❌ 无效选择，请输入1-6之间的数字")
            return 1
            
    except KeyboardInterrupt:
        print("\n🛑 操作被用户中断")
        return 1
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 