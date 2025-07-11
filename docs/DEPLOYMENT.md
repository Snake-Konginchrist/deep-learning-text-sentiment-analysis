# 部署指南

## 📋 环境要求

### 系统要求
- **操作系统**: Windows 10+, macOS 10.14+, Ubuntu 18.04+
- **Python**: 3.8 或更高版本
- **Node.js**: 16.0 或更高版本
- **内存**: 建议 8GB 以上
- **存储**: 至少 5GB 可用空间

### 硬件要求
- **CPU**: 支持 AVX2 指令集（推荐 Intel i5 或 AMD Ryzen 5 以上）
- **GPU**: 可选，支持 CUDA 的 NVIDIA GPU 可加速训练
- **网络**: 稳定的互联网连接（用于下载数据集和模型）

## 🚀 完整部署流程

### 1. 环境准备

#### 1.1 安装 Python
```bash
# 下载并安装 Python 3.8+
# Windows: 从 python.org 下载安装包
# macOS: brew install python@3.8
# Ubuntu: sudo apt install python3.8 python3.8-venv
```

#### 1.2 安装 Node.js
```bash
# 下载并安装 Node.js 16+
# Windows: 从 nodejs.org 下载安装包
# macOS: brew install node
# Ubuntu: curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
```

### 2. 项目部署

#### 2.1 克隆项目
```bash
git clone https://gitee.com/Snake-Konginchrist/deep-learning-text-sentiment-analysis.git
cd deep-learning-text-sentiment-analysis
```

#### 2.2 后端部署

**创建虚拟环境**
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
```

**安装 Python 依赖**
```bash
# 升级 pip
pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt
```

**配置环境变量（可选）**
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，添加 Kaggle API 凭据
# 参考 KAGGLE_SETUP.md 进行配置
```

**启动后端服务**
```bash
python run_server.py
```

后端服务将在 `http://localhost:5000` 启动

#### 2.3 前端部署

**进入前端目录**
```bash
cd webui
```

**安装依赖**
```bash
npm install
# 或使用 yarn
yarn install
```

**启动开发服务器**
```bash
npm run dev
# 或使用 yarn
yarn dev
```

前端服务将在 `http://localhost:5173` 启动

### 3. 生产环境部署

#### 3.1 使用 Gunicorn 部署后端

**安装 Gunicorn**
```bash
pip install gunicorn
```

**创建 Gunicorn 配置文件**
```bash
# 创建 gunicorn.conf.py
cat > gunicorn.conf.py << EOF
bind = "0.0.0.0:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
EOF
```

**启动生产服务**
```bash
gunicorn -c gunicorn.conf.py src.api.app:app
```

#### 3.2 使用 Nginx 部署前端

**构建生产版本**
```bash
cd webui
npm run build
```

**配置 Nginx**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # 前端静态文件
    location / {
        root /path/to/webui/dist;
        try_files $uri $uri/ /index.html;
    }
    
    # API 代理
    location /api/ {
        proxy_pass http://localhost:5000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 4. Docker 部署

#### 4.1 使用 Docker Compose

**创建 docker-compose.yml**
```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./models:/app/models
      - ./datasets:/app/datasets
    environment:
      - FLASK_ENV=production

  frontend:
    build:
      context: .
      dockerfile: webui/Dockerfile
    ports:
      - "80:80"
    depends_on:
      - backend
```

**启动服务**
```bash
docker-compose up -d
```

## 🔧 配置说明

### 环境变量配置

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `FLASK_ENV` | Flask 环境 | `development` |
| `FLASK_DEBUG` | 调试模式 | `True` |
| `KAGGLE_USERNAME` | Kaggle 用户名 | - |
| `KAGGLE_KEY` | Kaggle API Key | - |
| `MODEL_PATH` | 模型存储路径 | `./models` |
| `DATASET_PATH` | 数据集存储路径 | `./datasets` |

### 端口配置

| 服务 | 默认端口 | 说明 |
|------|----------|------|
| 后端 API | 5000 | Flask 开发服务器 |
| 前端开发 | 5173 | Vite 开发服务器 |
| 前端生产 | 80 | Nginx 服务器 |

## 🐛 常见问题

### 后端问题

**Q: 端口 5000 被占用？**
```bash
# 查看端口占用
netstat -ano | findstr :5000  # Windows
lsof -i :5000                 # macOS/Linux

# 杀死进程
taskkill /PID <进程ID>        # Windows
kill -9 <进程ID>              # macOS/Linux
```

**Q: 依赖安装失败？**
```bash
# 升级 pip
pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

**Q: 虚拟环境激活失败？**
```bash
# Windows PowerShell 可能需要设置执行策略
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 或者使用 cmd
venv\Scripts\activate.bat
```

### 前端问题

**Q: Node.js 版本过低？**
```bash
# 检查版本
node --version

# 升级 Node.js
# 建议使用 nvm 管理 Node.js 版本
nvm install 16
nvm use 16
```

**Q: npm 安装失败？**
```bash
# 清除缓存
npm cache clean --force

# 使用国内镜像
npm config set registry https://registry.npmmirror.com/
```

**Q: 前端无法连接后端？**
```bash
# 检查后端是否运行
curl http://localhost:5000/

# 检查 CORS 配置
# 确保后端允许前端域名访问
```

### 数据集问题

**Q: 数据集下载失败？**
```bash
# 检查网络连接
ping huggingface.co

# 配置代理（如果需要）
export https_proxy=http://proxy:port
export http_proxy=http://proxy:port
```

**Q: Kaggle API 配置问题？**
```bash
# 参考 KAGGLE_SETUP.md 配置 Kaggle API
# 确保 kaggle.json 文件格式正确
```

## 📊 性能优化

### 后端优化

1. **使用 Gunicorn 替代 Flask 开发服务器**
2. **配置适当的工作进程数**
3. **启用模型缓存**
4. **使用 Redis 缓存（可选）**

### 前端优化

1. **启用 Gzip 压缩**
2. **配置静态资源缓存**
3. **使用 CDN 加速**
4. **启用 HTTP/2**

### 模型优化

1. **使用 GPU 加速训练**
2. **模型量化减少内存占用**
3. **批量推理提高吞吐量**
4. **模型缓存避免重复加载**

## 🔒 安全配置

### 生产环境安全

1. **使用 HTTPS**
2. **配置防火墙**
3. **定期更新依赖**
4. **限制 API 访问频率**
5. **日志监控和告警**

### 数据安全

1. **敏感数据加密存储**
2. **定期备份模型和数据**
3. **访问权限控制**
4. **审计日志记录**

## 📈 监控和维护

### 系统监控

1. **CPU 和内存使用率**
2. **磁盘空间监控**
3. **网络连接状态**
4. **API 响应时间**

### 日志管理

1. **应用日志收集**
2. **错误日志告警**
3. **性能指标记录**
4. **用户行为分析**

### 备份策略

1. **模型文件备份**
2. **配置文件备份**
3. **数据库备份（如果有）**
4. **定期恢复测试** 