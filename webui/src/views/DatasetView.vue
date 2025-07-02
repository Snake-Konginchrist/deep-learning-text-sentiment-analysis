<!-- 数据集管理页面 -->
<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useSentimentStore } from '@/stores/sentiment'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Check, FolderOpened, Download, Refresh, Close, DataAnalysis } from '@element-plus/icons-vue'

const sentimentStore = useSentimentStore()

// 响应式数据
const selectedLanguage = ref('chinese')
const maxSamples = ref(10000)
const showAdvanced = ref(false)

// 数据集配置
const datasetConfigs = {
  chinese: {
    name: 'ChnSentiCorp',
    description: '中文情感分析数据集，包含酒店、书籍、餐饮等领域的评论数据',
    size: '约12,000条',
    source: 'Hugging Face + Kaggle备用',
    languages: ['中文'],
    domains: ['酒店评论', '书籍评论', '餐饮评论'],
    format: 'text, label',
    icon: '🇨🇳',
    sources: ['Hugging Face (主)', 'Kaggle ChnSentiCorp (备用)', 'GitHub (备用)']
  },
  english: {
    name: 'IMDb Movie Reviews',
    description: '英文电影评论情感分析数据集，包含正面和负面电影评论',
    size: '50,000条',
    source: 'Hugging Face + Kaggle备用',
    languages: ['English'],
    domains: ['电影评论'],
    format: 'text, label',
    icon: '🇺🇸',
    sources: ['Hugging Face (主)', 'Kaggle API (备用)']
  }
}

// 计算属性
const currentDataset = computed(() => {
  return datasetConfigs[selectedLanguage.value as keyof typeof datasetConfigs]
})

const isDownloading = computed(() => sentimentStore.isDownloading)
const downloadProgress = computed(() => sentimentStore.downloadStatus.progress)
const downloadMessage = computed(() => sentimentStore.downloadStatus.message)

// 开始下载数据集
const startDownload = async () => {
  try {
    const confirmed = await ElMessageBox.confirm(
      `确定要下载 ${currentDataset.value.name} 数据集吗？\n数据量: ${currentDataset.value.size}`,
      '确认下载',
      {
        confirmButtonText: '开始下载',
        cancelButtonText: '取消',
        type: 'info'
      }
    )

    if (confirmed) {
      const success = await sentimentStore.downloadDataset(
        selectedLanguage.value,
        showAdvanced.value ? maxSamples.value : undefined
      )

      if (success) {
        ElMessage.success('数据集下载已启动')
      }
    }
  } catch (error) {
    // 用户取消操作
  }
}

// 停止下载
const stopDownload = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要停止下载吗？已下载的数据将保留。',
      '确认停止',
      {
        confirmButtonText: '停止下载',
        cancelButtonText: '继续下载',
        type: 'warning'
      }
    )
    // TODO: 实现停止下载功能
    ElMessage.warning('停止下载功能待实现')
  } catch (error) {
    // 用户取消操作
  }
}

// 刷新数据集信息
const refreshDatasets = async () => {
  const success = await sentimentStore.fetchDatasetsInfo()
  if (success) {
    ElMessage.success('数据集信息已刷新')
  } else {
    ElMessage.error('刷新失败')
  }
}

// 格式化文件大小
const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 获取数据集状态
const getDatasetStatus = (language: string) => {
  // 从后端API数据中查找对应语言的数据集状态
  const dataset = sentimentStore.datasetsInfo?.available_datasets?.find(
    (d: any) => d.language === language
  )

  if (dataset?.downloaded) {
    return { type: 'success', text: '已下载' }
  } else {
    return { type: 'info', text: '待下载' }
  }
}

onMounted(() => {
  // 获取数据集信息
  sentimentStore.fetchDatasetsInfo()
})
</script>

<template>
  <div class="dataset-page">
    <div class="page-header">
      <h1>
        <el-icon><FolderOpened /></el-icon>
        数据集管理
      </h1>
      <p>下载和管理训练所需的情感分析数据集</p>
    </div>

    <el-row :gutter="24" style="margin-bottom: 40px;">
      <!-- 数据集选择和下载 -->
      <el-col :xl="18" :lg="16" :md="24">
        <el-card class="dataset-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Download /></el-icon>
              <span>数据集下载</span>
              <el-button size="small" @click="refreshDatasets">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </template>

          <!-- 数据集选择 -->
          <div class="dataset-selection">
            <h3>选择数据集</h3>
            <div class="dataset-cards">
              <div
                v-for="(config, key) in datasetConfigs"
                :key="key"
                class="dataset-card-item"
                :class="{ active: selectedLanguage === key }"
                @click="selectedLanguage = key"
              >
                <div class="card-content">
                  <div class="card-header-section">
                    <span class="dataset-icon">{{ config.icon }}</span>
                    <strong>{{ config.name }}</strong>
                    <el-tag
                      size="small"
                      :type="getDatasetStatus(key).type"
                      class="status-tag"
                    >
                      {{ getDatasetStatus(key).text }}
                    </el-tag>
                  </div>
                  <div class="card-description">{{ config.description }}</div>
                  <div class="card-meta">
                    <el-tag size="small">{{ config.size }}</el-tag>
                    <el-tag size="small" type="info">{{ config.source }}</el-tag>
                  </div>
                  <div class="card-details">
                    <div class="detail-row">
                      <span class="detail-label">语言:</span>
                      <span class="detail-value">{{ config.languages.join(', ') }}</span>
                    </div>
                    <div class="detail-row">
                      <span class="detail-label">领域:</span>
                      <span class="detail-value">{{ config.domains.join(', ') }}</span>
                    </div>
                    <div class="detail-row">
                      <span class="detail-label">数据源:</span>
                      <div class="sources-list">
                        <el-tag
                          v-for="source in config.sources"
                          :key="source"
                          size="mini"
                          :type="source.includes('主') ? 'primary' : 'info'"
                          class="source-tag"
                        >
                          {{ source }}
                        </el-tag>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="selection-indicator">
                  <el-icon v-if="selectedLanguage === key"><Check /></el-icon>
                </div>
              </div>
            </div>
          </div>

          <!-- 当前选中数据集详情 -->
          <div class="dataset-details">
            <h3>数据集详情</h3>
            <el-descriptions :column="2" border>
              <el-descriptions-item label="数据集名称">
                <span class="dataset-icon">{{ currentDataset.icon }}</span>
                {{ currentDataset.name }}
              </el-descriptions-item>
              <el-descriptions-item label="数据量">
                {{ currentDataset.size }}
              </el-descriptions-item>
              <el-descriptions-item label="数据源">
                {{ currentDataset.source }}
              </el-descriptions-item>
              <el-descriptions-item label="数据格式">
                {{ currentDataset.format }}
              </el-descriptions-item>
              <el-descriptions-item label="支持语言" :span="2">
                <el-tag
                  v-for="lang in currentDataset.languages"
                  :key="lang"
                  size="small"
                  style="margin-right: 8px;"
                >
                  {{ lang }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="应用领域" :span="2">
                <el-tag
                  v-for="domain in currentDataset.domains"
                  :key="domain"
                  size="small"
                  type="success"
                  style="margin-right: 8px;"
                >
                  {{ domain }}
                </el-tag>
              </el-descriptions-item>
            </el-descriptions>
          </div>

          <!-- 高级配置 -->
          <el-collapse v-model="showAdvanced" class="advanced-config">
            <el-collapse-item title="高级配置" name="advanced">
              <el-form label-width="120px" size="default">
                <el-form-item label="最大样本数">
                  <el-input-number
                    v-model="maxSamples"
                    :min="1000"
                    :max="100000"
                    :step="1000"
                    controls-position="right"
                    style="width: 200px;"
                  />
                  <div class="form-tip">
                    限制下载的样本数量，用于快速测试。设置为0表示下载全部数据。
                  </div>
                </el-form-item>
              </el-form>
            </el-collapse-item>
          </el-collapse>

          <!-- 下载控制 -->
          <div class="download-controls">
            <el-button
              v-if="!isDownloading"
              type="primary"
              size="large"
              @click="startDownload"
            >
              <el-icon><Download /></el-icon>
              开始下载
            </el-button>
            <el-button
              v-else
              type="danger"
              size="large"
              @click="stopDownload"
            >
              <el-icon><Close /></el-icon>
              停止下载
            </el-button>
          </div>

          <!-- 下载进度 -->
          <div v-if="isDownloading" class="download-progress">
            <h4>下载进度</h4>
            <el-progress
              :percentage="downloadProgress"
              :format="(percentage: number) => `${percentage}%`"
              :stroke-width="12"
              status="active"
            />
            <div class="progress-text">
              {{ downloadMessage || '正在下载...' }}
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 数据集状态和统计 -->
      <el-col :xl="6" :lg="8" :md="24">
        <el-card class="status-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><DataAnalysis /></el-icon>
              <span>数据集状态</span>
            </div>
          </template>

          <!-- 下载状态概览 -->
          <div class="status-overview">
            <div class="status-item">
              <div class="status-label">当前状态</div>
              <el-tag
                :type="isDownloading ? 'warning' : 'success'"
                size="large"
              >
                {{ isDownloading ? '下载中' : '就绪' }}
              </el-tag>
            </div>

            <div class="status-item">
              <div class="status-label">可用数据集</div>
              <div class="status-value">
                {{ Object.keys(datasetConfigs).length }} 个
              </div>
            </div>

            <div class="status-item">
              <div class="status-label">存储位置</div>
              <div class="status-value">
                <el-text type="info" size="small">
                  {{ sentimentStore.datasetsInfo?.data_directory || 'datasets/' }}
                </el-text>
              </div>
            </div>
          </div>

          <!-- 数据集列表 -->
          <div class="datasets-list">
            <h4>数据集状态</h4>
            <div class="datasets-grid">
              <div
                v-for="(config, key) in datasetConfigs"
                :key="key"
                class="dataset-item"
              >
                <div class="dataset-header">
                  <span class="dataset-icon">{{ config.icon }}</span>
                  <strong>{{ config.name }}</strong>
                </div>
                <div class="dataset-status">
                  <el-tag
                    size="small"
                    :type="getDatasetStatus(key).type"
                  >
                    {{ getDatasetStatus(key).text }}
                  </el-tag>
                </div>
              </div>
            </div>
          </div>

          <!-- 使用说明 -->
          <div class="usage-tips">
            <h4>使用说明</h4>
            <el-alert
              title="数据集说明"
              type="info"
              :closable="false"
              show-icon
            >
              <template #default>
                <ul>
                  <li>中文数据集适用于中文文本情感分析</li>
                  <li>英文数据集适用于英文文本情感分析</li>
                  <li>下载完成后可在模型训练页面使用</li>
                  <li>建议先下载小规模数据进行测试</li>
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
.dataset-page {
  width: 100%;
  padding: 0 20px;
  min-height: 100vh;
  overflow-x: hidden;
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

.dataset-card {
  margin-bottom: 20px;
}

.status-card {
  position: relative;
  z-index: 1;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.card-header span {
  font-weight: 600;
}

.dataset-selection {
  margin-bottom: 30px;
}

.dataset-selection h3 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
  color: #303133;
}

.dataset-cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 20px;
}

.dataset-card-item {
  position: relative;
  border: 2px solid #ebeef5;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #ffffff;
  min-height: 200px;
}

.dataset-card-item:hover {
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
  transform: translateY(-2px);
}

.dataset-card-item.active {
  border-color: #409eff;
  background: linear-gradient(135deg, #f8fbff 0%, #e6f4ff 100%);
  box-shadow: 0 4px 16px rgba(64, 158, 255, 0.2);
}

.card-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.card-header-section {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}

.dataset-icon {
  font-size: 24px;
}

.status-tag {
  margin-left: auto;
}

.card-description {
  color: #606266;
  font-size: 14px;
  line-height: 1.5;
  flex: 1;
}

.card-meta {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.card-details {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
  font-size: 12px;
}

.detail-label {
  color: #909399;
  font-weight: 500;
}

.detail-value {
  color: #606266;
}

.sources-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 4px;
}

.source-tag {
  margin-right: 4px;
}

.selection-indicator {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #409eff;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: all 0.3s ease;
}

.dataset-card-item.active .selection-indicator {
  opacity: 1;
}

.dataset-details {
  margin-bottom: 30px;
}

.dataset-details h3 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
  color: #303133;
}

.advanced-config {
  margin-bottom: 30px;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.download-controls {
  text-align: center;
  margin-bottom: 30px;
}

.download-progress h4 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
  color: #303133;
}

.progress-text {
  text-align: center;
  color: #606266;
  font-size: 14px;
  margin-top: 8px;
}

.status-overview {
  margin-bottom: 30px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.status-item:last-child {
  border-bottom: none;
}

.status-label {
  font-weight: 600;
  color: #303133;
}

.status-value {
  font-size: 18px;
  font-weight: 600;
  color: #409eff;
}

.datasets-list h4 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
  color: #303133;
}

.datasets-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 30px;
}

.dataset-item {
  padding: 12px;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  background: #fafafa;
}

.dataset-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.dataset-status {
  text-align: right;
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
@media (max-width: 1200px) {
  .dataset-cards {
    gap: 16px;
  }

  .dataset-card-item {
    min-height: 180px;
    padding: 16px;
  }
}

@media (max-width: 768px) {
  .dataset-page {
    padding: 0 10px;
  }

  .dataset-cards {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .dataset-card-item {
    min-height: 160px;
    padding: 16px;
  }

  .card-header-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .status-tag {
    margin-left: 0;
    align-self: flex-start;
  }

  .status-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .status-card {
    margin-top: 20px;
  }

  .selection-indicator {
    top: 8px;
    right: 8px;
    width: 20px;
    height: 20px;
  }
}
</style>
