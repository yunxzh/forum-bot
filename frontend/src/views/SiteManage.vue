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
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-switch
              v-model="row.is_active"
              @change="toggleSiteStatus(row)"
            />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="editSite(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteSite(row)">删除</el-button>
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
    sites.value = response || []
  } catch (error) {
    console.error('加载站点失败:', error)
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
    type: 'warning'
  }).then(async () => {
    try {
      await request.delete(`/sites/${site.id}`)
      ElMessage.success('删除成功')
      loadSites()
    } catch (error) {
      console.error('删除站点失败:', error)
    }
  }).catch(() => {})
}

const toggleSiteStatus = async (site) => {
  try {
    await request.put(`/sites/${site.id}`, {
      is_active: site.is_active
    })
    ElMessage.success(site.is_active ? '已启用' : '已禁用')
  } catch (error) {
    console.error('更新站点状态失败:', error)
    site.is_active = !site.is_active
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
</style>
