# 深度学习文本情感分析后端系统

## 项目概述

这是一个基于深度学习的文本情感分析后端系统，支持中英文文本的情感分类。系统采用模块化设计，实现了TextCNN、BiLSTM和BERT三种主流深度学习模型，并提供RESTful API接口供前端Vue应用调用。

## 技术特性

- **多模型支持**: TextCNN、BiLSTM、BERT三种情感分析模型
- **多语言支持**: 中文（ChnSentiCorp数据集）和英文（IMDb数据集）
- **模块化设计**: 清晰的代码结构，易于维护和扩展
- **RESTful API**: 完整的API接口，支持单文本和批量分析
- **自动数据集下载**: 使用Hugging Face自动下载和预处理数据

## 项目结构

```
├── src/                     # 源代码目录
│   ├── utils/              # 工具模块
│   │   ├── config.py       # 配置管理
│   │   └── text_processor.py # 文本预处理
│   ├── scripts/            # 命令行脚本工具
│   │   ├── dataset_loader.py # 数据集加载器
│   │   └── download_data.py # 数据下载命令行工具
│   ├── architectures/      # 深度学习模型架构
│   │   ├── textcnn.py      # TextCNN模型
│   │   ├── bilstm.py       # BiLSTM模型
│   │   └── bert_model.py   # BERT模型
│   ├── services/           # 业务服务
│   │   └── sentiment_analyzer.py # 情感分析服务
│   ├── training/           # 模型训练模块
│   │   └── trainer.py      # 训练器
│   └── api/                # API接口
│       ├── app.py          # Flask应用
│       ├── training_api.py # 训练相关API
│       └── test_client.py  # API测试客户端
├── datasets/               # 数据集存储目录（存放下载的数据集文件）
├── models/                 # 模型存储目录（存放训练好的模型文件）
├── requirements.txt        # 依赖包列表
├── run_server.py          # 服务器启动脚本
└── quick_start.py         # 快速启动脚本
```

## 快速开始

### 1. 环境准备

#### 1.1 Python版本要求
确保系统已安装Python 3.8或更高版本：
```bash
python --version
# 应该显示 Python 3.8.x 或更高版本
```

#### 1.2 创建虚拟环境
为了避免依赖冲突，强烈建议使用虚拟环境：

**使用 venv（推荐）：**
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境（Windows）
venv\Scripts\activate

# 激活虚拟环境（Linux/Mac）
source venv/bin/activate

# 确认虚拟环境已激活（命令行前应显示 (venv)）
```

**使用 conda：**
```bash
# 创建conda虚拟环境
conda create -n venv python=3.12

# 激活环境
conda activate venv
```

#### 1.3 升级pip
```bash
# 升级pip到最新版本
python -m pip install --upgrade pip
```

### 2. 安装依赖

在激活的虚拟环境中安装项目依赖：
```bash
# 安装Python依赖包
pip install -r requirements.txt

# 验证关键包是否安装成功
python -c "import torch; print('PyTorch版本:', torch.__version__)"
python -c "import transformers; print('Transformers版本:', transformers.__version__)"
```

**注意事项：**
- 如果在中国大陆，建议使用清华源加速下载：
  ```bash
  pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
  ```
- 如果安装PyTorch时遇到问题，可访问 [PyTorch官网](https://pytorch.org/get-started/locally/) 获取适合你系统的安装命令

### 3. 下载数据集

```bash
# 下载中文数据集
python -m src.scripts.download_data chinese

# 下载英文数据集  
python -m src.scripts.download_data english

# 下载所有数据集
python -m src.scripts.download_data both
```

### 4. 启动API服务器

```bash
# 启动Flask开发服务器
python run_server.py
```

服务器将在 `http://localhost:5000` 启动。

### 5. 测试API接口

```bash
# 运行API测试脚本
python -m src.api.test_client
```

### 6. 虚拟环境管理

#### 退出虚拟环境
```bash
# 退出当前虚拟环境
deactivate
```

#### 重新激活虚拟环境
```bash
# venv方式重新激活（Windows）
venv\Scripts\activate

# venv方式重新激活（Linux/Mac）
source venv/bin/activate

# conda方式重新激活
conda activate venv
```

#### 删除虚拟环境
```bash
# venv方式：直接删除文件夹
rm -rf venv  # Linux/Mac
rmdir /s venv  # Windows

# conda方式：
conda env remove -n venv
```

## API接口文档

### 健康检查

```http
GET /
```

返回API状态信息。

### 单文本情感分析

```http
POST /analyze
Content-Type: application/json

{
    "text": "这个电影真的很棒！"
}
```

响应：
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

### 获取模型信息

```http
GET /models
```

返回当前模型状态和可用模型列表。

## 配置说明

主要配置项在 `src/utils/config.py` 中：

- **数据集配置**: 支持的数据集和下载源
- **模型配置**: 各模型的超参数设置
- **API配置**: 服务器地址、端口、跨域设置
- **训练配置**: 批次大小、学习率等训练参数

## 模型说明

### TextCNN
- 基于卷积神经网络的文本分类模型
- 适合短文本的特征提取
- 使用多种尺寸的卷积核捕获不同长度的n-gram特征

### BiLSTM  
- 基于双向长短期记忆网络的序列模型
- 能够捕获文本的前后文信息
- 支持注意力机制增强关键信息

### BERT
- 基于Transformer的预训练语言模型
- 中文使用bert-base-chinese，英文使用bert-base-uncased
- 通过微调适配情感分析任务

## 开发指南

### 添加新模型

1. 在 `src/models/` 目录下创建新的模型文件
2. 继承 `nn.Module` 并实现必要方法
3. 在配置文件中添加模型参数
4. 更新情感分析服务以支持新模型

### 添加新语言

1. 在配置文件中添加新的数据集配置
2. 更新文本处理器支持新语言的分词
3. 修改数据加载器处理新的数据格式
4. 测试并验证新语言的分析效果

## 注意事项

- 首次运行会自动下载预训练模型和数据集，需要网络连接
- BERT模型需要较大内存，建议至少8GB RAM
- 生产环境建议使用WSGI服务器（如Gunicorn）而非Flask开发服务器
- 模型文件会保存在 `models/` 目录，确保有足够磁盘空间

## 故障排除

### 常见问题

1. **下载数据集失败**
   - 检查网络连接
   - 确认Hugging Face可访问性
   - 尝试使用镜像源

2. **模型加载失败**
   - 检查模型文件是否存在
   - 确认模型配置与训练时一致
   - 查看错误日志定位问题

3. **API请求失败**
   - 确认服务器正常启动
   - 检查端口是否被占用
   - 验证请求格式是否正确

### 日志查看

项目日志保存在 `logs/` 目录下，可通过查看日志文件获取详细的错误信息。

## 许可证

本项目采用MIT许可证，详见LICENSE文件。 