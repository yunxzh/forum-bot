<template>
  <div class="site-manage">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>站点管理</span>
          <el-button type="primary" @click="showAddDialog">
            <el-icon><Plus /></el-icon>
            新增站点
          </el-button>
        </div>
      </template>
      
      <el-table :data="sites" v-loading="loading">
        <el-table-column prop="name" label="站点名称" width="150" />
        <el-table-column prop="base_url" label="URL" />
        <el-table-column prop="cron_expression" label="执行时间" width="120" />
        <el-table-column label="认证方式" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ row.auth_type === 'cookie' ? 'Cookie' : '账号密码' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="任务状态" width="150">
          <template #default="{ row }">
            <el-tag v-if="row.enable_signin" type="success" size="small">签到</el-tag>
            <el-tag v-if="row.enable_reply" type="primary" size="small">回复</el-tag>
            <el-tag v-if="row.enable_feedback" type="warning" size="small">回帖</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-switch
              v-model="row.is_active"
              :active-value="1"
              :inactive-value="0"
              :loading="row.statusLoading"
              @change="toggleSiteStatus(row)"
            />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right" align="center">
          <template #default="{ row }">
            <!-- 立即执行按钮 -->
            <el-button 
              type="primary" 
              size="small" 
              :loading="row.running"
              :disabled="!row.is_active"
              @click="runSiteNow(row)"
            >
              立即执行
            </el-button>
            
            <!-- 编辑按钮 -->
            <el-button 
              type="warning" 
              size="small" 
              @click="editSite(row)"
            >
              编辑
            </el-button>
            
            <!-- 删除按钮 -->
            <el-button 
              type="danger" 
              size="small" 
              @click="deleteSite(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 站点表单对话框 -->
    <SiteForm
      v-model="dialogVisible"
      :site="currentSite"
      @success="handleSuccess"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import request from '@/api/request'
import SiteForm from '@/components/SiteForm.vue'

const sites = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const currentSite = ref(null)

onMounted(() => {
  loadSites()
})

const loadSites = async () => {
  loading.value = true
  try {
    const response = await request.get('/sites')
    // 为每个站点添加运行状态和加载状态
    sites.value = (response || []).map(site => ({
      ...site,
      running: false,
      statusLoading: false
    }))
  } catch (error) {
    console.error('加载站点失败:', error)
    ElMessage.error('加载站点列表失败')
  } finally {
    loading.value = false
  }
}

const showAddDialog = () => {
  currentSite.value = null
  dialogVisible.value = true
}

const editSite = (site) => {
  currentSite.value = { ...site }
  dialogVisible.value = true
}

const deleteSite = (site) => {
  ElMessageBox.confirm(`确定要删除站点 "${site.name}" 吗？`, '提示', {
    type: 'warning',
    confirmButtonText: '确定',
    cancelButtonText: '取消'
  }).then(async () => {
    try {
      await request.delete(`/sites/${site.id}`)
      ElMessage.success('删除成功')
      loadSites()
    } catch (error) {
      console.error('删除站点失败:', error)
      ElMessage.error('删除站点失败')
    }
  }).catch(() => {})
}

const toggleSiteStatus = async (site) => {
  // 保存原始状态
  const originalStatus = site.is_active
  site.statusLoading = true
  
  try {
    // 发送完整的站点数据
    await request.put(`/sites/${site.id}`, {
      ...site,
      is_active: site.is_active
    })
    
    ElMessage.success(site.is_active === 1 ? '站点已启用' : '站点已禁用')
  } catch (error) {
    console.error('更新站点状态失败:', error)
    // 恢复原始状态
    site.is_active = originalStatus
    ElMessage.error(error.response?.data?.error || '更新站点状态失败')
  } finally {
    site.statusLoading = false
  }
}

/**
 * 立即执行站点任务
 */
const runSiteNow = async (site) => {
  try {
    await ElMessageBox.confirm(
      `确定要立即执行站点 "${site.name}" 的任务吗？`,
      '确认执行',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info'
      }
    )
    
    // 设置运行状态
    site.running = true
    
    try {
      // 调用立即执行 API
      const response = await request.post(`/sites/${site.id}/run`)
      
      ElMessage.success({
        message: response.message || '任务已开始执行，请稍后查看任务日志',
        duration: 3000
      })
      
      // 2秒后取消运行状态并刷新列表
      setTimeout(() => {
        site.running = false
        loadSites()
      }, 2000)
      
    } catch (error) {
      site.running = false
      console.error('执行站点任务失败:', error)
      
      ElMessage.error({
        message: error.response?.data?.error || '执行失败，请检查站点配置',
        duration: 3000
      })
    }
    
  } catch (error) {
    // 用户取消
    if (error !== 'cancel') {
      console.error('执行站点任务出错:', error)
    }
  }
}

const handleSuccess = () => {
  loadSites()
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.site-manage {
  padding: 20px;
}

/* 确保按钮之间有适当的间距 */
:deep(.el-button + .el-button) {
  margin-left: 8px;
}
</style>
