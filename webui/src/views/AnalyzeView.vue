<!-- 情感分析页面 -->
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useSentimentStore } from '@/stores/sentiment'
import { ElMessage } from 'element-plus'

const sentimentStore = useSentimentStore()

// 响应式数据
const inputText = ref('')
const batchTexts = ref('')
const activeTab = ref('single')
const showAdvanced = ref(false)

// 批量分析配置
const batchConfig = ref({
  batchSize: 10,
  separator: '\n'
})

// 计算属性
const canAnalyze = computed(() => {
  if (activeTab.value === 'single') {
    return inputText.value.trim().length > 0
  } else {
    return batchTexts.value.trim().length > 0
  }
})

const parsedBatchTexts = computed(() => {
  if (!batchTexts.value.trim()) return []
  return batchTexts.value
    .split(batchConfig.value.separator)
    .map(text => text.trim())
    .filter(text => text.length > 0)
})

// 情感标签配置
const sentimentLabels = {
  positive: { label: '正面', color: '#67c23a', icon: 'CircleCheck' },
  negative: { label: '负面', color: '#f56c6c', icon: 'CircleClose' },
  neutral: { label: '中性', color: '#909399', icon: 'Remove' }
}

// 示例文本
const exampleTexts = {
  chinese: [
    '这部电影真的很棒，演员表演很自然，剧情也很吸引人！',
    '服务态度太差了，完全不推荐这家餐厅。',
    '产品质量一般，价格适中，总体来说还可以。',
    '今天天气不错，心情很好。'
  ],
  english: [
    'This movie is absolutely fantastic! The acting is superb and the plot is engaging.',
    'Terrible service and poor food quality. Would never recommend this place.',
    'The product is decent for the price. Nothing special but does the job.',
    'The weather is nice today, feeling great.'
  ]
}

// 单文本分析
const analyzeSingle = async () => {
  if (!inputText.value.trim()) {
    ElMessage.warning('请输入要分析的文本')
    return
  }

  const success = await sentimentStore.analyzeSentiment(inputText.value)
  if (success) {
    ElMessage.success('分析完成')
  } else {
    ElMessage.error(sentimentStore.error || '分析失败')
  }
}

// 批量分析
const analyzeBatch = async () => {
  if (parsedBatchTexts.value.length === 0) {
    ElMessage.warning('请输入要分析的文本列表')
    return
  }

  const success = await sentimentStore.analyzeBatch(
    parsedBatchTexts.value,
    batchConfig.value.batchSize
  )

  if (success) {
    ElMessage.success(`成功分析 ${parsedBatchTexts.value.length} 条文本`)
    // 切换到单文本标签查看结果
    activeTab.value = 'single'
  } else {
    ElMessage.error(sentimentStore.error || '批量分析失败')
  }
}

// 使用示例文本
const useExample = (text: string) => {
  if (activeTab.value === 'single') {
    inputText.value = text
  } else {
    if (batchTexts.value.trim()) {
      batchTexts.value += '\n' + text
    } else {
      batchTexts.value = text
    }
  }
}

// 清空输入
const clearInput = () => {
  if (activeTab.value === 'single') {
    inputText.value = ''
  } else {
    batchTexts.value = ''
  }
}

// 清空结果
const clearResults = () => {
  sentimentStore.clearResults()
  ElMessage.success('已清空历史结果')
}

// 获取情感标签配置
const getSentimentConfig = (sentiment: string) => {
  const key = sentiment.toLowerCase()
  return sentimentLabels[key as keyof typeof sentimentLabels] || {
    label: sentiment,
    color: '#909399',
    icon: 'QuestionFilled'
  }
}

// 格式化置信度
const formatConfidence = (confidence: number) => {
  return `${(confidence * 100).toFixed(1)}%`
}

onMounted(() => {
  // 检查后端连接
  sentimentStore.healthCheck()
  // 获取当前模型状态
  sentimentStore.fetchCurrentModel()
})
</script>

<template>
  <div class="analyze-page">
    <div class="page-header">
      <h1>
        <el-icon><ChatDotRound /></el-icon>
        文本情感分析
      </h1>
      <p>输入文本内容，系统将自动分析其情感倾向</p>
    </div>

    <el-row :gutter="24">
      <!-- 模型状态显示 -->
      <el-col :span="24">
        <el-card class="model-status-card" shadow="hover">
          <div class="model-status">
            <div class="status-left">
              <el-icon class="status-icon">
                <Box />
              </el-icon>
              <div class="status-info">
                <div class="status-title">模型状态</div>
                <div class="status-desc">
                  <span v-if="sentimentStore.currentModel.model_loaded" class="loaded">
                    已加载: {{ sentimentStore.currentModel.model_type?.toUpperCase() }}
                    ({{ sentimentStore.currentModel.language === 'chinese' ? '中文' : 'English' }})
                  </span>
                  <span v-else class="not-loaded">
                    {{ sentimentStore.currentModel.message || '未加载任何模型' }}
                  </span>
                </div>
              </div>
            </div>
            <div class="status-right">
              <el-tag
                :type="sentimentStore.currentModel.model_loaded ? 'success' : 'warning'"
                size="large"
              >
                {{ sentimentStore.currentModel.model_loaded ? '就绪' : '未就绪' }}
              </el-tag>
              <router-link to="/models">
                <el-button type="primary" size="small" style="margin-left: 12px;">
                  <el-icon><Setting /></el-icon>
                  管理模型
                </el-button>
              </router-link>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 输入区域 -->
      <el-col :xl="14" :lg="16" :md="12" :sm="24">
        <el-card class="input-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><EditPen /></el-icon>
              <span>文本输入</span>
            </div>
          </template>

          <!-- 分析模式切换 -->
          <el-tabs v-model="activeTab" class="analyze-tabs">
            <el-tab-pane label="单文本分析" name="single">
              <el-input
                v-model="inputText"
                type="textarea"
                :rows="6"
                placeholder="请输入要分析的文本内容..."
                show-word-limit
                :maxlength="1000"
                class="text-input"
              />

              <div class="input-actions">
                <el-button
                  type="primary"
                  :loading="sentimentStore.isAnalyzing"
                  :disabled="!canAnalyze"
                  @click="analyzeSingle"
                >
                  <el-icon><Search /></el-icon>
                  开始分析
                </el-button>
                <el-button @click="clearInput">
                  <el-icon><RefreshLeft /></el-icon>
                  清空输入
                </el-button>
              </div>
            </el-tab-pane>

            <el-tab-pane label="批量分析" name="batch">
              <el-input
                v-model="batchTexts"
                type="textarea"
                :rows="8"
                placeholder="请输入多条文本，每行一条..."
                show-word-limit
                :maxlength="5000"
                class="text-input"
              />

              <!-- 批量配置 -->
              <el-collapse v-model="showAdvanced" class="batch-config">
                <el-collapse-item title="高级配置" name="1">
                  <el-form label-width="100px" size="small">
                    <el-form-item label="批次大小">
                      <el-input-number
                        v-model="batchConfig.batchSize"
                        :min="1"
                        :max="50"
                        controls-position="right"
                      />
                    </el-form-item>
                    <el-form-item label="分隔符">
                      <el-select v-model="batchConfig.separator">
                        <el-option label="换行符" value="\n" />
                        <el-option label="逗号" value="," />
                        <el-option label="分号" value=";" />
                      </el-select>
                    </el-form-item>
                  </el-form>
                </el-collapse-item>
              </el-collapse>

              <div class="batch-info">
                <el-tag type="info">
                  将分析 {{ parsedBatchTexts.length }} 条文本
                </el-tag>
              </div>

              <div class="input-actions">
                <el-button
                  type="primary"
                  :loading="sentimentStore.isAnalyzing"
                  :disabled="!canAnalyze"
                  @click="analyzeBatch"
                >
                  <el-icon><Operation /></el-icon>
                  批量分析
                </el-button>
                <el-button @click="clearInput">
                  <el-icon><RefreshLeft /></el-icon>
                  清空输入
                </el-button>
              </div>
            </el-tab-pane>
          </el-tabs>

          <!-- 示例文本 -->
          <div class="examples-section">
            <h4>示例文本</h4>
            <div class="examples-grid">
              <div class="example-group">
                <h5>中文示例</h5>
                <div class="example-buttons">
                  <el-button
                    v-for="(text, index) in exampleTexts.chinese"
                    :key="index"
                    size="small"
                    type="text"
                    @click="useExample(text)"
                  >
                    {{ text.substring(0, 20) }}{{ text.length > 20 ? '...' : '' }}
                  </el-button>
                </div>
              </div>
              <div class="example-group">
                <h5>英文示例</h5>
                <div class="example-buttons">
                  <el-button
                    v-for="(text, index) in exampleTexts.english"
                    :key="index"
                    size="small"
                    type="text"
                    @click="useExample(text)"
                  >
                    {{ text.substring(0, 20) }}{{ text.length > 20 ? '...' : '' }}
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 结果区域 -->
      <el-col :xl="10" :lg="8" :md="12" :sm="24">
        <el-card class="result-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><DataAnalysis /></el-icon>
              <span>分析结果</span>
              <el-button
                v-if="sentimentStore.hasResults"
                size="small"
                type="danger"
                text
                @click="clearResults"
              >
                <el-icon><Delete /></el-icon>
                清空结果
              </el-button>
            </div>
          </template>

          <!-- 当前结果 -->
          <div v-if="sentimentStore.currentResult" class="current-result">
            <h4>最新分析结果</h4>
            <div class="result-item featured">
              <div class="result-text">
                {{ sentimentStore.currentResult.text }}
              </div>
              <div class="result-details">
                <el-tag
                  :type="getSentimentConfig(sentimentStore.currentResult.sentiment).color === '#67c23a' ? 'success' :
                         getSentimentConfig(sentimentStore.currentResult.sentiment).color === '#f56c6c' ? 'danger' : 'info'"
                  size="large"
                  effect="dark"
                >
                  <el-icon>
                    <component :is="getSentimentConfig(sentimentStore.currentResult.sentiment).icon" />
                  </el-icon>
                  {{ getSentimentConfig(sentimentStore.currentResult.sentiment).label }}
                </el-tag>
                <div class="confidence">
                  置信度: {{ formatConfidence(sentimentStore.currentResult.confidence) }}
                </div>
              </div>

              <!-- 概率分布 -->
              <div v-if="sentimentStore.currentResult.probabilities" class="probabilities">
                <h5>概率分布</h5>
                <div class="prob-bars">
                                     <div
                     v-for="(prob, sentiment) in sentimentStore.currentResult.probabilities"
                     :key="sentiment"
                     class="prob-bar"
                   >
                     <span class="prob-label">{{ getSentimentConfig(String(sentiment)).label }}</span>
                                         <el-progress
                       :percentage="prob * 100"
                       :color="getSentimentConfig(String(sentiment)).color"
                       :stroke-width="12"
                     />
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 历史结果 -->
          <div v-if="sentimentStore.hasResults" class="history-results">
            <h4>
              历史分析记录
              <el-tag type="info" size="small">{{ sentimentStore.analysisResults.length }}</el-tag>
            </h4>
            <div class="results-list">
              <div
                v-for="(result, index) in sentimentStore.analysisResults.slice(0, 10)"
                :key="index"
                class="result-item"
              >
                <div class="result-text">
                  {{ result.text.length > 50 ? result.text.substring(0, 50) + '...' : result.text }}
                </div>
                <div class="result-summary">
                  <el-tag
                    :type="getSentimentConfig(result.sentiment).color === '#67c23a' ? 'success' :
                           getSentimentConfig(result.sentiment).color === '#f56c6c' ? 'danger' : 'info'"
                    size="small"
                  >
                    {{ getSentimentConfig(result.sentiment).label }}
                  </el-tag>
                  <span class="confidence-small">
                    {{ formatConfidence(result.confidence) }}
                  </span>
                </div>
              </div>
            </div>
            <div v-if="sentimentStore.analysisResults.length > 10" class="more-results">
              <el-text type="info">还有 {{ sentimentStore.analysisResults.length - 10 }} 条记录...</el-text>
            </div>
          </div>

          <!-- 空状态 -->
          <el-empty v-else description="暂无分析结果" :image-size="120">
            <el-text type="info">输入文本并点击分析按钮开始</el-text>
          </el-empty>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.analyze-page {
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

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.card-header span {
  font-weight: 600;
}

.analyze-tabs {
  margin-bottom: 20px;
}

.text-input {
  margin-bottom: 16px;
}

.input-actions {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.batch-config {
  margin-bottom: 16px;
}

.batch-info {
  margin-bottom: 16px;
}

.examples-section {
  border-top: 1px solid #ebeef5;
  padding-top: 20px;
}

.examples-section h4 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #303133;
}

.examples-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.example-group h5 {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 8px;
  color: #606266;
}

.example-buttons {
  display: flex;
  flex-direction: column;
  gap: 4px;
  align-items: flex-start;
}

.current-result {
  margin-bottom: 30px;
}

.current-result h4 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #303133;
}

.result-item {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
  transition: all 0.3s ease;
}

.result-item:hover {
  border-color: #c6e2ff;
  background-color: #f8fbff;
}

.result-item.featured {
  border-color: #409eff;
  background: linear-gradient(135deg, #f8fbff 0%, #ecf5ff 100%);
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.result-text {
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 12px;
  color: #303133;
}

.result-details {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.confidence {
  font-size: 14px;
  font-weight: 600;
  color: #606266;
}

.probabilities h5 {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 8px;
  color: #303133;
}

.prob-bars {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.prob-bar {
  display: flex;
  align-items: center;
  gap: 12px;
}

.prob-label {
  font-size: 12px;
  min-width: 40px;
  color: #606266;
}

.history-results h4 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.results-list {
  max-height: 400px;
  overflow-y: auto;
}

.result-summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.confidence-small {
  font-size: 12px;
  color: #909399;
}

.more-results {
  text-align: center;
  padding: 12px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .examples-grid {
    grid-template-columns: 1fr;
  }

  .result-details {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .input-actions {
    flex-direction: column;
  }
}

.model-status-card {
  margin-bottom: 24px;
}

.model-status {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.status-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-icon {
  font-size: 24px;
  color: #409eff;
}

.status-info .status-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.status-info .status-desc {
  font-size: 14px;
  color: #606266;
}

.status-desc .loaded {
  color: #67c23a;
  font-weight: 500;
}

.status-desc .not-loaded {
  color: #e6a23c;
}

.status-right {
  display: flex;
  align-items: center;
}
</style>
