<!-- 首页组件 -->
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useSentimentStore } from '@/stores/sentiment'
import { useRouter } from 'vue-router'

const router = useRouter()
const sentimentStore = useSentimentStore()
const systemStatus = ref({
  backend: false,
  models: 0,
  datasets: 0
})

// 快速操作菜单
const quickActions = [
  {
    title: '情感分析',
    description: '输入文本进行实时情感分析',
    icon: 'ChatDotRound',
    color: '#409eff',
    route: '/analyze'
  },
  {
    title: '下载数据集',
    description: '下载中文和英文情感分析数据集',
    icon: 'Download',
    color: '#67c23a',
    route: '/dataset'
  },
  {
    title: '训练模型',
    description: '使用深度学习模型进行训练',
    icon: 'Setting',
    color: '#e6a23c',
    route: '/training'
  },
  {
    title: '模型管理',
    description: '查看和管理已训练的模型',
    icon: 'Box',
    color: '#f56c6c',
    route: '/models'
  }
]

// 系统功能特点
const features = [
  {
    title: 'TextCNN',
    description: '卷积神经网络，适合短文本特征提取',
    icon: 'Grid'
  },
  {
    title: 'BiLSTM',
    description: '双向LSTM，捕捉上下文语义序列关系',
    icon: 'Share'
  },
  {
    title: 'BERT',
    description: '基于Transformer的预训练语言模型',
    icon: 'Star'
  },
  {
    title: '多语言支持',
    description: '支持中文和英文文本情感分析',
    icon: 'Globe'
  }
]

// 获取系统状态
const getSystemStatus = async () => {
  try {
    systemStatus.value.backend = await sentimentStore.healthCheck()

    if (systemStatus.value.backend) {
      await sentimentStore.fetchTrainedModels()
      await sentimentStore.fetchDatasetsInfo()

      systemStatus.value.models = sentimentStore.trainedModels.length
      systemStatus.value.datasets = sentimentStore.datasetsInfo?.available_datasets?.length || 0
    }
  } catch (error) {
    console.error('获取系统状态失败:', error)
  }
}

onMounted(() => {
  getSystemStatus()
})

// 处理快速操作点击
const handleQuickAction = (route: string) => {
  router.push(route)
}
</script>

<template>
  <div class="home-page">
    <!-- 欢迎区域 -->
    <el-card class="welcome-card" shadow="hover">
      <div class="welcome-content">
        <div class="welcome-text">
          <h1 class="welcome-title">
            <el-icon size="32"><BrainFilled /></el-icon>
            欢迎使用深度学习文本情感分析系统
          </h1>
          <p class="welcome-description">
            基于PyTorch构建的深度学习情感分析平台，支持TextCNN、BiLSTM、BERT等多种模型，
            提供中英文文本情感分析能力，适用于评论分析、舆情监控等应用场景。
          </p>

          <!-- 系统状态 -->
          <div class="status-indicators">
            <el-tag
              :type="systemStatus.backend ? 'success' : 'danger'"
              size="large"
              effect="dark"
            >
              <el-icon><Connection /></el-icon>
              后端服务: {{ systemStatus.backend ? '正常' : '异常' }}
            </el-tag>
            <el-tag type="info" size="large" effect="dark">
              <el-icon><Box /></el-icon>
              已训练模型: {{ systemStatus.models }}
            </el-tag>
            <el-tag type="warning" size="large" effect="dark">
              <el-icon><FolderOpened /></el-icon>
              可用数据集: {{ systemStatus.datasets }}
            </el-tag>
          </div>
        </div>

        <div class="welcome-actions">
          <el-button
            type="primary"
            size="large"
            @click="$router.push('/analyze')"
          >
            <el-icon><ChatDotRound /></el-icon>
            开始分析
          </el-button>
          <el-button
            size="large"
            @click="$router.push('/about')"
          >
            <el-icon><InfoFilled /></el-icon>
            了解更多
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 快速操作 -->
    <div class="quick-actions">
      <h2 class="section-title">快速操作</h2>
      <el-row :gutter="24">
        <el-col
          v-for="action in quickActions"
          :key="action.title"
          :xs="24" :sm="12" :md="6" :lg="6" :xl="4"
        >
          <el-card
            class="action-card"
            shadow="hover"
            @click="handleQuickAction(action.route)"
          >
            <div class="action-content">
              <div class="action-icon" :style="{ backgroundColor: action.color }">
                <el-icon size="28">
                  <component :is="action.icon" />
                </el-icon>
              </div>
              <h3 class="action-title">{{ action.title }}</h3>
              <p class="action-description">{{ action.description }}</p>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 系统特性 -->
    <div class="features-section">
      <h2 class="section-title">系统特性</h2>
      <el-row :gutter="24">
        <el-col
          v-for="feature in features"
          :key="feature.title"
          :xs="24" :sm="12" :md="6" :lg="6" :xl="4"
        >
          <el-card class="feature-card" shadow="hover">
            <div class="feature-content">
              <div class="feature-icon">
                <el-icon size="32">
                  <component :is="feature.icon" />
                </el-icon>
              </div>
              <h3 class="feature-title">{{ feature.title }}</h3>
              <p class="feature-description">{{ feature.description }}</p>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 使用流程 -->
    <div class="workflow-section">
      <h2 class="section-title">使用流程</h2>
      <el-card shadow="hover">
        <el-steps
          :active="0"
          align-center
          finish-status="success"
          process-status="primary"
        >
          <el-step title="下载数据集" description="获取中文或英文情感分析数据集">
            <template #icon>
              <el-icon><Download /></el-icon>
            </template>
          </el-step>
          <el-step title="训练模型" description="选择模型类型进行训练">
            <template #icon>
              <el-icon><Setting /></el-icon>
            </template>
          </el-step>
          <el-step title="情感分析" description="使用训练好的模型进行分析">
            <template #icon>
              <el-icon><ChatDotRound /></el-icon>
            </template>
          </el-step>
          <el-step title="查看结果" description="获取详细的分析结果和置信度">
            <template #icon>
              <el-icon><DataAnalysis /></el-icon>
            </template>
          </el-step>
        </el-steps>
      </el-card>
    </div>
  </div>
</template>

<style scoped>
.home-page {
  width: 100%;
  padding: 0 20px;
}

.welcome-card {
  margin-bottom: 40px;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.welcome-card :deep(.el-card__body) {
  padding: 40px;
}

.welcome-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 40px;
  width: 100%;
}

.welcome-text {
  flex: 1;
}

.welcome-title {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 16px 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.welcome-description {
  font-size: 16px;
  line-height: 1.6;
  margin-bottom: 24px;
  opacity: 0.9;
}

.status-indicators {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.welcome-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.section-title {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 24px;
  color: #303133;
  text-align: center;
}

.quick-actions {
  margin-bottom: 40px;
}

.action-card {
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 8px;
  margin-bottom: 20px;
}

.action-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.action-content {
  text-align: center;
  padding: 20px;
}

.action-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
  color: white;
}

.action-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
  color: #303133;
}

.action-description {
  font-size: 14px;
  color: #606266;
  margin: 0;
}

.features-section {
  margin-bottom: 40px;
}

.feature-card {
  border-radius: 8px;
  margin-bottom: 20px;
}

.feature-content {
  text-align: center;
  padding: 20px;
}

.feature-icon {
  color: #409eff;
  margin-bottom: 16px;
}

.feature-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
  color: #303133;
}

.feature-description {
  font-size: 14px;
  color: #606266;
  margin: 0;
}

.workflow-section {
  margin-bottom: 40px;
}

.workflow-section .el-card {
  border-radius: 8px;
  padding: 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .welcome-content {
    flex-direction: column;
    text-align: center;
  }

  .welcome-title {
    font-size: 24px;
    justify-content: center;
  }

  .welcome-actions {
    flex-direction: row;
    justify-content: center;
  }

  .status-indicators {
    justify-content: center;
  }
}
</style>
