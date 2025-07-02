# Kaggle API 配置说明

## 简介

本项目支持从Hugging Face和Kaggle多个数据源下载数据集。当Hugging Face下载失败时，系统会自动切换到Kaggle备用数据源。

## Kaggle API 配置（可选）

### 1. 安装Kaggle包

```bash
pip install kaggle
```

### 2. 获取API凭证

1. 访问 [Kaggle官网](https://www.kaggle.com/) 并登录
2. 点击右上角头像 → "Account"
3. 滚动到"API"部分
4. 点击"Create New API Token"
5. 下载`kaggle.json`文件

### 3. 配置API凭证

#### Windows:
```bash
# 创建.kaggle目录
mkdir %USERPROFILE%\.kaggle

# 复制kaggle.json文件到该目录
copy kaggle.json %USERPROFILE%\.kaggle\

# 或者设置环境变量
set KAGGLE_USERNAME=your_username
set KAGGLE_KEY=your_api_key
```

#### Linux/Mac:
```bash
# 创建.kaggle目录
mkdir ~/.kaggle

# 复制kaggle.json文件到该目录
cp kaggle.json ~/.kaggle/

# 设置文件权限
chmod 600 ~/.kaggle/kaggle.json

# 或者设置环境变量
export KAGGLE_USERNAME=your_username
export KAGGLE_KEY=your_api_key
```

## 数据源回退机制

系统会按以下顺序尝试下载数据集：

1. **Hugging Face**（主要数据源）
   - 中文：`seamew/ChnSentiCorp`
   - 英文：`imdb`

2. **Kaggle API**（备用数据源）
   - 中文：`kaggleyxz/chnsenticorp`
   - 英文：`lakshmi25npathi/imdb-dataset-of-50k-movie-reviews`

3. **GitHub备用源**（最后备用）
   - 中文：GitHub上的开源中文情感数据集

## 使用说明

- **无需配置Kaggle API**：系统会尝试直接下载备用数据源
- **配置了Kaggle API**：可以使用完整的Kaggle数据集下载功能
- **网络限制**：所有数据源都无法访问时，请手动下载数据集到`datasets/`目录

## 故障排除

### 1. Hugging Face下载慢或失败
- 使用代理或VPN
- 等待系统自动切换到Kaggle数据源

### 2. Kaggle API认证失败
```bash
# 检查凭证文件
cat ~/.kaggle/kaggle.json  # Linux/Mac
type %USERPROFILE%\.kaggle\kaggle.json  # Windows

# 重新下载API Token
```

### 3. 网络连接问题
- 检查防火墙设置
- 尝试使用移动热点
- 联系网络管理员开放相关域名

## 支持的数据集

| 语言 | 主数据源 | 备用数据源 | 数据量 |
|------|----------|------------|--------|
| 中文 | Hugging Face ChnSentiCorp | Kaggle ChnSentiCorp | 约12,000条 |
| 英文 | Hugging Face IMDb | Kaggle IMDb数据集 | 约50,000条 |

## 联系方式

如有问题，请在项目GitHub页面提交Issue。 