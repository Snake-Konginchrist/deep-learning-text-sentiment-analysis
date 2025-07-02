# -*- coding: utf-8 -*-
"""
训练相关API端点
用途：提供模型训练、数据下载等功能的RESTful接口
"""

from flask import Blueprint, request, jsonify
import threading
import time
from typing import Dict, Any
import traceback

from ..scripts.dataset_loader import DatasetLoader
from ..training.trainer import ModelTrainer
from ..utils.config import Config

# 创建蓝图
training_bp = Blueprint('training', __name__, url_prefix='/training')

# 全局变量存储训练状态
training_status = {
    "is_training": False,
    "current_task": None,
    "progress": 0,
    "message": "",
    "error": None,
    "results": None
}

# 数据下载状态
download_status = {
    "is_downloading": False,
    "language": None,
    "progress": 0,
    "message": "",
    "error": None,
    "completed": False
}

@training_bp.route('/datasets/download', methods=['POST'])
def download_dataset():
    """
    下载数据集端点
    请求体: {"language": "chinese/english/both", "max_samples": 可选}
    """
    global download_status
    
    try:
        data = request.get_json()
        if not data or "language" not in data:
            return jsonify({
                "status": "error",
                "message": "请求数据格式错误，需要包含'language'字段"
            }), 400
        
        language = data["language"]
        max_samples = data.get("max_samples", None)
        
        if language not in ["chinese", "english", "both"]:
            return jsonify({
                "status": "error",
                "message": "语言类型必须是 chinese、english 或 both"
            }), 400
        
        # 检查是否已经在下载
        if download_status["is_downloading"]:
            return jsonify({
                "status": "error",
                "message": "数据集下载正在进行中，请稍后再试"
            }), 409
        
        # 启动后台下载任务
        def download_task():
            global download_status
            try:
                download_status.update({
                    "is_downloading": True,
                    "language": language,
                    "progress": 0,
                    "message": "开始下载数据集...(支持Hugging Face + Kaggle多数据源)",
                    "error": None,
                    "completed": False
                })
                
                if language == "both":
                    # 下载中英文数据集
                    languages = ["chinese", "english"]
                    for i, lang in enumerate(languages):
                        download_status["message"] = f"正在下载{lang}数据集..."
                        download_status["progress"] = int((i / len(languages)) * 50)
                        
                        loader = DatasetLoader(language=lang)
                        train_data, val_data, test_data = loader.get_processed_data(max_samples)
                        
                        download_status["progress"] = int(((i + 1) / len(languages)) * 100)
                else:
                    # 下载单一语言数据集
                    download_status["message"] = f"正在下载{language}数据集..."
                    download_status["progress"] = 50
                    
                    loader = DatasetLoader(language=language)
                    train_data, val_data, test_data = loader.get_processed_data(max_samples)
                    
                    download_status["progress"] = 100
                
                download_status.update({
                    "is_downloading": False,
                    "message": "数据集下载完成",
                    "completed": True
                })
                
            except Exception as e:
                download_status.update({
                    "is_downloading": False,
                    "error": str(e),
                    "message": f"下载失败: {str(e)}"
                })
        
        # 在后台线程中启动下载
        thread = threading.Thread(target=download_task)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "status": "success",
            "message": "数据集下载已启动，请使用状态接口查看进度"
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"启动下载失败: {str(e)}"
        }), 500

@training_bp.route('/datasets/status', methods=['GET'])
def get_download_status():
    """
    获取数据下载状态
    """
    return jsonify({
        "status": "success",
        "data": download_status
    })

@training_bp.route('/models/train', methods=['POST'])
def train_model():
    """
    启动模型训练端点
    请求体: {
        "model_type": "textcnn/bilstm/bert",
        "language": "chinese/english",
        "epochs": 可选,
        "batch_size": 可选,
        "learning_rate": 可选
    }
    """
    global training_status
    
    try:
        data = request.get_json()
        if not data or "model_type" not in data:
            return jsonify({
                "status": "error",
                "message": "请求数据格式错误，需要包含'model_type'字段"
            }), 400
        
        model_type = data["model_type"]
        language = data.get("language", "chinese")
        epochs = data.get("epochs", Config.TRAINING_CONFIG["num_epochs"])
        batch_size = data.get("batch_size", Config.TRAINING_CONFIG["batch_size"])
        learning_rate = data.get("learning_rate", Config.TRAINING_CONFIG["learning_rate"])
        
        # 验证参数
        if model_type not in ["textcnn", "bilstm", "bert"]:
            return jsonify({
                "status": "error",
                "message": "模型类型必须是 textcnn、bilstm 或 bert"
            }), 400
        
        if language not in ["chinese", "english"]:
            return jsonify({
                "status": "error",
                "message": "语言类型必须是 chinese 或 english"
            }), 400
        
        # 检查是否已经在训练
        if training_status["is_training"]:
            return jsonify({
                "status": "error",
                "message": "模型训练正在进行中，请稍后再试"
            }), 409
        
        # 启动后台训练任务
        def training_task():
            global training_status
            try:
                training_status.update({
                    "is_training": True,
                    "current_task": f"训练{model_type}模型",
                    "progress": 0,
                    "message": "初始化训练器...",
                    "error": None,
                    "results": None
                })
                
                # 创建训练管理器，带进度回调
                def progress_callback(progress: int, message: str):
                    training_status["progress"] = progress
                    training_status["message"] = message
                
                from ..training.trainer_manager import TrainerManager
                trainer_manager = TrainerManager(
                    model_type=model_type, 
                    language=language, 
                    progress_callback=progress_callback
                )
                
                # 执行完整的训练流水线
                results = trainer_manager.full_training_pipeline(
                    epochs=epochs,
                    learning_rate=learning_rate,
                    max_samples=1000  # 为了快速测试，限制样本数量
                )
                
                # 训练完成
                training_status.update({
                    "is_training": False,
                    "progress": 100,
                    "message": "训练完成",
                    "results": {
                        "model_type": results['model_type'],
                        "language": results['language'],
                        "epochs": results['epochs'],
                        "best_val_accuracy": results['best_val_accuracy'],
                        "final_train_accuracy": results['final_train_accuracy'],
                        "final_val_accuracy": results['final_val_accuracy'],
                        "test_accuracy": results['test_results']['accuracy'],
                        "model_path": results['model_path'],
                        "early_stopped": results.get('early_stopped', False)
                    }
                })
                
                print(f"✅ {model_type}模型训练完成!")
                print(f"📊 最佳验证准确率: {results['best_val_accuracy']:.4f}")
                print(f"📊 测试准确率: {results['test_results']['accuracy']:.4f}")
                print(f"💾 模型保存路径: {results['model_path']}")
                
            except Exception as e:
                import traceback
                error_detail = traceback.format_exc()
                print(f"❌ 训练失败: {str(e)}")
                print(f"详细错误: {error_detail}")
                
                training_status.update({
                    "is_training": False,
                    "error": str(e),
                    "message": f"训练失败: {str(e)}"
                })
        
        # 在后台线程中启动训练
        thread = threading.Thread(target=training_task)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "status": "success",
            "message": "模型训练已启动，请使用状态接口查看进度"
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"启动训练失败: {str(e)}"
        }), 500

@training_bp.route('/models/status', methods=['GET'])
def get_training_status():
    """
    获取训练状态
    """
    return jsonify({
        "status": "success",
        "data": training_status
    })

@training_bp.route('/models/list', methods=['GET'])
def list_trained_models():
    """
    列出已训练的模型
    """
    try:
        models = []
        models_dir = Config.MODELS_DIR
        
        if models_dir.exists():
            for model_file in models_dir.glob("*.pth"):
                # 解析模型文件名
                filename = model_file.stem
                parts = filename.split("_")
                if len(parts) >= 2:
                    model_type = parts[0]
                    language = parts[1]
                    
                    models.append({
                        "model_type": model_type,
                        "language": language,
                        "filename": model_file.name,
                        "size": model_file.stat().st_size,
                        "created_time": model_file.stat().st_ctime
                    })
        
        return jsonify({
            "status": "success",
            "data": {
                "models": models,
                "total_count": len(models)
            }
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"获取模型列表失败: {str(e)}"
        }), 500

@training_bp.route('/datasets/info', methods=['GET'])
def get_datasets_info():
    """
    获取数据集信息
    """
    try:
        # 检查数据集是否已下载
        def check_dataset_downloaded(language):
            """检查指定语言的数据集是否已下载"""
            datasets_dir = Config.DATASETS_DIR
            if not datasets_dir.exists():
                return False
            
            dataset_name = Config.DATASETS[language]
            
            # 根据不同数据集检查特定文件夹
            if language == "chinese":
                # 中文数据集：检查是否有 seamew 或 ChnSentiCorp 相关文件夹
                seamew_dirs = list(datasets_dir.glob("**/seamew*")) + list(datasets_dir.glob("**/ChnSentiCorp*"))
                return len(seamew_dirs) > 0
            elif language == "english":
                # 英文数据集：检查是否有 imdb 相关文件夹
                imdb_dirs = list(datasets_dir.glob("**/imdb*")) + list(datasets_dir.glob("**/IMDb*"))
                return len(imdb_dirs) > 0
            
            return False
        
        info = {
            "available_datasets": [
                {
                    "language": "chinese",
                    "name": "ChnSentiCorp",
                    "description": "中文情感分析数据集，包含酒店、书籍、餐饮评论",
                    "size": "约12,000条",
                    "source": "Hugging Face",
                    "downloaded": check_dataset_downloaded("chinese")
                },
                {
                    "language": "english", 
                    "name": "IMDb Movie Reviews",
                    "description": "英文电影评论情感分析数据集",
                    "size": "50,000条",
                    "source": "Hugging Face",
                    "downloaded": check_dataset_downloaded("english")
                }
            ],
            "supported_languages": ["chinese", "english"],
            "data_directory": str(Config.DATASETS_DIR)
        }
        
        return jsonify({
            "status": "success",
            "data": info
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"获取数据集信息失败: {str(e)}"
        }), 500 