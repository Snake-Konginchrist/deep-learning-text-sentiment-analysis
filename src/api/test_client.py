# -*- coding: utf-8 -*-
"""
API测试客户端
用途：测试情感分析API的各个端点功能
使用方法：python -m src.api.test_client
"""

import requests
import json
import sys
from pathlib import Path

# API服务器配置
API_BASE_URL = "http://localhost:5000"

def test_health_check():
    """
    测试健康检查端点
    返回值：True表示服务器正常，False表示异常
    使用场景：确认API服务器是否正常运行
    """
    print("测试健康检查端点...")
    try:
        response = requests.get(f"{API_BASE_URL}/")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
            return True
        else:
            print(f"请求失败: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"连接错误: {str(e)}")
        return False

def test_single_analysis():
    """
    测试单文本情感分析端点
    使用场景：验证单个文本的情感分析功能
    """
    print("\n测试单文本情感分析...")
    
    # 测试用例
    test_cases = [
        "这个电影真的很棒，我非常喜欢！",
        "服务态度太差了，完全不推荐。",
        "今天天气不错，心情很好。",
        "这个产品质量一般，价格有点贵。"
    ]
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n测试案例 {i}: {text}")
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/analyze",
                json={"text": text},
                headers={"Content-Type": "application/json"}
            )
            
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data["status"] == "success":
                    result = data["data"]
                    print(f"情感: {result['sentiment']}")
                    print(f"置信度: {result['confidence']}")
                    if "probabilities" in result:
                        print(f"概率分布: {result['probabilities']}")
                else:
                    print(f"分析失败: {data['message']}")
            else:
                print(f"请求失败: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"请求错误: {str(e)}")

def test_batch_analysis():
    """
    测试批量文本分析端点
    使用场景：验证多个文本的批量处理功能
    """
    print("\n测试批量文本分析...")
    
    # 批量测试用例
    test_texts = [
        "这个餐厅的菜品很美味，环境也很好。",
        "价格太贵了，性价比不高。",
        "服务员态度很友好，值得推荐。",
        "等了很久才上菜，体验不好。"
    ]
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/analyze/batch",
            json={"texts": test_texts},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "success":
                batch_data = data["data"]
                print(f"总数量: {batch_data['total_count']}")
                
                for i, result in enumerate(batch_data["results"], 1):
                    print(f"\n结果 {i}:")
                    print(f"  文本: {result['text']}")
                    print(f"  情感: {result['sentiment']}")
                    print(f"  置信度: {result['confidence']}")
            else:
                print(f"批量分析失败: {data['message']}")
        else:
            print(f"请求失败: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {str(e)}")

def test_models_info():
    """
    测试获取模型信息端点
    使用场景：验证模型信息查询功能
    """
    print("\n测试获取模型信息...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/models")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "success":
                models_info = data["data"]
                print("模型信息:")
                print(f"当前模型: {models_info['current_model']}")
                print(f"可用模型数量: {len(models_info['available_models'])}")
                print(f"支持语言: {[lang['name'] for lang in models_info['supported_languages']]}")
            else:
                print(f"获取模型信息失败: {data['message']}")
        else:
            print(f"请求失败: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {str(e)}")

def test_training_endpoints():
    """
    测试训练相关端点
    使用场景：验证模型训练和数据下载功能
    """
    print("\n测试训练相关端点...")
    
    # 测试获取数据集信息
    print("1. 测试获取数据集信息:")
    try:
        response = requests.get(f"{API_BASE_URL}/training/datasets/info")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"数据集信息: {json.dumps(data, ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"错误: {str(e)}")
    
    # 测试获取训练状态
    print("\n2. 测试获取训练状态:")
    try:
        response = requests.get(f"{API_BASE_URL}/training/models/status")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"训练状态: {json.dumps(data, ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"错误: {str(e)}")
    
    # 测试获取已训练模型列表
    print("\n3. 测试获取已训练模型列表:")
    try:
        response = requests.get(f"{API_BASE_URL}/training/models/list")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"模型列表: {json.dumps(data, ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"错误: {str(e)}")

def test_error_cases():
    """
    测试错误处理
    使用场景：验证API的错误处理和边界情况
    """
    print("\n测试错误处理...")
    
    # 测试空文本
    print("1. 测试空文本:")
    try:
        response = requests.post(
            f"{API_BASE_URL}/analyze",
            json={"text": ""},
            headers={"Content-Type": "application/json"}
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()['message']}")
    except Exception as e:
        print(f"错误: {str(e)}")
    
    # 测试无效JSON
    print("\n2. 测试无效请求格式:")
    try:
        response = requests.post(
            f"{API_BASE_URL}/analyze",
            json={"invalid_field": "test"},
            headers={"Content-Type": "application/json"}
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()['message']}")
    except Exception as e:
        print(f"错误: {str(e)}")
    
    # 测试不存在的端点
    print("\n3. 测试不存在的端点:")
    try:
        response = requests.get(f"{API_BASE_URL}/nonexistent")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()['message']}")
    except Exception as e:
        print(f"错误: {str(e)}")

def main():
    """
    主函数：执行所有API测试
    使用场景：作为测试套件的入口点，全面验证API功能
    """
    print("=" * 50)
    print("情感分析API测试工具")
    print("=" * 50)
    print(f"API服务器: {API_BASE_URL}")
    
    # 检查API服务器是否运行
    if not test_health_check():
        print("\n❌ API服务器未运行或无法访问")
        print("请先启动API服务器: python run_server.py")
        return 1
    
    print("\n✅ API服务器连接成功")
    
    # 执行各项测试
    try:
        test_single_analysis()
        test_batch_analysis()
        test_models_info()
        test_training_endpoints()
        test_error_cases()
        
        print("\n" + "=" * 50)
        print("✅ 所有API测试完成！")
        
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        return 1
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 