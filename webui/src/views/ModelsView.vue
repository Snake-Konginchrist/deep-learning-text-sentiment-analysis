<!-- 模型管理页面 -->
<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useSentimentStore } from '@/stores/sentiment'
import { ElMessage, ElMessageBox } from 'element-plus'

// 模型接口定义
interface TrainedModel {
  id: string
  name: string
  type: string
  language: string
  accuracy?: number
  size?: string
  trainDate?: string
  status: string
  description?: string
}

const sentimentStore = useSentimentStore()

// 响应式数据
const selectedModel = ref('')
const modelSearchText = ref('')

// 已训练模型数据（从后端API获取）
const trainedModels = ref<TrainedModel[]>([])

// 模型类型配置
const modelTypeConfigs = {
  textcnn: {
    name: 'TextCNN',
    icon: '🔍',
    color: '#409eff'
  },
  bilstm: {
    name: 'BiLSTM',
    icon: '🔄',
    color: '#67c23a'
  },
  bert: {
    name: 'BERT',
    icon: '🧠',
    color: '#e6a23c'
  }
}

const languageConfigs = {
  chinese: {
    name: '中文',
    icon: '🇨🇳'
  },
  english: {
    name: 'English',
    icon: '🇺🇸'
  }
}

// 计算属性
const filteredModels = computed(() => {
  if (!modelSearchText.value) return trainedModels.value

  return trainedModels.value.filter(model =>
    model.name.toLowerCase().includes(modelSearchText.value.toLowerCase()) ||
    model.type.toLowerCase().includes(modelSearchText.value.toLowerCase()) ||
    model.language.toLowerCase().includes(modelSearchText.value.toLowerCase())
  )
})

const modelStats = computed(() => {
  const total = trainedModels.value.length
  const ready = trainedModels.value.filter(m => m.status === 'ready').length
  const training = trainedModels.value.filter(m => m.status === 'training').length

  return { total, ready, training }
})

// 获取模型类型配置
const getModelTypeConfig = (type: string) => {
  return modelTypeConfigs[type as keyof typeof modelTypeConfigs] || {
    name: type,
    icon: '📦',
    color: '#909399'
  }
}

// 获取语言配置
const getLanguageConfig = (language: string) => {
  return languageConfigs[language as keyof typeof languageConfigs] || {
    name: language,
    icon: '🌐'
  }
}

// 获取状态标签类型
const getStatusType = (status: string) => {
  const types = {
    ready: 'success',
    training: 'warning',
    error: 'danger',
    loading: 'info'
  }
  return types[status as keyof typeof types] || 'info'
}

// 获取状态文本
const getStatusText = (status: string) => {
  const texts = {
    ready: '就绪',
    training: '训练中',
    error: '错误',
    loading: '加载中'
  }
  return texts[status as keyof typeof texts] || status
}

// 切换模型
const switchModel = async (model: any) => {
  try {
    const confirmed = await ElMessageBox.confirm(
      `确定要切换到 ${model.name} 模型吗？`,
      '确认切换模型',
      {
        confirmButtonText: '切换',
        cancelButtonText: '取消',
        type: 'info'
      }
    )

    if (confirmed) {
      // 调用后端API加载模型
      const success = await sentimentStore.loadModel({
        model_type: model.type,
        language: model.language
      })

      if (success) {
        selectedModel.value = model.id
        ElMessage.success(`已成功加载 ${model.name}`)
        // 刷新当前模型状态
        await sentimentStore.fetchCurrentModel()
      } else {
        ElMessage.error(sentimentStore.error || '加载模型失败')
      }
    }
  } catch (error) {
    // 用户取消操作或其他错误
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

// 删除模型
const deleteModel = async (model: any) => {
  try {
    const confirmed = await ElMessageBox.confirm(
      `确定要删除 ${model.name} 模型吗？此操作不可撤销。`,
      '确认删除模型',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    if (confirmed) {
      // 获取原始模型文件名
      const originalModel = sentimentStore.trainedModels.find(m =>
        m.model_type === model.type && m.language === model.language
      )

      if (!originalModel) {
        ElMessage.error('找不到对应的模型文件')
        return
      }

      // 调用后端API删除模型
      const success = await sentimentStore.deleteModel(originalModel.filename)

      if (success) {
        // 从本地列表中移除
        const index = trainedModels.value.findIndex(m => m.id === model.id)
        if (index > -1) {
          trainedModels.value.splice(index, 1)
        }

        ElMessage.success(`已成功删除 ${model.name}`)

        // 如果删除的是当前选中的模型，清除选中状态
        if (selectedModel.value === model.id) {
          selectedModel.value = ''
        }
      } else {
        ElMessage.error(sentimentStore.error || '删除模型失败')
      }
    }
  } catch (error) {
    // 用户取消操作或其他错误
    if (error !== 'cancel') {
      ElMessage.error('删除操作失败')
    }
  }
}

// 下载模型
const downloadModel = (model: any) => {
  ElMessage.info('模型下载功能待实现')
}

// 查看模型详情
const viewModelDetails = (model: any) => {
  ElMessageBox.alert(
    `模型类型: ${getModelTypeConfig(model.type).name}\n` +
    `训练语言: ${getLanguageConfig(model.language).name}\n` +
    `准确率: ${(model.accuracy * 100).toFixed(1)}%\n` +
    `模型大小: ${model.size}\n` +
    `训练日期: ${model.trainDate}\n` +
    `描述: ${model.description}`,
    model.name,
    {
      confirmButtonText: '确定'
    }
  )
}

// 格式化日期
const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

// 格式化文件大小
const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 加载模型列表
const loadModels = async () => {
  try {
    // 从后端API获取模型文件列表
    const success = await sentimentStore.fetchTrainedModelFiles()
    if (success && sentimentStore.trainedModels) {
      trainedModels.value = sentimentStore.trainedModels.map((model: any) => ({
        id: model.filename?.replace('.pth', '') || `${model.model_type}_${model.language}`,
        name: `${getModelTypeConfig(model.model_type).name}${getLanguageConfig(model.language).name}模型`,
        type: model.model_type,
        language: model.language,
        size: formatFileSize(model.size || 0),
        trainDate: model.created_time ? new Date(model.created_time * 1000).toISOString().split('T')[0] : undefined,
        status: 'ready',
        description: `基于${getModelTypeConfig(model.model_type).name}的${getLanguageConfig(model.language).name}情感分析模型`
      }))
    }

    // 获取当前加载的模型状态
    await sentimentStore.fetchCurrentModel()

    // 设置选中的模型（如果有的话）
    if (sentimentStore.currentModel.model_loaded && sentimentStore.currentModel.model_type) {
      const currentModelId = `${sentimentStore.currentModel.model_type}_${sentimentStore.currentModel.language}`
      const currentModel = trainedModels.value.find(m => m.id === currentModelId)
      if (currentModel) {
        selectedModel.value = currentModel.id
      }
    }
  } catch (error) {
    console.error('加载模型列表失败:', error)
    ElMessage.error('加载模型列表失败')
  }
}

onMounted(() => {
  // 加载模型列表
  loadModels()
})
</script>

<template>
  <div class="models-page">
    <div class="page-header">
      <h1>
        <el-icon><Box /></el-icon>
        模型管理
      </h1>
      <p>管理和切换训练好的情感分析模型</p>
    </div>

    <!-- 模型统计 -->
    <div class="models-stats">
      <el-row :gutter="24">
        <el-col :span="8">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-value">{{ modelStats.total }}</div>
              <div class="stat-label">总模型数</div>
            </div>
            <el-icon class="stat-icon"><Box /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card class="stat-card ready">
            <div class="stat-content">
              <div class="stat-value">{{ modelStats.ready }}</div>
              <div class="stat-label">可用模型</div>
            </div>
            <el-icon class="stat-icon"><CircleCheck /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card class="stat-card training">
            <div class="stat-content">
              <div class="stat-value">{{ modelStats.training }}</div>
              <div class="stat-label">训练中</div>
            </div>
            <el-icon class="stat-icon"><Loading /></el-icon>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <el-row :gutter="24">
      <!-- 模型列表 -->
      <el-col :lg="16" :md="24">
        <el-card class="models-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <div class="header-left">
                <el-icon><List /></el-icon>
                <span>模型列表</span>
              </div>
              <div class="header-right">
                <el-input
                  v-model="modelSearchText"
                  placeholder="搜索模型..."
                  size="small"
                  clearable
                  style="width: 200px;"
                >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>
              </div>
            </div>
          </template>

          <!-- 模型网格 -->
          <div class="models-grid">
            <div
              v-for="model in filteredModels"
              :key="model.id"
              class="model-card"
              :class="{ active: selectedModel === model.id }"
            >
              <div class="model-header">
                <div class="model-title">
                  <span
                    class="model-type-icon"
                    :style="{ color: getModelTypeConfig(model.type).color }"
                  >
                    {{ getModelTypeConfig(model.type).icon }}
                  </span>
                  <strong>{{ model.name }}</strong>
                </div>
                <el-tag
                  :type="getStatusType(model.status)"
                  size="small"
                >
                  {{ getStatusText(model.status) }}
                </el-tag>
              </div>

              <div class="model-info">
                <div class="info-row">
                  <span class="info-label">类型:</span>
                  <span>{{ getModelTypeConfig(model.type).name }}</span>
                </div>
                <div class="info-row">
                  <span class="info-label">语言:</span>
                  <span>
                    {{ getLanguageConfig(model.language).icon }}
                    {{ getLanguageConfig(model.language).name }}
                  </span>
                </div>
                <div class="info-row" v-if="model.accuracy">
                  <span class="info-label">准确率:</span>
                  <span class="accuracy">{{ (model.accuracy * 100).toFixed(1) }}%</span>
                </div>
                <div class="info-row" v-if="model.size">
                  <span class="info-label">大小:</span>
                  <span>{{ model.size }}</span>
                </div>
                <div class="info-row" v-if="model.trainDate">
                  <span class="info-label">训练日期:</span>
                  <span>{{ formatDate(model.trainDate) }}</span>
                </div>
              </div>

              <div class="model-actions">
                <el-button
                  v-if="model.status === 'ready' && selectedModel !== model.id"
                  type="primary"
                  size="small"
                  @click="switchModel(model)"
                >
                  切换使用
                </el-button>
                <el-button
                  v-if="selectedModel === model.id"
                  type="success"
                  size="small"
                  disabled
                >
                  当前使用
                </el-button>
                <el-button
                  size="small"
                  @click="viewModelDetails(model)"
                >
                  详情
                </el-button>
                <el-button
                  size="small"
                  @click="downloadModel(model)"
                >
                  下载
                </el-button>
                <el-button
                  type="danger"
                  size="small"
                  @click="deleteModel(model)"
                >
                  删除
                </el-button>
              </div>
            </div>
          </div>

          <!-- 空状态 -->
          <el-empty
            v-if="filteredModels.length === 0"
            description="暂无模型"
            :image-size="120"
          >
            <el-text type="info">请先在训练页面训练模型</el-text>
          </el-empty>
        </el-card>
      </el-col>

      <!-- 当前模型信息 -->
      <el-col :lg="8" :md="24">
        <el-card class="current-model-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Setting /></el-icon>
              <span>当前模型</span>
            </div>
          </template>

          <div v-if="selectedModel" class="current-model">
            <div
              v-for="model in trainedModels.filter(m => m.id === selectedModel)"
              :key="model.id"
              class="model-detail"
            >
              <div class="model-avatar">
                <span
                  class="avatar-icon"
                  :style="{ color: getModelTypeConfig(model.type).color }"
                >
                  {{ getModelTypeConfig(model.type).icon }}
                </span>
              </div>

              <div class="model-meta">
                <h3>{{ model.name }}</h3>
                <p>{{ model.description }}</p>
              </div>

              <el-descriptions :column="1" border size="small">
                <el-descriptions-item label="模型类型">
                  {{ getModelTypeConfig(model.type).name }}
                </el-descriptions-item>
                <el-descriptions-item label="训练语言">
                  {{ getLanguageConfig(model.language).icon }}
                  {{ getLanguageConfig(model.language).name }}
                </el-descriptions-item>
                <el-descriptions-item label="准确率" v-if="model.accuracy">
                  <el-progress
                    :percentage="model.accuracy * 100"
                    :stroke-width="8"
                    :show-text="true"
                    :format="() => `${(model.accuracy! * 100).toFixed(1)}%`"
                  />
                </el-descriptions-item>
                <el-descriptions-item label="模型大小">
                  {{ model.size }}
                </el-descriptions-item>
                <el-descriptions-item label="训练日期" v-if="model.trainDate">
                  {{ formatDate(model.trainDate) }}
                </el-descriptions-item>
                <el-descriptions-item label="状态">
                  <el-tag
                    :type="getStatusType(model.status)"
                    size="small"
                  >
                    {{ getStatusText(model.status) }}
                  </el-tag>
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </div>

          <el-empty
            v-else
            description="未选择模型"
            :image-size="80"
          >
            <el-text type="info">请选择一个模型</el-text>
          </el-empty>

          <!-- 模型操作提示 -->
          <div class="usage-tips">
            <h4>操作说明</h4>
            <el-alert
              title="模型管理"
              type="info"
              :closable="false"
              show-icon
            >
              <template #default>
                <ul>
                  <li>切换模型后在分析页面即可使用新模型</li>
                  <li>删除模型前请确认已备份重要模型</li>
                  <li>准确率仅供参考，实际效果可能因数据而异</li>
                  <li>BERT模型体积较大但效果最佳</li>
                </ul>
              </template>
            </el-alert>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.models-page {
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

.models-stats {
  margin-bottom: 30px;
}

.stat-card {
  text-align: center;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-card.ready {
  border-color: #67c23a;
}

.stat-card.training {
  border-color: #e6a23c;
}

.stat-content {
  padding: 20px;
}

.stat-value {
  font-size: 32px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.stat-label {
  color: #606266;
  font-size: 14px;
}

.stat-icon {
  position: absolute;
  top: 20px;
  right: 20px;
  font-size: 32px;
  color: #e4e7ed;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-left span {
  font-weight: 600;
}

.models-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
}

.model-card {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 20px;
  transition: all 0.3s ease;
  background: #fff;
}

.model-card:hover {
  border-color: #409eff;
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.1);
}

.model-card.active {
  border-color: #67c23a;
  background: linear-gradient(135deg, #f0f9ff 0%, #ecf5ff 100%);
}

.model-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.model-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.model-type-icon {
  font-size: 20px;
}

.model-info {
  margin-bottom: 16px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.info-label {
  color: #606266;
  font-size: 14px;
}

.accuracy {
  color: #67c23a;
  font-weight: 600;
}

.model-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.current-model {
  margin-bottom: 30px;
}

.model-detail {
  text-align: center;
  margin-bottom: 20px;
}

.model-avatar {
  margin-bottom: 16px;
}

.avatar-icon {
  font-size: 48px;
  padding: 20px;
  border-radius: 50%;
  background: #f5f7fa;
  display: inline-block;
}

.model-meta h3 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
  color: #303133;
}

.model-meta p {
  color: #606266;
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 20px;
}

.usage-tips {
  margin-top: 30px;
}

.usage-tips h4 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
  color: #303133;
}

.usage-tips ul {
  margin: 0;
  padding-left: 20px;
}

.usage-tips li {
  margin-bottom: 8px;
  color: #606266;
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .models-grid {
    grid-template-columns: 1fr;
  }

  .model-actions {
    justify-content: center;
  }

  .card-header {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }
}
</style>
