<!-- 关于项目页面 -->
<script setup lang="ts">
import { ref } from 'vue'

// 技术栈信息
const techStack = {
  frontend: [
    { name: 'Vue 3', version: '3.4+', description: '渐进式JavaScript框架，采用Composition API' },
    { name: 'TypeScript', version: '5.0+', description: '带类型的JavaScript，提升开发体验' },
    { name: 'Element Plus', version: '2.4+', description: '基于Vue3的组件库' },
    { name: 'Pinia', version: '2.1+', description: 'Vue的状态管理库' },
    { name: 'Vite', version: '5.0+', description: '快速的前端构建工具' }
  ],
  backend: [
    { name: 'Python', version: '3.8+', description: '主要编程语言' },
    { name: 'Flask', version: '2.3+', description: '轻量级Web框架' },
    { name: 'PyTorch', version: '2.0+', description: '深度学习框架' },
    { name: 'Transformers', version: '4.30+', description: 'Hugging Face模型库' },
    { name: 'Scikit-learn', version: '1.3+', description: '机器学习库' }
  ],
  models: [
    { name: 'TextCNN', description: '基于卷积神经网络的文本分类模型' },
    { name: 'BiLSTM', description: '双向长短期记忆网络模型' },
    { name: 'BERT', description: '基于Transformer的预训练语言模型' }
  ]
}

// 功能特性
const features = [
  {
    icon: '🔍',
    title: '智能文本分析',
    description: '支持中英文情感分析，准确识别文本的情感倾向'
  },
  {
    icon: '🚀',
    title: '多模型支持',
    description: '集成TextCNN、BiLSTM、BERT三种主流深度学习模型'
  },
  {
    icon: '📊',
    title: '批量处理',
    description: '支持批量文本分析，提高处理效率'
  },
  {
    icon: '🎯',
    title: '高精度分析',
    description: '基于大规模数据集训练，提供高准确率的情感识别'
  },
  {
    icon: '🔧',
    title: '自定义训练',
    description: '支持自定义模型训练，适应特定领域需求'
  },
  {
    icon: '💡',
    title: '实时预测',
    description: '提供实时API接口，支持在线情感分析服务'
  }
]

// 项目统计
const projectStats = [
  { label: '支持语言', value: '2+', desc: '中文和英文' },
  { label: '模型类型', value: '3', desc: 'TextCNN、BiLSTM、BERT' },
  { label: '数据集', value: '50K+', desc: '训练样本数量' },
  { label: '准确率', value: '93%+', desc: 'BERT模型准确率' }
]

// 开发团队信息
const teamInfo = [
  {
    name: '项目架构',
    role: '系统设计与架构',
    avatar: '🏗️',
    description: '负责整体架构设计和技术选型'
  },
  {
    name: '算法研发',
    role: '深度学习模型',
    avatar: '🧠',
    description: '负责模型训练和算法优化'
  },
  {
    name: '前端开发',
    role: '用户界面设计',
    avatar: '💻',
    description: '负责前端界面和用户体验'
  },
  {
    name: '后端开发',
    role: 'API服务开发',
    avatar: '⚙️',
    description: '负责后端服务和API接口'
  }
]

const activeTab = ref('overview')
</script>

<template>
  <div class="about-page">
    <div class="page-header">
      <h1>
        <el-icon><InfoFilled /></el-icon>
        关于项目
      </h1>
      <p>深度学习文本情感分析系统</p>
    </div>

    <el-tabs v-model="activeTab" class="about-tabs">
      <!-- 项目概览 -->
      <el-tab-pane label="项目概览" name="overview">
        <el-row :gutter="24">
          <el-col :lg="16" :md="24">
            <el-card class="overview-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <el-icon><Document /></el-icon>
                  <span>项目简介</span>
                </div>
              </template>

              <div class="project-intro">
                <h3>深度学习文本情感分析系统</h3>
                <p>
                  这是一个基于深度学习的文本情感分析系统，集成了多种主流的神经网络模型，
                  包括TextCNN、BiLSTM和BERT。系统支持中英文文本的情感倾向分析，
                  可以准确识别文本的正面、负面或中性情感。
                </p>

                <p>
                  项目采用前后端分离的架构设计，前端使用Vue 3 + TypeScript构建现代化的用户界面，
                  后端基于Flask框架提供RESTful API服务。整个系统具有良好的扩展性和可维护性，
                  适用于企业级应用场景。
                </p>

                <h4>主要特点</h4>
                <ul>
                  <li><strong>多模型支持：</strong>集成TextCNN、BiLSTM、BERT三种深度学习模型</li>
                  <li><strong>多语言支持：</strong>支持中文和英文文本情感分析</li>
                  <li><strong>高准确率：</strong>基于大规模数据集训练，BERT模型准确率可达93%+</li>
                  <li><strong>易于使用：</strong>提供友好的Web界面和简洁的API接口</li>
                  <li><strong>可扩展性：</strong>支持自定义模型训练和新语言扩展</li>
                  <li><strong>实时处理：</strong>支持单文本和批量文本的实时分析</li>
                </ul>
              </div>
            </el-card>
          </el-col>

          <el-col :lg="8" :md="24">
            <el-card class="stats-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <el-icon><DataAnalysis /></el-icon>
                  <span>项目数据</span>
                </div>
              </template>

              <div class="project-stats">
                <div
                  v-for="stat in projectStats"
                  :key="stat.label"
                  class="stat-item"
                >
                  <div class="stat-value">{{ stat.value }}</div>
                  <div class="stat-label">{{ stat.label }}</div>
                  <div class="stat-desc">{{ stat.desc }}</div>
                </div>
              </div>
            </el-card>

            <el-card class="features-card" shadow="hover" style="margin-top: 20px;">
              <template #header>
                <div class="card-header">
                  <el-icon><Star /></el-icon>
                  <span>核心功能</span>
                </div>
              </template>

              <div class="features-grid">
                <div
                  v-for="feature in features"
                  :key="feature.title"
                  class="feature-item"
                >
                  <span class="feature-icon">{{ feature.icon }}</span>
                  <div class="feature-content">
                    <h5>{{ feature.title }}</h5>
                    <p>{{ feature.description }}</p>
                  </div>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-tab-pane>

      <!-- 技术栈 -->
      <el-tab-pane label="技术栈" name="tech">
        <div class="tech-stack">
          <el-row :gutter="24">
            <el-col :md="8" :sm="24">
              <el-card class="tech-card" shadow="hover">
                <template #header>
                  <div class="card-header">
                    <el-icon style="color: #42b883;"><Monitor /></el-icon>
                    <span>前端技术</span>
                  </div>
                </template>

                <div class="tech-list">
                  <div
                    v-for="tech in techStack.frontend"
                    :key="tech.name"
                    class="tech-item"
                  >
                    <div class="tech-header">
                      <strong>{{ tech.name }}</strong>
                      <el-tag size="small">{{ tech.version }}</el-tag>
                    </div>
                    <p>{{ tech.description }}</p>
                  </div>
                </div>
              </el-card>
            </el-col>

            <el-col :md="8" :sm="24">
              <el-card class="tech-card" shadow="hover">
                <template #header>
                  <div class="card-header">
                    <el-icon style="color: #3776ab;"><Cpu /></el-icon>
                    <span>后端技术</span>
                  </div>
                </template>

                <div class="tech-list">
                  <div
                    v-for="tech in techStack.backend"
                    :key="tech.name"
                    class="tech-item"
                  >
                    <div class="tech-header">
                      <strong>{{ tech.name }}</strong>
                      <el-tag size="small" type="success">{{ tech.version }}</el-tag>
                    </div>
                    <p>{{ tech.description }}</p>
                  </div>
                </div>
              </el-card>
            </el-col>

            <el-col :md="8" :sm="24">
              <el-card class="tech-card" shadow="hover">
                <template #header>
                  <div class="card-header">
                    <el-icon style="color: #ff6b35;"><BrainFilled /></el-icon>
                    <span>AI模型</span>
                  </div>
                </template>

                <div class="tech-list">
                  <div
                    v-for="model in techStack.models"
                    :key="model.name"
                    class="tech-item"
                  >
                    <div class="tech-header">
                      <strong>{{ model.name }}</strong>
                    </div>
                    <p>{{ model.description }}</p>
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </el-tab-pane>

      <!-- 使用指南 -->
      <el-tab-pane label="使用指南" name="guide">
        <el-card class="guide-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Guide /></el-icon>
              <span>快速开始</span>
            </div>
          </template>

          <div class="guide-content">
            <el-steps :active="4" direction="vertical" finish-status="success">
              <el-step title="数据集准备" description="下载并准备训练所需的情感分析数据集">
                <template #icon>
                  <el-icon><FolderOpened /></el-icon>
                </template>
              </el-step>

              <el-step title="模型训练" description="选择合适的模型类型和参数进行训练">
                <template #icon>
                  <el-icon><Setting /></el-icon>
                </template>
              </el-step>

              <el-step title="模型部署" description="将训练好的模型部署到生产环境">
                <template #icon>
                  <el-icon><Upload /></el-icon>
                </template>
              </el-step>

              <el-step title="开始分析" description="使用Web界面或API接口进行文本情感分析">
                <template #icon>
                  <el-icon><ChatDotRound /></el-icon>
                </template>
              </el-step>
            </el-steps>

            <div class="usage-examples">
              <h4>API使用示例</h4>
              <el-code language="javascript" :code="apiExample" />

              <h4>批量分析示例</h4>
              <el-code language="python" :code="batchExample" />
            </div>
          </div>
        </el-card>
      </el-tab-pane>

      <!-- 团队信息 -->
      <el-tab-pane label="开发团队" name="team">
        <el-card class="team-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><User /></el-icon>
              <span>开发团队</span>
            </div>
          </template>

          <div class="team-grid">
            <div
              v-for="member in teamInfo"
              :key="member.name"
              class="team-member"
            >
              <div class="member-avatar">{{ member.avatar }}</div>
              <div class="member-info">
                <h4>{{ member.name }}</h4>
                <p class="member-role">{{ member.role }}</p>
                <p class="member-desc">{{ member.description }}</p>
              </div>
            </div>
          </div>

          <div class="contact-info">
            <h4>联系我们</h4>
            <el-alert
              title="项目信息"
              type="info"
              :closable="false"
              show-icon
            >
              <template #default>
                <p>如果您在使用过程中遇到问题或有改进建议，欢迎通过以下方式联系我们：</p>
                <ul>
                  <li>📧 邮箱: developer@skstudio.cn</li>
                  <li>🐛 Bug报告: 请在GitHub提交Issue</li>
                  <li>💡 功能建议: 欢迎提交Pull Request</li>
                  <li>📚 文档: 查看在线文档获取更多信息</li>
                </ul>
              </template>
            </el-alert>
          </div>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<!-- API示例代码定义 -->
<script lang="ts">
const apiExample = `// 单文本分析
fetch('http://localhost:5000/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ text: '这部电影真的很棒！' })
})
.then(response => response.json())
.then(data => console.log(data));`

const batchExample = `# Python批量分析示例
import requests

texts = [
    "这个产品质量很好",
    "服务态度太差了",
    "价格适中，性价比不错"
]

response = requests.post('http://localhost:5000/analyze/batch',
    json={'texts': texts})
results = response.json()
print(results)`

export { apiExample, batchExample }
</script>

<style scoped>
.about-page {
  width: 100%;
  padding: 0 20px;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-header h1 {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.page-header p {
  color: #606266;
  font-size: 16px;
  margin: 0;
}

.about-tabs {
  margin-bottom: 30px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-header span {
  font-weight: 600;
}

.project-intro h3 {
  color: #303133;
  margin-bottom: 16px;
}

.project-intro p {
  color: #606266;
  line-height: 1.6;
  margin-bottom: 16px;
}

.project-intro h4 {
  color: #303133;
  margin: 24px 0 12px 0;
}

.project-intro ul {
  padding-left: 20px;
}

.project-intro li {
  color: #606266;
  line-height: 1.6;
  margin-bottom: 8px;
}

.project-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.stat-item {
  text-align: center;
  padding: 20px;
  border-radius: 8px;
  background: #f8f9fa;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #409eff;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.stat-desc {
  font-size: 12px;
  color: #909399;
}

.features-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.feature-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  border-radius: 6px;
  background: #f8f9fa;
}

.feature-icon {
  font-size: 20px;
  margin-top: 2px;
}

.feature-content h5 {
  margin: 0 0 4px 0;
  color: #303133;
  font-size: 14px;
}

.feature-content p {
  margin: 0;
  color: #606266;
  font-size: 12px;
  line-height: 1.4;
}

.tech-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.tech-item {
  padding: 16px;
  border-radius: 6px;
  background: #f8f9fa;
}

.tech-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.tech-item p {
  margin: 0;
  color: #606266;
  font-size: 14px;
  line-height: 1.4;
}

.guide-content {
  padding: 20px 0;
}

.usage-examples {
  margin-top: 40px;
}

.usage-examples h4 {
  color: #303133;
  margin: 24px 0 16px 0;
}

.team-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
  margin-bottom: 40px;
}

.team-member {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 20px;
  border-radius: 8px;
  background: #f8f9fa;
}

.member-avatar {
  font-size: 32px;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #fff;
}

.member-info h4 {
  margin: 0 0 4px 0;
  color: #303133;
}

.member-role {
  margin: 0 0 8px 0;
  color: #409eff;
  font-size: 14px;
  font-weight: 600;
}

.member-desc {
  margin: 0;
  color: #606266;
  font-size: 14px;
  line-height: 1.4;
}

.contact-info h4 {
  color: #303133;
  margin: 0 0 16px 0;
}

.contact-info ul {
  margin: 12px 0 0 0;
  padding-left: 20px;
}

.contact-info li {
  color: #606266;
  line-height: 1.6;
  margin-bottom: 8px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .project-stats {
    grid-template-columns: 1fr;
  }

  .team-grid {
    grid-template-columns: 1fr;
  }

  .team-member {
    flex-direction: column;
    text-align: center;
  }
}
</style>
