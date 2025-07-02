/**
 * API服务类
 * 用途：封装与后端API的通信逻辑
 */

import axios from 'axios'
import type { AxiosResponse } from 'axios'

// API基础配置
const API_BASE_URL = 'http://localhost:5000'

// 创建axios实例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 响应拦截器
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error) => {
    console.error('API请求失败:', error)
    return Promise.reject(error)
  }
)

// 接口类型定义
export interface SentimentResult {
  text: string
  sentiment: string
  confidence: number
  predicted_class: number
  probabilities?: {
    [key: string]: number
  }
}

export interface ApiResponse<T = any> {
  status: 'success' | 'error'
  message?: string
  data?: T
}

export interface TrainingStatus {
  is_training: boolean
  current_task: string | null
  progress: number
  message: string
  error: string | null
  results: any
}

export interface DownloadStatus {
  is_downloading: boolean
  language: string | null
  progress: number
  message: string
  error: string | null
  completed: boolean
}

export interface ModelInfo {
  type: string
  name: string
  description: string
  languages: string[]
}

export interface TrainedModel {
  model_type: string
  language: string
  filename: string
  size: number
  created_time: number
}

/**
 * API服务类
 */
export class ApiService {
  /**
   * 健康检查
   */
  static async healthCheck(): Promise<ApiResponse> {
    const response = await apiClient.get('/')
    return response.data
  }

  /**
   * 单文本情感分析
   */
  static async analyzeSentiment(text: string): Promise<ApiResponse<SentimentResult>> {
    const response = await apiClient.post('/analyze', { text })
    return response.data
  }

  /**
   * 批量文本情感分析
   */
  static async analyzeBatch(texts: string[], batchSize?: number): Promise<ApiResponse<{ total_count: number; results: SentimentResult[] }>> {
    const response = await apiClient.post('/analyze/batch', {
      texts,
      batch_size: batchSize
    })
    return response.data
  }

  /**
   * 获取模型信息
   */
  static async getModelsInfo(): Promise<ApiResponse<{
    current_model: any
    available_models: ModelInfo[]
    supported_languages: any[]
  }>> {
    const response = await apiClient.get('/models')
    return response.data
  }

  /**
   * 下载数据集
   */
  static async downloadDataset(language: string, maxSamples?: number): Promise<ApiResponse> {
    const response = await apiClient.post('/training/datasets/download', {
      language,
      max_samples: maxSamples
    })
    return response.data
  }

  /**
   * 获取数据下载状态
   */
  static async getDownloadStatus(): Promise<ApiResponse<DownloadStatus>> {
    const response = await apiClient.get('/training/datasets/status')
    return response.data
  }

  /**
   * 获取数据集信息
   */
  static async getDatasetsInfo(): Promise<ApiResponse> {
    const response = await apiClient.get('/training/datasets/info')
    return response.data
  }

  /**
   * 启动模型训练
   */
  static async trainModel(params: {
    model_type: string
    language: string
    epochs?: number
    batch_size?: number
    learning_rate?: number
  }): Promise<ApiResponse> {
    const response = await apiClient.post('/training/models/train', params)
    return response.data
  }

  /**
   * 获取训练状态
   */
  static async getTrainingStatus(): Promise<ApiResponse<TrainingStatus>> {
    const response = await apiClient.get('/training/models/status')
    return response.data
  }

  /**
   * 获取已训练模型列表
   */
  static async getTrainedModels(): Promise<ApiResponse<{
    models: TrainedModel[]
    total_count: number
  }>> {
    const response = await apiClient.get('/training/models/list')
    return response.data
  }

  /**
   * 加载指定模型
   */
  static async loadModel(params: {
    model_type: string
    language: string
    model_path?: string
  }): Promise<ApiResponse<{
    model_type: string
    language: string
    model_path: string
    model_loaded: boolean
  }>> {
    const response = await apiClient.post('/models/load', params)
    return response.data
  }

  /**
   * 获取当前加载的模型信息
   */
  static async getCurrentModel(): Promise<ApiResponse<{
    model_loaded: boolean
    model_type?: string
    language?: string
    message: string
  }>> {
    const response = await apiClient.get('/models/current')
    return response.data
  }

  /**
   * 获取已训练的模型文件列表
   */
  static async getTrainedModelFiles(): Promise<ApiResponse<{
    models: TrainedModel[]
    total_count: number
  }>> {
    const response = await apiClient.get('/models/trained')
    return response.data
  }
}

export default ApiService
