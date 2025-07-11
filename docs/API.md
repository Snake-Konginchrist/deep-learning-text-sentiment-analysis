# API 接口文档

## 📋 概述

本系统提供基于 Flask 的 RESTful API 服务，支持情感分析、模型训练、数据集管理等功能。

### 基础信息

- **基础URL**: `http://localhost:5000`
- **内容类型**: `application/json`
- **字符编码**: `UTF-8`

### 响应格式

所有 API 响应都遵循统一的格式：

```json
{
  "status": "success|error",
  "message": "响应消息",
  "data": {
    // 具体数据
  }
}
```

## 🔍 健康检查

### 获取服务状态

```http
GET /
```

**响应示例**:
```json
{
  "status": "success",
  "message": "情感分析API服务运行正常",
  "data": {
    "service": "sentiment-analysis-api",
    "version": "1.0.0",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

## 📊 情感分析接口

### 单文本情感分析

```http
POST /analyze
Content-Type: application/json

{
  "text": "这个电影真的很棒！"
}
```

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| text | string | 是 | 待分析的文本内容 |

**响应示例**:
```json
{
  "status": "success",
  "data": {
    "text": "这个电影真的很棒！",
    "sentiment": "正面",
    "confidence": 0.9234,
    "predicted_class": 1,
    "probabilities": {
      "负面": 0.0766,
      "正面": 0.9234
    }
  }
}
```

### 批量文本分析

```http
POST /analyze/batch
Content-Type: application/json

{
  "texts": ["文本1", "文本2", "文本3"],
  "batch_size": 32
}
```

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| texts | array | 是 | 待分析的文本数组 |
| batch_size | integer | 否 | 批处理大小，默认32 |

**响应示例**:
```json
{
  "status": "success",
  "data": {
    "results": [
      {
        "text": "文本1",
        "sentiment": "正面",
        "confidence": 0.85,
        "predicted_class": 1
      },
      {
        "text": "文本2",
        "sentiment": "负面",
        "confidence": 0.78,
        "predicted_class": 0
      }
    ],
    "total_count": 2,
    "processing_time": 0.15
  }
}
```

## 🤖 模型管理接口

### 获取模型信息

```http
GET /models
```

**响应示例**:
```json
{
  "status": "success",
  "data": {
    "current_model": {
      "type": "bert",
      "language": "chinese",
      "status": "loaded"
    },
    "available_models": [
      {
        "type": "textcnn",
        "name": "TextCNN",
        "description": "基于卷积神经网络的文本分类模型",
        "languages": ["chinese", "english"]
      }
    ],
    "supported_languages": [
      {
        "code": "chinese",
        "name": "中文",
        "dataset": "ChnSentiCorp"
      }
    ]
  }
}
```

### 获取已训练模型列表

```http
GET /models/trained
```

**响应示例**:
```json
{
  "status": "success",
  "data": {
    "models": [
      {
        "filename": "bert_chinese.pth",
        "model_type": "bert",
        "language": "chinese",
        "size": 438912000,
        "created_time": 1704067200,
        "path": "/path/to/models/bert_chinese.pth"
      }
    ],
    "total_count": 1
  }
}
```

### 加载指定模型

```http
POST /models/load
Content-Type: application/json

{
  "model_type": "bert",
  "language": "chinese",
  "model_path": "/optional/path/to/model.pth"
}
```

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| model_type | string | 是 | 模型类型 (textcnn/bilstm/bert) |
| language | string | 是 | 语言类型 (chinese/english) |
| model_path | string | 否 | 自定义模型路径 |

**响应示例**:
```json
{
  "status": "success",
  "message": "成功加载模型: bert_chinese",
  "data": {
    "model_type": "bert",
    "language": "chinese",
    "model_path": "/path/to/models/bert_chinese.pth",
    "model_loaded": true
  }
}
```

### 获取当前模型信息

```http
GET /models/current
```

**响应示例**:
```json
{
  "status": "success",
  "data": {
    "model_loaded": true,
    "model_type": "bert",
    "language": "chinese",
    "message": "模型已加载"
  }
}
```

### 删除指定模型

```http
DELETE /models/delete
Content-Type: application/json

{
  "filename": "bert_chinese.pth"
}
```

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| filename | string | 是 | 模型文件名 |

**响应示例**:
```json
{
  "status": "success",
  "message": "成功删除模型: bert_chinese.pth",
  "data": {
    "deleted_file": "bert_chinese.pth",
    "file_size": 438912000
  }
}
```

## 🎯 模型训练接口

### 启动模型训练

```http
POST /training/models/train
Content-Type: application/json

{
  "model_type": "bert",
  "language": "chinese",
  "epochs": 10,
  "batch_size": 32,
  "learning_rate": 0.001
}
```

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| model_type | string | 是 | 模型类型 (textcnn/bilstm/bert) |
| language | string | 是 | 语言类型 (chinese/english) |
| epochs | integer | 否 | 训练轮数，默认10 |
| batch_size | integer | 否 | 批次大小，默认32 |
| learning_rate | float | 否 | 学习率，默认0.001 |

**响应示例**:
```json
{
  "status": "success",
  "message": "训练任务已启动",
  "data": {
    "task_id": "train_bert_chinese_20240101_120000",
    "model_type": "bert",
    "language": "chinese",
    "status": "started"
  }
}
```

### 获取训练状态

```http
GET /training/status
```

**响应示例**:
```json
{
  "status": "success",
  "data": {
    "is_training": true,
    "current_task": "训练bert模型",
    "progress": 45,
    "message": "正在训练第5轮...",
    "error": null,
    "results": null
  }
}
```

### 获取已训练模型列表

```http
GET /training/models/list
```

**响应示例**:
```json
{
  "status": "success",
  "data": {
    "models": [
      {
        "model_type": "bert",
        "language": "chinese",
        "filename": "bert_chinese.pth",
        "size": 438912000,
        "created_time": 1704067200
      }
    ],
    "total_count": 1
  }
}
```

## 📊 数据集管理接口

### 获取数据集信息

```http
GET /datasets
```

**响应示例**:
```json
{
  "status": "success",
  "data": {
    "datasets": [
      {
        "name": "ChnSentiCorp",
        "language": "chinese",
        "description": "中文情感分析数据集",
        "size": "12MB",
        "samples": 12000,
        "status": "downloaded"
      }
    ]
  }
}
```

### 下载数据集

```http
POST /datasets/download
Content-Type: application/json

{
  "language": "chinese"
}
```

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| language | string | 是 | 语言类型 (chinese/english) |

**响应示例**:
```json
{
  "status": "success",
  "message": "数据集下载已启动",
  "data": {
    "language": "chinese",
    "status": "downloading",
    "progress": 0
  }
}
```

### 获取下载状态

```http
GET /datasets/status
```

**响应示例**:
```json
{
  "status": "success",
  "data": {
    "is_downloading": true,
    "current_task": "下载中文数据集",
    "progress": 65,
    "message": "正在下载数据文件...",
    "error": null
  }
}
```

## ⚠️ 错误处理

### 错误响应格式

```json
{
  "status": "error",
  "message": "错误描述信息",
  "error_code": "ERROR_CODE"
}
```

### 常见错误码

| HTTP状态码 | 错误码 | 说明 |
|------------|--------|------|
| 400 | INVALID_PARAMETER | 请求参数无效 |
| 404 | MODEL_NOT_FOUND | 模型文件不存在 |
| 409 | TRAINING_IN_PROGRESS | 训练正在进行中 |
| 500 | INTERNAL_ERROR | 服务器内部错误 |

### 错误响应示例

**参数错误**:
```json
{
  "status": "error",
  "message": "请求数据格式错误，需要包含'text'字段",
  "error_code": "INVALID_PARAMETER"
}
```

**模型未找到**:
```json
{
  "status": "error",
  "message": "模型文件不存在: bert_chinese.pth",
  "error_code": "MODEL_NOT_FOUND"
}
```

**训练冲突**:
```json
{
  "status": "error",
  "message": "模型训练正在进行中，请稍后再试",
  "error_code": "TRAINING_IN_PROGRESS"
}
```

## 🔧 使用示例

### Python 示例

```python
import requests
import json

# 基础配置
BASE_URL = "http://localhost:5000"
HEADERS = {"Content-Type": "application/json"}

# 健康检查
response = requests.get(f"{BASE_URL}/")
print(response.json())

# 单文本情感分析
text_data = {"text": "这个产品非常好用！"}
response = requests.post(f"{BASE_URL}/analyze", 
                        headers=HEADERS, 
                        data=json.dumps(text_data))
result = response.json()
print(f"情感: {result['data']['sentiment']}")
print(f"置信度: {result['data']['confidence']}")

# 批量分析
batch_data = {
    "texts": ["很好", "很差", "一般"],
    "batch_size": 10
}
response = requests.post(f"{BASE_URL}/analyze/batch", 
                        headers=HEADERS, 
                        data=json.dumps(batch_data))
results = response.json()
for item in results['data']['results']:
    print(f"{item['text']}: {item['sentiment']}")

# 加载模型
model_data = {
    "model_type": "bert",
    "language": "chinese"
}
response = requests.post(f"{BASE_URL}/models/load", 
                        headers=HEADERS, 
                        data=json.dumps(model_data))
print(response.json())

# 启动训练
train_data = {
    "model_type": "bert",
    "language": "chinese",
    "epochs": 5
}
response = requests.post(f"{BASE_URL}/training/models/train", 
                        headers=HEADERS, 
                        data=json.dumps(train_data))
print(response.json())
```

### JavaScript 示例

```javascript
// 基础配置
const BASE_URL = 'http://localhost:5000';
const HEADERS = {
  'Content-Type': 'application/json'
};

// 健康检查
async function healthCheck() {
  const response = await fetch(`${BASE_URL}/`);
  const data = await response.json();
  console.log(data);
}

// 单文本情感分析
async function analyzeSentiment(text) {
  const response = await fetch(`${BASE_URL}/analyze`, {
    method: 'POST',
    headers: HEADERS,
    body: JSON.stringify({ text })
  });
  const result = await response.json();
  console.log(`情感: ${result.data.sentiment}`);
  console.log(`置信度: ${result.data.confidence}`);
  return result;
}

// 批量分析
async function analyzeBatch(texts) {
  const response = await fetch(`${BASE_URL}/analyze/batch`, {
    method: 'POST',
    headers: HEADERS,
    body: JSON.stringify({ texts, batch_size: 10 })
  });
  const results = await response.json();
  results.data.results.forEach(item => {
    console.log(`${item.text}: ${item.sentiment}`);
  });
  return results;
}

// 加载模型
async function loadModel(modelType, language) {
  const response = await fetch(`${BASE_URL}/models/load`, {
    method: 'POST',
    headers: HEADERS,
    body: JSON.stringify({ model_type: modelType, language })
  });
  const result = await response.json();
  console.log(result);
  return result;
}

// 启动训练
async function startTraining(modelType, language, epochs = 10) {
  const response = await fetch(`${BASE_URL}/training/models/train`, {
    method: 'POST',
    headers: HEADERS,
    body: JSON.stringify({
      model_type: modelType,
      language,
      epochs
    })
  });
  const result = await response.json();
  console.log(result);
  return result;
}

// 使用示例
healthCheck();
analyzeSentiment("这个电影真的很棒！");
analyzeBatch(["很好", "很差", "一般"]);
loadModel("bert", "chinese");
startTraining("bert", "chinese", 5);
```

### cURL 示例

```bash
# 健康检查
curl -X GET http://localhost:5000/

# 单文本情感分析
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "这个产品非常好用！"}'

# 批量分析
curl -X POST http://localhost:5000/analyze/batch \
  -H "Content-Type: application/json" \
  -d '{"texts": ["很好", "很差", "一般"], "batch_size": 10}'

# 获取模型信息
curl -X GET http://localhost:5000/models

# 加载模型
curl -X POST http://localhost:5000/models/load \
  -H "Content-Type: application/json" \
  -d '{"model_type": "bert", "language": "chinese"}'

# 启动训练
curl -X POST http://localhost:5000/training/models/train \
  -H "Content-Type: application/json" \
  -d '{"model_type": "bert", "language": "chinese", "epochs": 5}'

# 获取训练状态
curl -X GET http://localhost:5000/training/status
```

## 📈 性能指标

### 响应时间

| 接口 | 平均响应时间 | 说明 |
|------|-------------|------|
| 健康检查 | < 10ms | 基础状态检查 |
| 单文本分析 | 50-200ms | 取决于模型大小 |
| 批量分析 | 100-500ms | 取决于批次大小 |
| 模型加载 | 1-5s | 取决于模型大小 |
| 训练启动 | < 100ms | 异步任务启动 |

### 并发处理

- **单文本分析**: 支持 100+ 并发请求
- **批量分析**: 支持 50+ 并发请求
- **模型训练**: 单次训练任务（不支持并发）

### 资源使用

- **内存**: 模型加载后约占用 1-2GB
- **CPU**: 推理时约占用 20-50%
- **GPU**: 可选，可显著提升性能

## 🔒 安全说明

### 访问控制

- 当前版本为开发版本，无访问控制
- 生产环境建议添加认证和授权机制

### 数据安全

- 所有文本数据仅用于情感分析
- 不会存储或传输用户隐私信息
- 建议在生产环境中使用 HTTPS

### 输入验证

- 所有输入参数都会进行验证
- 文本长度限制：单文本最大 1000 字符
- 批量分析限制：最多 100 条文本 