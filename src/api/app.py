# -*- coding: utf-8 -*-
"""
Flask API应用主文件
用途：提供情感分析的RESTful API服务，对接前端Vue应用
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from typing import Dict, Any
import traceback
import os

from ..utils.config import Config
from ..services.sentiment_analyzer import SentimentAnalyzer
from .training_api import training_bp
import glob
from pathlib import Path

# 创建Flask应用实例
app = Flask(__name__)

# 配置CORS跨域支持（允许前端访问）
CORS(app, origins=Config.API_CONFIG["cors_origins"])

# 注册训练相关的蓝图
app.register_blueprint(training_bp)

# 全局情感分析器实例
analyzer = None

def init_analyzer() -> None:
    """
    初始化情感分析器
    用途：在应用启动时加载默认模型
    """
    global analyzer
    try:
        print("初始化情感分析器...")
        # 使用BERT模型和中文语言作为默认配置
        analyzer = SentimentAnalyzer(model_type="bert", language="chinese")
        
        # 如果存在预训练模型，则加载
        model_path = Config.get_model_path("bert", "chinese")
        if os.path.exists(model_path):
            analyzer.load_model(str(model_path))
            print("已加载默认预训练模型: bert_chinese")
        else:
            print("未找到默认模型，尝试查找其他可用模型...")
            
            # 查找所有可用的模型文件
            models_dir = Config.MODELS_DIR
            model_files = list(models_dir.glob("*.pth"))
            
            if model_files:
                # 尝试加载第一个找到的模型
                first_model = model_files[0]
                filename = first_model.name
                
                # 尝试从文件名解析模型类型和语言
                name_parts = filename.replace('.pth', '').split('_')
                if len(name_parts) >= 2:
                    model_type = name_parts[0]
                    language = name_parts[1]
                    
                    # 重新创建分析器
                    analyzer = SentimentAnalyzer(model_type=model_type, language=language)
                    analyzer.load_model(str(first_model))
                    print(f"已自动加载模型: {filename}")
                else:
                    print("无法解析模型文件名，未加载任何模型")
            else:
                print("未找到任何训练好的模型文件")
            
    except Exception as e:
        print(f"初始化分析器失败: {str(e)}")
        analyzer = None

@app.route("/", methods=["GET"])
def health_check() -> Dict[str, Any]:
    """
    健康检查端点
    返回值：API状态信息
    使用场景：检查API服务是否正常运行
    """
    model_info = {}
    if analyzer is not None:
        model_info = {
            "analyzer_ready": True,
            "model_loaded": analyzer.model is not None,
            "model_type": analyzer.model_type,
            "language": analyzer.language
        }
    else:
        model_info = {
            "analyzer_ready": False,
            "model_loaded": False,
            "model_type": None,
            "language": None
        }
    
    return jsonify({
        "status": "success",
        "message": "情感分析API服务正常运行",
        "data": model_info,
        "endpoints": [
            "/analyze - POST: 分析单个文本",
            "/analyze/batch - POST: 批量分析文本",
            "/models - GET: 获取可用模型信息",
            "/models/load - POST: 加载指定模型",
            "/models/current - GET: 获取当前模型状态"
        ]
    })

@app.route("/analyze", methods=["POST"])
def analyze_sentiment() -> Dict[str, Any]:
    """
    单文本情感分析端点
    请求体: {"text": "待分析的文本", "model": "可选的模型类型", "language": "可选的语言类型"}
    返回值：情感分析结果
    使用场景：前端提交单条文本进行情感分析
    """
    try:
        # 获取请求数据
        data = request.get_json()
        
        if not data or "text" not in data:
            return jsonify({
                "status": "error",
                "message": "请求数据格式错误，需要包含'text'字段"
            }), 400
        
        text = data["text"].strip()
        if not text:
            return jsonify({
                "status": "error", 
                "message": "文本内容不能为空"
            }), 400
        
        # 检查分析器是否已初始化
        if analyzer is None:
            return jsonify({
                "status": "error",
                "message": "分析器未初始化，请稍后重试"
            }), 503
        
        # 执行情感分析
        result = analyzer.predict_single(text, return_proba=True)
        
        return jsonify({
            "status": "success",
            "data": result
        })
        
    except Exception as e:
        print(f"分析过程中出错: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            "status": "error",
            "message": f"分析失败: {str(e)}"
        }), 500

@app.route("/analyze/batch", methods=["POST"])
def analyze_batch() -> Dict[str, Any]:
    """
    批量文本情感分析端点
    请求体: {"texts": ["文本1", "文本2", ...], "batch_size": 可选的批处理大小}
    返回值：批量分析结果
    使用场景：前端提交多条文本进行批量分析
    """
    try:
        # 获取请求数据
        data = request.get_json()
        
        if not data or "texts" not in data:
            return jsonify({
                "status": "error",
                "message": "请求数据格式错误，需要包含'texts'字段"
            }), 400
        
        texts = data["texts"]
        if not isinstance(texts, list) or len(texts) == 0:
            return jsonify({
                "status": "error",
                "message": "texts必须是非空列表"
            }), 400
        
        # 限制批次大小防止内存溢出
        max_batch_size = 100
        if len(texts) > max_batch_size:
            return jsonify({
                "status": "error",
                "message": f"批次大小超过限制，最大支持{max_batch_size}条文本"
            }), 400
        
        # 检查分析器是否已初始化
        if analyzer is None:
            return jsonify({
                "status": "error",
                "message": "分析器未初始化，请稍后重试"
            }), 503
        
        # 获取批处理大小
        batch_size = data.get("batch_size", 32)
        batch_size = min(batch_size, 32)  # 限制最大批处理大小
        
        # 执行批量分析
        results = analyzer.predict_batch(texts, batch_size=batch_size)
        
        return jsonify({
            "status": "success",
            "data": {
                "total_count": len(texts),
                "results": results
            }
        })
        
    except Exception as e:
        print(f"批量分析过程中出错: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            "status": "error",
            "message": f"批量分析失败: {str(e)}"
        }), 500

@app.route("/models", methods=["GET"])
def get_models_info() -> Dict[str, Any]:
    """
    获取可用模型信息端点
    返回值：模型配置和状态信息
    使用场景：前端获取支持的模型类型和配置
    """
    try:
        models_info = {
            "current_model": {
                "type": analyzer.model_type if analyzer else None,
                "language": analyzer.language if analyzer else None,
                "status": "loaded" if analyzer and analyzer.model else "not_loaded"
            },
            "available_models": [
                {
                    "type": "textcnn",
                    "name": "TextCNN",
                    "description": "基于卷积神经网络的文本分类模型",
                    "languages": ["chinese", "english"]
                },
                {
                    "type": "bilstm", 
                    "name": "BiLSTM",
                    "description": "基于双向长短期记忆网络的文本分类模型",
                    "languages": ["chinese", "english"]
                },
                {
                    "type": "bert",
                    "name": "BERT",
                    "description": "基于Transformer的预训练语言模型",
                    "languages": ["chinese", "english"]
                }
            ],
            "supported_languages": [
                {
                    "code": "chinese",
                    "name": "中文",
                    "dataset": "ChnSentiCorp"
                },
                {
                    "code": "english", 
                    "name": "English",
                    "dataset": "IMDb"
                }
            ]
        }
        
        return jsonify({
            "status": "success",
            "data": models_info
        })
        
    except Exception as e:
        print(f"获取模型信息时出错: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"获取模型信息失败: {str(e)}"
        }), 500

@app.route("/models/trained", methods=["GET"])
def get_trained_models() -> Dict[str, Any]:
    """
    获取已训练模型列表端点
    返回值：已训练的模型文件信息
    使用场景：前端获取可用的已训练模型
    """
    try:
        models_dir = Config.MODELS_DIR
        models = []
        
        # 查找所有.pth模型文件
        for model_file in models_dir.glob("*.pth"):
            try:
                # 解析模型文件名获取信息
                filename = model_file.name
                stat = model_file.stat()
                
                # 尝试从文件名解析模型类型和语言
                # 文件名格式：{model_type}_{language}.pth
                name_parts = filename.replace('.pth', '').split('_')
                if len(name_parts) >= 2:
                    model_type = name_parts[0]
                    language = name_parts[1]
                else:
                    # 如果无法解析，使用默认值
                    model_type = "unknown"
                    language = "unknown"
                
                model_info = {
                    "filename": filename,
                    "model_type": model_type,
                    "language": language,
                    "size": stat.st_size,
                    "created_time": stat.st_mtime,
                    "path": str(model_file)
                }
                
                models.append(model_info)
                
            except Exception as e:
                print(f"解析模型文件 {model_file} 失败: {str(e)}")
                continue
        
        # 按创建时间排序（最新的在前）
        models.sort(key=lambda x: x["created_time"], reverse=True)
        
        return jsonify({
            "status": "success",
            "data": {
                "models": models,
                "total_count": len(models)
            }
        })
        
    except Exception as e:
        print(f"获取已训练模型列表失败: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"获取已训练模型列表失败: {str(e)}"
        }), 500

@app.route("/models/load", methods=["POST"])
def load_model() -> Dict[str, Any]:
    """
    加载指定模型端点
    请求体: {"model_type": "模型类型", "language": "语言", "model_path": "可选的模型路径"}
    返回值：加载结果
    使用场景：前端选择并加载特定的模型进行情感分析
    """
    global analyzer
    try:
        # 获取请求数据
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "请求数据不能为空"
            }), 400
        
        model_type = data.get("model_type", "bert")
        language = data.get("language", "chinese")
        model_path = data.get("model_path")
        
        # 验证模型类型和语言
        valid_models = ["textcnn", "bilstm", "bert"]
        valid_languages = ["chinese", "english"]
        
        if model_type not in valid_models:
            return jsonify({
                "status": "error",
                "message": f"不支持的模型类型: {model_type}，支持的类型: {', '.join(valid_models)}"
            }), 400
        
        if language not in valid_languages:
            return jsonify({
                "status": "error",
                "message": f"不支持的语言: {language}，支持的语言: {', '.join(valid_languages)}"
            }), 400
        
        # 创建新的分析器实例
        print(f"正在加载模型: {model_type}_{language}")
        analyzer = SentimentAnalyzer(model_type=model_type, language=language)
        
        # 确定模型路径
        if not model_path:
            model_path = Config.get_model_path(model_type, language)
        
        if not os.path.exists(model_path):
            return jsonify({
                "status": "error",
                "message": f"模型文件不存在: {model_path}"
            }), 404
        
        # 加载模型
        analyzer.load_model(str(model_path))
        
        return jsonify({
            "status": "success",
            "message": f"成功加载模型: {model_type}_{language}",
            "data": {
                "model_type": model_type,
                "language": language,
                "model_path": str(model_path),
                "model_loaded": analyzer.model is not None
            }
        })
        
    except FileNotFoundError as e:
        return jsonify({
            "status": "error",
            "message": f"模型文件未找到: {str(e)}"
        }), 404
    except Exception as e:
        print(f"加载模型时出错: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            "status": "error",
            "message": f"加载模型失败: {str(e)}"
        }), 500

@app.route("/models/current", methods=["GET"])
def get_current_model() -> Dict[str, Any]:
    """
    获取当前加载的模型信息端点
    返回值：当前模型状态
    使用场景：前端查询当前使用的模型
    """
    try:
        if analyzer is None:
            return jsonify({
                "status": "success",
                "data": {
                    "model_loaded": False,
                    "message": "未加载任何模型"
                }
            })
        
        return jsonify({
            "status": "success",
            "data": {
                "model_loaded": analyzer.model is not None,
                "model_type": analyzer.model_type,
                "language": analyzer.language,
                "message": "模型已加载" if analyzer.model else "分析器已初始化，但未加载模型"
            }
        })
        
    except Exception as e:
        print(f"获取当前模型信息时出错: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"获取模型信息失败: {str(e)}"
        }), 500

@app.errorhandler(404)
def not_found(error) -> Dict[str, Any]:
    """
    404错误处理器
    """
    return jsonify({
        "status": "error",
        "message": "API端点不存在"
    }), 404

@app.errorhandler(500)
def internal_error(error) -> Dict[str, Any]:
    """
    500错误处理器
    """
    return jsonify({
        "status": "error",
        "message": "服务器内部错误"
    }), 500

def create_app() -> Flask:
    """
    应用工厂函数
    返回值：配置好的Flask应用实例
    使用场景：创建和配置Flask应用
    """
    # 确保必要目录存在
    Config.create_directories()
    
    # 初始化分析器
    init_analyzer()
    
    return app

if __name__ == "__main__":
    # 开发环境下直接运行
    app = create_app()
    config = Config.API_CONFIG
    
    print(f"启动情感分析API服务...")
    print(f"服务地址: http://{config['host']}:{config['port']}")
    print(f"调试模式: {config['debug']}")
    
    app.run(
        host=config["host"],
        port=config["port"], 
        debug=config["debug"]
    ) 