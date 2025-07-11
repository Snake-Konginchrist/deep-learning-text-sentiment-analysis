# 开发指南

## 📋 开发环境搭建

### 系统要求

- **操作系统**: Windows 10+, macOS 10.14+, Ubuntu 18.04+
- **Python**: 3.8 或更高版本
- **Node.js**: 16.0 或更高版本
- **Git**: 2.20 或更高版本
- **IDE**: 推荐 VS Code 或 PyCharm

### 环境准备

#### 1. 安装 Python

**Windows**:
```bash
# 从 python.org 下载安装包
# 确保勾选 "Add Python to PATH"
```

**macOS**:
```bash
# 使用 Homebrew
brew install python@3.8

# 或从 python.org 下载安装包
```

**Ubuntu**:
```bash
sudo apt update
sudo apt install python3.8 python3.8-venv python3.8-dev
```

#### 2. 安装 Node.js

**Windows**:
```bash
# 从 nodejs.org 下载安装包
```

**macOS**:
```bash
# 使用 Homebrew
brew install node

# 或使用 nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 16
nvm use 16
```

**Ubuntu**:
```bash
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt-get install -y nodejs
```

#### 3. 安装 Git

**Windows**:
```bash
# 从 git-scm.com 下载安装包
```

**macOS**:
```bash
# 使用 Homebrew
brew install git

# 或从 git-scm.com 下载安装包
```

**Ubuntu**:
```bash
sudo apt install git
```

### 项目初始化

#### 1. 克隆项目

```bash
git clone https://gitee.com/Snake-Konginchrist/deep-learning-text-sentiment-analysis.git
cd deep-learning-text-sentiment-analysis
```

#### 2. 后端环境设置

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 升级 pip
pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt
```

#### 3. 前端环境设置

```bash
# 进入前端目录
cd webui

# 安装依赖
npm install
# 或使用 yarn
yarn install
```

#### 4. 开发工具配置

**VS Code 推荐扩展**:
- Python
- Vue Language Features (Volar)
- TypeScript Vue Plugin (Volar)
- ESLint
- Prettier
- GitLens

**PyCharm 配置**:
- 配置 Python 解释器为虚拟环境
- 安装 Vue.js 插件
- 配置代码风格

## 🏗️ 项目结构

```
deep-learning-text-sentiment-analysis/
├── docs/                    # 文档目录
│   ├── TECHNICAL.md        # 技术文档
│   ├── DEPLOYMENT.md       # 部署指南
│   ├── API.md              # API文档
│   ├── DEVELOPMENT.md      # 开发指南
│   └── DATASETS.md         # 数据集说明
├── src/                    # 后端源码
│   ├── api/               # API接口
│   ├── architectures/     # 模型架构
│   ├── scripts/           # 脚本工具
│   ├── services/          # 业务服务
│   ├── training/          # 训练模块
│   └── utils/             # 工具函数
├── webui/                  # 前端源码
│   ├── src/               # 源码目录
│   ├── public/            # 静态资源
│   └── package.json       # 依赖配置
├── models/                 # 模型文件
├── datasets/               # 数据集
├── logs/                   # 日志文件
├── requirements.txt        # Python依赖
├── run_server.py          # 启动脚本
└── README.md              # 项目说明
```

## 🔧 开发规范

### 代码风格

#### Python 代码规范

- 遵循 PEP 8 规范
- 使用 4 空格缩进
- 行长度不超过 120 字符
- 使用类型注解
- 添加详细的文档字符串

**示例**:
```python
from typing import Dict, List, Optional
import torch
import torch.nn as nn


class SentimentAnalyzer:
    """
    情感分析器类
    
    用于加载模型并进行文本情感分析。
    
    Attributes:
        model_type (str): 模型类型
        language (str): 语言类型
        model (Optional[nn.Module]): 加载的模型
    """
    
    def __init__(self, model_type: str = "bert", language: str = "chinese") -> None:
        """
        初始化情感分析器
        
        Args:
            model_type: 模型类型，支持 'textcnn', 'bilstm', 'bert'
            language: 语言类型，支持 'chinese', 'english'
        """
        self.model_type = model_type
        self.language = language
        self.model: Optional[nn.Module] = None
```

#### TypeScript/JavaScript 代码规范

- 使用 ESLint + Prettier
- 遵循 Vue 3 组合式 API 规范
- 使用 TypeScript 类型注解
- 组件命名使用 PascalCase
- 文件命名使用 kebab-case

**示例**:
```typescript
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import type { SentimentResult } from '@/types/sentiment'

interface AnalysisState {
  isAnalyzing: boolean
  results: SentimentResult[]
  error: string | null
}

export const useSentimentAnalysis = () => {
  const state = ref<AnalysisState>({
    isAnalyzing: false,
    results: [],
    error: null
  })

  const hasResults = computed(() => state.value.results.length > 0)

  const analyzeText = async (text: string): Promise<void> => {
    try {
      state.value.isAnalyzing = true
      state.value.error = null
      
      // 分析逻辑
      const result = await apiService.analyzeSentiment(text)
      state.value.results.push(result)
      
      ElMessage.success('分析完成')
    } catch (error) {
      state.value.error = error instanceof Error ? error.message : '分析失败'
      ElMessage.error(state.value.error)
    } finally {
      state.value.isAnalyzing = false
    }
  }

  return {
    state: readonly(state),
    hasResults,
    analyzeText
  }
}
```

### Git 提交规范

使用 Angular 提交规范：

```
<type>(<scope>): <subject>

<body>

<footer>
```

**类型说明**:
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

**示例**:
```bash
git commit -m "feat(api): 添加批量情感分析接口

- 支持批量文本情感分析
- 添加进度显示功能
- 优化错误处理机制

Closes #123"
```

### 分支管理

- `main`: 主分支，用于生产环境
- `develop`: 开发分支，用于集成测试
- `feature/*`: 功能分支，用于开发新功能
- `hotfix/*`: 热修复分支，用于紧急修复

## 🧪 测试规范

### 后端测试

#### 单元测试

使用 `pytest` 进行单元测试：

```python
import pytest
from src.services.sentiment_analyzer import SentimentAnalyzer


class TestSentimentAnalyzer:
    """情感分析器测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.analyzer = SentimentAnalyzer(model_type="bert", language="chinese")
    
    def test_analyzer_initialization(self):
        """测试分析器初始化"""
        assert self.analyzer.model_type == "bert"
        assert self.analyzer.language == "chinese"
        assert self.analyzer.model is None
    
    def test_invalid_model_type(self):
        """测试无效模型类型"""
        with pytest.raises(ValueError):
            SentimentAnalyzer(model_type="invalid")
    
    def test_invalid_language(self):
        """测试无效语言类型"""
        with pytest.raises(ValueError):
            SentimentAnalyzer(language="invalid")
```

#### 集成测试

```python
import pytest
from src.api.app import app


@pytest.fixture
def client():
    """测试客户端"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_health_check(client):
    """测试健康检查接口"""
    response = client.get('/')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'


def test_sentiment_analysis(client):
    """测试情感分析接口"""
    response = client.post('/analyze', json={'text': '这个电影很棒！'})
    assert response.status_code == 200
    data = response.get_json()
    assert 'sentiment' in data['data']
```

### 前端测试

#### 单元测试

使用 `Vitest` 进行单元测试：

```typescript
import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { ElMessage } from 'element-plus'
import SentimentAnalyzer from '@/components/SentimentAnalyzer.vue'

describe('SentimentAnalyzer', () => {
  let wrapper: any

  beforeEach(() => {
    wrapper = mount(SentimentAnalyzer)
  })

  it('renders correctly', () => {
    expect(wrapper.find('.sentiment-analyzer').exists()).toBe(true)
  })

  it('analyzes text correctly', async () => {
    const textInput = wrapper.find('textarea')
    await textInput.setValue('这个电影很棒！')
    
    const analyzeButton = wrapper.find('button')
    await analyzeButton.trigger('click')
    
    expect(wrapper.vm.isAnalyzing).toBe(true)
  })
})
```

#### E2E 测试

使用 `Playwright` 进行端到端测试：

```typescript
import { test, expect } from '@playwright/test'

test('sentiment analysis workflow', async ({ page }) => {
  // 访问首页
  await page.goto('http://localhost:5173')
  
  // 导航到分析页面
  await page.click('text=情感分析')
  
  // 输入文本
  await page.fill('textarea', '这个产品非常好用！')
  
  // 点击分析按钮
  await page.click('button:has-text("开始分析")')
  
  // 等待结果
  await page.waitForSelector('.analysis-result')
  
  // 验证结果
  const result = await page.textContent('.sentiment-label')
  expect(result).toContain('正面')
})
```

## 🚀 开发流程

### 1. 功能开发流程

1. **创建功能分支**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/new-feature
   ```

2. **开发功能**
   - 编写代码
   - 添加测试
   - 更新文档

3. **提交代码**
   ```bash
   git add .
   git commit -m "feat(component): 添加新功能"
   ```

4. **推送分支**
   ```bash
   git push origin feature/new-feature
   ```

5. **创建 Pull Request**
   - 在 Gitee 上创建 PR
   - 填写详细的描述
   - 等待代码审查

### 2. Bug 修复流程

1. **创建修复分支**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b hotfix/bug-fix
   ```

2. **修复问题**
   - 定位问题
   - 编写修复代码
   - 添加测试用例

3. **提交修复**
   ```bash
   git add .
   git commit -m "fix(api): 修复情感分析接口错误"
   ```

4. **合并到主分支**
   ```bash
   git checkout main
   git merge hotfix/bug-fix
   git push origin main
   ```

## 📊 性能优化

### 后端优化

1. **模型优化**
   ```python
   # 使用模型缓存
   @lru_cache(maxsize=1)
   def load_model(model_type: str, language: str):
       # 模型加载逻辑
       pass
   
   # 批量处理
   def batch_analyze(texts: List[str], batch_size: int = 32):
       results = []
       for i in range(0, len(texts), batch_size):
           batch = texts[i:i + batch_size]
           batch_results = model(batch)
           results.extend(batch_results)
       return results
   ```

2. **API 优化**
   ```python
   # 使用异步处理
   from concurrent.futures import ThreadPoolExecutor
   
   executor = ThreadPoolExecutor(max_workers=4)
   
   @app.route('/analyze/batch', methods=['POST'])
   def analyze_batch():
       texts = request.json['texts']
       future = executor.submit(batch_analyze, texts)
       return jsonify({'task_id': future.result()})
   ```

### 前端优化

1. **组件优化**
   ```typescript
   // 使用 computed 缓存计算结果
   const filteredResults = computed(() => {
     return results.value.filter(result => 
       result.confidence > confidenceThreshold.value
     )
   })
   
   // 使用 v-memo 缓存渲染结果
   <div v-memo="[result.id, result.sentiment]">
     {{ result.text }}: {{ result.sentiment }}
   </div>
   ```

2. **API 调用优化**
   ```typescript
   // 使用防抖
   import { debounce } from 'lodash-es'
   
   const debouncedAnalyze = debounce(async (text: string) => {
     const result = await apiService.analyzeSentiment(text)
     return result
   }, 300)
   ```

## 🔍 调试技巧

### 后端调试

1. **使用 pdb 调试**
   ```python
   import pdb
   
   def analyze_sentiment(text: str):
       pdb.set_trace()  # 设置断点
       result = model(text)
       return result
   ```

2. **使用日志调试**
   ```python
   import logging
   
   logging.basicConfig(level=logging.DEBUG)
   logger = logging.getLogger(__name__)
   
   def analyze_sentiment(text: str):
       logger.debug(f"Analyzing text: {text}")
       result = model(text)
       logger.debug(f"Analysis result: {result}")
       return result
   ```

### 前端调试

1. **使用 Vue DevTools**
   - 安装 Vue DevTools 浏览器扩展
   - 查看组件状态和事件

2. **使用浏览器调试**
   ```typescript
   // 在代码中添加断点
   debugger
   
   // 使用 console 调试
   console.log('Debug info:', data)
   console.table(results)
   ```

## 📚 学习资源

### 技术文档

- [Vue 3 官方文档](https://vuejs.org/)
- [Element Plus 文档](https://element-plus.org/)
- [Flask 官方文档](https://flask.palletsprojects.com/)
- [PyTorch 官方文档](https://pytorch.org/docs/)

### 最佳实践

- [Vue 3 组合式 API 最佳实践](https://vuejs.org/guide/extras/composition-api-faq.html)
- [Flask 应用工厂模式](https://flask.palletsprojects.com/en/2.3.x/patterns/appfactories/)
- [PyTorch 模型训练最佳实践](https://pytorch.org/tutorials/beginner/basics/quickstart_tutorial.html)

### 社区资源

- [Vue.js 社区](https://forum.vuejs.org/)
- [Flask 社区](https://flask.palletsprojects.com/en/2.3.x/community/)
- [PyTorch 论坛](https://discuss.pytorch.org/)

## 🤝 贡献指南

### 如何贡献

1. **Fork 项目**
   - 在 Gitee 上 Fork 本项目

2. **创建功能分支**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **提交更改**
   ```bash
   git commit -m 'feat: 添加新功能'
   ```

4. **推送分支**
   ```bash
   git push origin feature/amazing-feature
   ```

5. **创建 Pull Request**
   - 在 Gitee 上创建 Pull Request
   - 填写详细的描述和测试说明

### 贡献规范

- 遵循项目的代码风格
- 为新功能添加测试
- 更新相关文档
- 确保所有测试通过
- 提供清晰的提交信息

### 问题反馈

- 使用 Gitee Issues 报告 Bug
- 提供详细的复现步骤
- 包含环境信息和错误日志
- 使用 Issue 模板

## 📞 联系方式

- **QQ交流群**: 1022820973
- **项目地址**: https://gitee.com/Snake-Konginchrist/deep-learning-text-sentiment-analysis
- **问题反馈**: 欢迎在 Gitee 提交 Issue

---

感谢您对项目的贡献！🚀 