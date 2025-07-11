# 数据集说明

## 📋 数据集概述

本项目支持中文和英文两种语言的情感分析数据集，用于训练深度学习模型。

## 🇨🇳 中文数据集：ChnSentiCorp

### 数据集信息

- **数据集名称**: ChnSentiCorp
- **语言**: 中文
- **数据量**: 约 12,000 条评论
- **情感标签**: 正面（1）、负面（0）
- **数据来源**: 酒店、书籍、餐饮等领域的用户评论

### 数据分布

| 情感类别 | 数量 | 比例 |
|----------|------|------|
| 正面 | ~6,000 | 50% |
| 负面 | ~6,000 | 50% |

### 数据源配置

#### 主要数据源：Hugging Face
- **数据集地址**: [seamew/ChnSentiCorp](https://huggingface.co/datasets/seamew/ChnSentiCorp)
- **下载方式**: 自动下载，支持断点续传
- **数据格式**: 标准 Hugging Face 格式

#### 备用数据源：Kaggle
- **数据集地址**: [kaggleyxz/chnsenticorp](https://www.kaggle.com/datasets/kaggleyxz/chnsenticorp)
- **下载方式**: 需要配置 Kaggle API
- **数据格式**: CSV 格式

## 🇺🇸 英文数据集：IMDb Movie Reviews

### 数据集信息

- **数据集名称**: IMDb Movie Reviews
- **语言**: 英文
- **数据量**: 50,000 条电影评论
- **情感标签**: 正面（1）、负面（0）
- **数据来源**: IMDb 电影评论

### 数据分布

| 情感类别 | 数量 | 比例 |
|----------|------|------|
| 正面 | 25,000 | 50% |
| 负面 | 25,000 | 50% |

### 数据源配置

#### 主要数据源：Hugging Face
- **数据集地址**: [imdb](https://huggingface.co/datasets/imdb)
- **下载方式**: 自动下载，支持断点续传
- **数据格式**: 标准 Hugging Face 格式

#### 备用数据源：Kaggle
- **数据集地址**: [lakshmi25npathi/imdb-dataset-of-50k-movie-reviews](https://www.kaggle.com/datasets/lakshmi25npathi/imdb-dataset-of-50k-movie-reviews)
- **下载方式**: 需要配置 Kaggle API
- **数据格式**: CSV 格式

## 🔧 数据集下载配置

### 智能下载策略

系统采用多数据源备用机制，确保数据获取的稳定性：

1. **优先使用 Hugging Face**
   - 速度快，稳定性好
   - 支持断点续传
   - 自动版本管理

2. **备用 Kaggle 数据源**
   - 当 Hugging Face 失败时自动切换
   - 需要配置 Kaggle API 凭据

### Kaggle API 配置

#### 1. 获取 API 凭据

1. 登录 [Kaggle](https://www.kaggle.com/)
2. 进入 "Account" 页面
3. 点击 "Create New API Token"
4. 下载 `kaggle.json` 文件

#### 2. 配置凭据

**Windows**:
```bash
# 将 kaggle.json 复制到用户目录
copy kaggle.json %USERPROFILE%\.kaggle\
```

**macOS/Linux**:
```bash
# 将 kaggle.json 复制到用户目录
cp kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
```

#### 3. 环境变量配置

```bash
# 设置环境变量
export KAGGLE_USERNAME=your_username
export KAGGLE_KEY=your_api_key
```

### 下载脚本使用

#### 命令行下载

```bash
# 下载中文数据集
python -m src.scripts.download_data chinese

# 下载英文数据集
python -m src.scripts.download_data english

# 下载所有数据集
python -m src.scripts.download_data both
```

## 📊 数据质量评估

### 数据清洗

#### 中文数据清洗
- 去除HTML标签和URL
- 去除表情符号和特殊字符
- 使用jieba进行分词
- 过滤停用词

#### 英文数据清洗
- 转换为小写
- 去除特殊字符
- 使用NLTK进行分词
- 过滤停用词

### 数据验证

#### 数据完整性检查
- 检查必要字段是否存在
- 验证文本长度是否合理
- 统计标签分布
- 检测数据格式错误

## 🚀 数据集使用

### 训练数据准备

#### 数据分割
- **训练集**: 80% 的数据用于模型训练
- **验证集**: 10% 的数据用于模型验证
- **测试集**: 10% 的数据用于最终测试

#### 数据增强
- 随机删除部分词汇
- 同义词替换
- 回译增强
- 随机插入词汇

### 数据加载器

#### PyTorch 数据加载器
- 支持批量加载
- 自动文本编码
- 动态填充
- 内存优化

## 📈 数据集统计

### 中文数据集统计

| 指标 | 训练集 | 验证集 | 测试集 |
|------|--------|--------|--------|
| 样本数 | 9,600 | 1,200 | 1,200 |
| 平均长度 | 45.2 | 44.8 | 45.1 |
| 最大长度 | 1,024 | 1,024 | 1,024 |
| 最小长度 | 5 | 5 | 5 |

### 英文数据集统计

| 指标 | 训练集 | 验证集 | 测试集 |
|------|--------|--------|--------|
| 样本数 | 20,000 | 2,500 | 2,500 |
| 平均长度 | 234.5 | 233.8 | 234.2 |
| 最大长度 | 2,048 | 2,048 | 2,048 |
| 最小长度 | 10 | 10 | 10 |

## 🔍 数据探索

### 文本长度分布
- 中文文本平均长度较短，适合CNN和RNN模型
- 英文文本平均长度较长，适合Transformer模型
- 两种语言都存在长尾分布

### 标签分布
- 两种数据集都保持平衡的标签分布
- 正面和负面样本各占50%
- 有利于模型训练的稳定性

## 🛠️ 常见问题

### 下载问题

**Q: 数据集下载失败？**
A: 检查网络连接，尝试使用备用数据源

**Q: Kaggle API 配置失败？**
A: 确保 `kaggle.json` 文件格式正确，权限设置正确

**Q: 下载速度慢？**
A: 可以配置代理或使用国内镜像源

### 数据质量问题

**Q: 数据中包含噪声？**
A: 使用数据清洗函数处理原始数据

**Q: 标签不平衡？**
A: 使用数据增强或重采样技术平衡数据

**Q: 文本长度差异大？**
A: 设置合理的最大长度限制，使用截断或填充

### 使用问题

**Q: 内存不足？**
A: 使用数据生成器或分批加载数据

**Q: 加载速度慢？**
A: 使用缓存机制或预加载数据

**Q: 格式不兼容？**
A: 检查数据格式，使用相应的数据加载器

## 📚 参考资料

- [Hugging Face Datasets](https://huggingface.co/docs/datasets/)
- [Kaggle API Documentation](https://github.com/Kaggle/kaggle-api)
- [ChnSentiCorp Dataset](https://huggingface.co/datasets/seamew/ChnSentiCorp)
- [IMDb Dataset](https://huggingface.co/datasets/imdb)
- [NLTK Documentation](https://www.nltk.org/)
- [jieba Documentation](https://github.com/fxsjy/jieba) 