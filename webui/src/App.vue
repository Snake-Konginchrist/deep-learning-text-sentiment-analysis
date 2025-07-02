<!-- 主应用组件 -->
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterView, useRouter } from 'vue-router'
import { useSentimentStore } from '@/stores/sentiment'
import { ElMessage } from 'element-plus'

const router = useRouter()
const sentimentStore = useSentimentStore()
const isConnected = ref(false)

// 菜单项配置
const menuItems = [
  { path: '/', label: '首页', icon: 'HomeFilled' },
  { path: '/analyze', label: '情感分析', icon: 'ChatDotRound' },
  { path: '/dataset', label: '数据集管理', icon: 'FolderOpened' },
  { path: '/training', label: '模型训练', icon: 'Setting' },
  { path: '/models', label: '模型管理', icon: 'Box' },
  { path: '/about', label: '关于项目', icon: 'InfoFilled' }
]

const activeMenu = ref('/')

// 检查后端连接状态
const checkConnection = async () => {
  try {
    const connected = await sentimentStore.healthCheck()
    isConnected.value = connected
    if (!connected) {
      ElMessage.error('无法连接到后端服务，请检查服务器是否启动')
    }
  } catch (error) {
    isConnected.value = false
    ElMessage.error('后端服务连接失败')
  }
}

onMounted(() => {
  checkConnection()
  // 定时检查连接状态
  setInterval(checkConnection, 30000) // 每30秒检查一次
})

// 处理菜单点击
const handleMenuClick = (path: string) => {
  activeMenu.value = path
  router.push(path)
}
</script>

<template>
  <div class="app-container">
    <!-- 顶部导航栏 -->
    <el-container>
      <el-header class="app-header">
        <div class="header-left">
          <h1 class="app-title">
            <el-icon><BrainFilled /></el-icon>
            深度学习文本情感分析系统
          </h1>
        </div>
        <div class="header-right">
          <el-badge :is-dot="!isConnected" type="danger">
            <el-button
              :type="isConnected ? 'success' : 'danger'"
              size="small"
              @click="checkConnection"
            >
              <el-icon><Connection /></el-icon>
              {{ isConnected ? '服务正常' : '服务异常' }}
            </el-button>
          </el-badge>
        </div>
      </el-header>

      <!-- 主内容区域 -->
      <el-container>
        <!-- 侧边栏 -->
        <el-aside width="240px" class="app-sidebar">
          <el-menu
            :default-active="activeMenu"
            class="sidebar-menu"
            @select="handleMenuClick"
          >
            <el-menu-item
              v-for="item in menuItems"
              :key="item.path"
              :index="item.path"
            >
              <el-icon><component :is="item.icon" /></el-icon>
              <span>{{ item.label }}</span>
            </el-menu-item>
          </el-menu>
        </el-aside>

        <!-- 主内容 -->
        <el-main class="app-main">
          <RouterView />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<style scoped>
.app-container {
  height: 100vh;
  background-color: #f5f7fa;
}

.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.header-left {
  display: flex;
  align-items: center;
}

.app-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.app-sidebar {
  background-color: white;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
  border-right: 1px solid #e4e7ed;
}

.sidebar-menu {
  border-right: none;
  height: 100%;
}

.sidebar-menu .el-menu-item {
  height: 50px;
  line-height: 50px;
  padding-left: 20px;
}

.sidebar-menu .el-menu-item:hover {
  background-color: #ecf5ff;
  color: #409eff;
}

.sidebar-menu .el-menu-item.is-active {
  background-color: #409eff;
  color: white;
}

.sidebar-menu .el-menu-item.is-active .el-icon {
  color: white;
}

.app-main {
  background-color: #f5f7fa;
  padding: 20px;
  overflow-y: auto;
  width: 100%;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .app-title {
    font-size: 16px;
  }

  .app-sidebar {
    width: 60px !important;
  }

  .sidebar-menu .el-menu-item span {
    display: none;
  }

  .app-main {
    padding: 10px;
  }
}
</style>
