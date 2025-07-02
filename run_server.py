# -*- coding: utf-8 -*-
"""
情感分析API服务器启动脚本
用途：启动Flask API服务，为前端Vue应用提供情感分析接口
使用方法：python run_server.py
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入API应用
from src.api.app import create_app
from src.utils.config import Config

def main():
    """
    主函数：启动Flask开发服务器
    """
    print("=" * 50)
    print("深度学习文本情感分析API服务")
    print("=" * 50)
    
    try:
        # 创建Flask应用
        app = create_app()
        
        # 获取配置
        config = Config.API_CONFIG
        
        print(f"服务器配置:")
        print(f"  地址: {config['host']}")
        print(f"  端口: {config['port']}")
        print(f"  调试模式: {config['debug']}")
        print(f"  允许跨域: {config['cors_origins']}")
        print()
        print(f"API文档:")
        print(f"  健康检查: GET  http://{config['host']}:{config['port']}/")
        print(f"  单文本分析: POST http://{config['host']}:{config['port']}/analyze")
        print(f"  批量分析: POST http://{config['host']}:{config['port']}/analyze/batch")
        print(f"  模型信息: GET  http://{config['host']}:{config['port']}/models")
        print()
        print("按 Ctrl+C 停止服务器")
        print("=" * 50)
        
        # 启动服务器
        app.run(
            host=config["host"],
            port=config["port"],
            debug=config["debug"],
            threaded=True  # 支持多线程处理请求
        )
        
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        print(f"启动服务器失败: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 