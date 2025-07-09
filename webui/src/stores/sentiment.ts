/**
 * 情感分析状态管理
 * 用途：管理情感分析相关的全局状态
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ApiService, type SentimentResult, type TrainingStatus, type DownloadStatus } from '@/services/api'

export const useSentimentStore = defineStore('sentiment', () => {
  // 响应式状态
  const isAnalyzing = ref(false)
  const analysisResults = ref<SentimentResult[]>([])
  const currentResult = ref<SentimentResult | null>(null)
  const error = ref<string | null>(null)

  // 训练相关状态
  const trainingStatus = ref<TrainingStatus>({
    is_training: false,
    current_task: null,
    progress: 0,
    message: '',
    error: null,
    results: null
  })

  // 数据下载状态
  const downloadStatus = ref<DownloadStatus>({
    is_downloading: false,
    language: null,
    progress: 0,
    message: '',
    error: null,
    completed: false
  })

  // 模型信息
  const modelsInfo = ref<any>(null)
  const datasetsInfo = ref<any>(null)
  const trainedModels = ref<any[]>([])

  // 计算属性
  const hasResults = computed(() => analysisResults.value.length > 0)
  const isTraining = computed(() => trainingStatus.value.is_training)
  const isDownloading = computed(() => downloadStatus.value.is_downloading)

  // 当前模型状态
  const currentModel = ref<{
    model_loaded: boolean
    model_type?: string
    language?: string
    message: string
  }>({
    model_loaded: false,
    message: '未加载任何模型'
  })

  const isLoadingModel = ref(false)

  /**
   * 分析单个文本情感
   */
  const analyzeSentiment = async (text: string) => {
    if (!text.trim()) {
      error.value = '请输入要分析的文本'
      return false
    }

    try {
      isAnalyzing.value = true
      error.value = null

      const response = await ApiService.analyzeSentiment(text)

      if (response.status === 'success' && response.data) {
        currentResult.value = response.data
        // 添加到历史结果
        analysisResults.value.unshift(response.data)
        return true
      } else {
        error.value = response.message || '分析失败'
        return false
      }
    } catch (err: any) {
      error.value = err.message || '网络错误'
      return false
    } finally {
      isAnalyzing.value = false
    }
  }

  /**
   * 批量分析文本情感
   */
  const analyzeBatch = async (texts: string[], batchSize?: number) => {
    if (!texts.length) {
      error.value = '请提供要分析的文本列表'
      return false
    }

    try {
      isAnalyzing.value = true
      error.value = null

      const response = await ApiService.analyzeBatch(texts, batchSize)

      if (response.status === 'success' && response.data) {
        analysisResults.value = response.data.results
        return true
      } else {
        error.value = response.message || '批量分析失败'
        return false
      }
    } catch (err: any) {
      error.value = err.message || '网络错误'
      return false
    } finally {
      isAnalyzing.value = false
    }
  }

  /**
   * 清空分析结果
   */
  const clearResults = () => {
    analysisResults.value = []
    currentResult.value = null
    error.value = null
  }

  /**
   * 下载数据集
   */
  const downloadDataset = async (language: string, maxSamples?: number) => {
    try {
      const response = await ApiService.downloadDataset(language, maxSamples)

      if (response.status === 'success') {
        // 开始轮询下载状态
        startDownloadStatusPolling()
        return true
      } else {
        error.value = response.message || '启动下载失败'
        return false
      }
    } catch (err: any) {
      error.value = err.message || '网络错误'
      return false
    }
  }

  /**
   * 轮询下载状态
   */
  const startDownloadStatusPolling = () => {
    const pollInterval = setInterval(async () => {
      try {
        const response = await ApiService.getDownloadStatus()
        if (response.status === 'success' && response.data) {
          downloadStatus.value = response.data

          // 如果下载完成或出错，停止轮询
          if (!response.data.is_downloading) {
            clearInterval(pollInterval)
          }
        }
      } catch (err) {
        console.error('获取下载状态失败:', err)
        clearInterval(pollInterval)
      }
    }, 1000) // 每秒检查一次
  }

  /**
   * 训练模型
   */
  const trainModel = async (params: {
    model_type: string
    language: string
    epochs?: number
    batch_size?: number
    learning_rate?: number
  }) => {
    try {
      const response = await ApiService.trainModel(params)

      if (response.status === 'success') {
        // 开始轮询训练状态
        startTrainingStatusPolling()
        return true
      } else {
        error.value = response.message || '启动训练失败'
        return false
      }
    } catch (err: any) {
      error.value = err.message || '网络错误'
      return false
    }
  }

  /**
   * 轮询训练状态
   */
  const startTrainingStatusPolling = () => {
    const pollInterval = setInterval(async () => {
      try {
        const response = await ApiService.getTrainingStatus()
        if (response.status === 'success' && response.data) {
          trainingStatus.value = response.data

          // 如果训练完成或出错，停止轮询
          if (!response.data.is_training) {
            clearInterval(pollInterval)
          }
        }
      } catch (err) {
        console.error('获取训练状态失败:', err)
        clearInterval(pollInterval)
      }
    }, 2000) // 每2秒检查一次
  }

  /**
   * 获取模型信息
   */
  const fetchModelsInfo = async () => {
    try {
      const response = await ApiService.getModelsInfo()
      if (response.status === 'success') {
        modelsInfo.value = response.data
        return true
      } else {
        error.value = response.message || '获取模型信息失败'
        return false
      }
    } catch (err: any) {
      error.value = err.message || '网络错误'
      return false
    }
  }

  /**
   * 获取数据集信息
   */
  const fetchDatasetsInfo = async () => {
    try {
      const response = await ApiService.getDatasetsInfo()
      if (response.status === 'success') {
        datasetsInfo.value = response.data
        return true
      } else {
        error.value = response.message || '获取数据集信息失败'
        return false
      }
    } catch (err: any) {
      error.value = err.message || '网络错误'
      return false
    }
  }

  /**
   * 获取已训练模型列表
   */
  const fetchTrainedModels = async () => {
    try {
      const response = await ApiService.getTrainedModels()
      if (response.status === 'success' && response.data) {
        trainedModels.value = response.data.models
        return true
      } else {
        error.value = response.message || '获取模型列表失败'
        return false
      }
    } catch (err: any) {
      error.value = err.message || '网络错误'
      return false
    }
  }

  /**
   * 健康检查
   */
  const healthCheck = async () => {
    try {
      const response = await ApiService.healthCheck()
      return response.status === 'success'
    } catch (err: any) {
      error.value = err.message || '无法连接到后端服务'
      return false
    }
  }

  /**
   * 加载指定模型
   */
  const loadModel = async (params: {
    model_type: string
    language: string
    model_path?: string
  }) => {
    try {
      isLoadingModel.value = true
      error.value = null

      const response = await ApiService.loadModel(params)

      if (response.status === 'success' && response.data) {
        // 更新当前模型状态
        await fetchCurrentModel()
        return true
      } else {
        error.value = response.message || '加载模型失败'
        return false
      }
    } catch (err: any) {
      error.value = err.message || '网络错误'
      return false
    } finally {
      isLoadingModel.value = false
    }
  }

  /**
   * 获取当前加载的模型信息
   */
  const fetchCurrentModel = async () => {
    try {
      const response = await ApiService.getCurrentModel()

      if (response.status === 'success' && response.data) {
        currentModel.value = response.data
        return true
      } else {
        error.value = response.message || '获取当前模型信息失败'
        return false
      }
    } catch (err: any) {
      error.value = err.message || '网络错误'
      return false
    }
  }

  /**
   * 获取已训练的模型文件列表
   */
  const fetchTrainedModelFiles = async () => {
    try {
      const response = await ApiService.getTrainedModelFiles()

      if (response.status === 'success' && response.data) {
        trainedModels.value = response.data.models || []
        return true
      } else {
        error.value = response.message || '获取模型文件列表失败'
        return false
      }
    } catch (err: any) {
      error.value = err.message || '网络错误'
      return false
    }
  }

  /**
   * 删除指定模型
   */
  const deleteModel = async (filename: string) => {
    try {
      const response = await ApiService.deleteModel(filename)

      if (response.status === 'success' && response.data) {
        // 从本地列表中移除已删除的模型
        const index = trainedModels.value.findIndex(model => model.filename === filename)
        if (index > -1) {
          trainedModels.value.splice(index, 1)
        }
        return true
      } else {
        error.value = response.message || '删除模型失败'
        return false
      }
    } catch (err: any) {
      error.value = err.message || '网络错误'
      return false
    }
  }

  return {
    // 状态
    isAnalyzing,
    analysisResults,
    currentResult,
    error,
    trainingStatus,
    downloadStatus,
    modelsInfo,
    datasetsInfo,
    trainedModels,

    // 计算属性
    hasResults,
    isTraining,
    isDownloading,

    // 当前模型状态
    currentModel,
    isLoadingModel,

    // 方法
    analyzeSentiment,
    analyzeBatch,
    clearResults,
    downloadDataset,
    trainModel,
    fetchModelsInfo,
    fetchDatasetsInfo,
    fetchTrainedModels,
    healthCheck,
    loadModel,
    fetchCurrentModel,
    fetchTrainedModelFiles,
    deleteModel
  }
})
