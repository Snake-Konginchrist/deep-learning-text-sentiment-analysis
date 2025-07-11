# 基于深度学习的文本情感分析研究与应用

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-red.svg)](https://pytorch.org/)
[![Vue](https://img.shields.io/badge/Vue-3.0+-green.svg)](https://vuejs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> 🚀 基于深度学习的情感分析系统，支持中文和英文文本的情感分类，提供完整的训练、部署和应用解决方案。

## 📋 项目简介

本项目是一个基于深度学习的情感分析系统，集成了TextCNN、BiLSTM、BERT等多种模型架构，支持中文和英文文本的情感分类。系统提供完整的Web界面，包括数据集管理、模型训练、模型管理和情感分析等功能。

### ✨ 主要特性

- 🤖 **多模型支持**: TextCNN、BiLSTM、BERT三种深度学习模型
- 🌍 **多语言支持**: 中文（ChnSentiCorp）和英文（IMDb）数据集
- 🎯 **智能训练**: 自动数据管理、进度监控、参数优化
- 🖥️ **友好界面**: 基于Vue3的现代化Web界面
- 🔧 **易于部署**: 完整的本地部署方案
- 📊 **实时分析**: 支持单文本和批量文本情感分析

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+
- npm 或 yarn

### 快速启动

1. **克隆项目**
   ```bash
   git clone https://gitee.com/Snake-Konginchrist/deep-learning-text-sentiment-analysis.git
   cd deep-learning-text-sentiment-analysis
   ```

2. **启动后端**
   ```bash
   # 创建虚拟环境
   python -m venv venv
   
   # 激活虚拟环境
   # Windows: venv\Scripts\activate
   # macOS/Linux: source venv/bin/activate
   
   # 安装依赖
   pip install -r requirements.txt
   
   # 启动服务
   python run_server.py
   ```

3. **启动前端**
   ```bash
   cd webui
   npm install
   npm run dev
   ```

4. **访问应用**
   
   打开浏览器访问 `http://localhost:5173`

### 📱 使用流程

1. **下载数据集** → 2. **训练模型** → 3. **加载模型** → 4. **开始分析**

## 🏗️ 系统架构

```
用户界面 (Vue3) → API服务 (Flask) → 深度学习模型 (PyTorch) → 数据存储
```

### 核心模块

- **前端界面**: Vue3 + TypeScript + Element Plus
- **后端API**: Flask + CORS + PyTorch
- **模型架构**: TextCNN / BiLSTM / BERT
- **数据处理**: jieba / NLTK / transformers

## 📚 详细文档

- 📖 **[技术文档](docs/TECHNICAL.md)**: 详细的技术实现和架构说明
- 🚀 **[部署指南](docs/DEPLOYMENT.md)**: 完整的部署和配置说明
- 🎯 **[API文档](docs/API.md)**: API接口详细说明
- 🔧 **[开发指南](docs/DEVELOPMENT.md)**: 开发环境搭建和贡献指南
- 📊 **[数据集说明](docs/DATASETS.md)**: 数据集介绍和下载配置

## 🤝 交流与支持

- **QQ交流群**: 1022820973
- **项目地址**: https://gitee.com/Snake-Konginchrist/deep-learning-text-sentiment-analysis
- **问题反馈**: 欢迎在Gitee提交Issue

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE) 开源。

## 🙏 致谢

感谢所有为开源社区做出贡献的开发者们！

---

**如果这个项目对您有帮助，请给个 ⭐ Star 支持一下！**

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Snake-Konginchrist/deep-learning-text-sentiment-analysis&type=Date)](https://www.star-history.com/#Snake-Konginchrist/deep-learning-text-sentiment-analysis&Date)