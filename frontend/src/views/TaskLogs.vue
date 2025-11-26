<template>
  <div class="task-logs">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>任务日志</span>
          <el-button type="danger" @click="clearOldLogs">清理旧日志</el-button>
        </div>
      </template>
      
      <!-- 筛选条件 -->
      <div class="filter-bar">
        <el-select v-model="filters.site_id" placeholder="选择站点" clearable @change="loadLogs">
          <el-option
            v-for="site in sites"
            :key="site.id"
            :label="site.name"
            :value="site.id"
          />
        </el-select>
        
        <el-select v-model="filters.task_type" placeholder="任务类型" clearable @change="loadLogs">
          <el-option label="签到" value="signin" />
          <el-option label="回复" value="reply" />
          <el-option label="回帖" value="feedback" />
        </el-select>
        
        <el-select v-model="filters.status" placeholder="状态" clearable @change="loadLogs">
          <el-option label="成功" value="success" />
          <el-option label="失败" value="failed" />
          <el-option label="跳过" value="skipped" />
        </el-select>
        
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          @change="handleDateChange"
        />
      </div>
      
      <!-- 日志表格 -->
      <el-table :data="logs" v-loading="loading" style="margin-top: 20px;">
        <el-table-column prop="site_name" label="站点" width="120" />
        <el-table-column label="任务类型" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ taskTypeMap[row.task_type] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="statusTypeMap[row.status]" size="small">
              {{ statusMap[row.status] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="message" label="消息" />
        <el-table-column label="执行时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.executed_at) }}
          </template>
        </el-table-column>
        <el-table-column label="耗时" width="100">
          <template #default="{ row }">
            {{ row.duration ? row.duration.toFixed(2) + 's' : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button size="small" @click="showDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.per_page"
        :total="pagination.total"
        :page-sizes="[20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @current-change="loadLogs"
        @size-change="loadLogs"
        style="margin-top: 20px; justify-content: flex-end;"
      />
    </el-card>
    
    <!-- 详情对话框 -->
    <el-dialog v-model="detailVisible" title="任务详情" width="600px">
      <el-descriptions :column="1" border v-if="currentLog">
        <el-descriptions-item label="站点">{{ currentLog.site_name }}</el-descriptions-item>
        <el-descriptions-item label="任务类型">{{ taskTypeMap[currentLog.task_type] }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusTypeMap[currentLog.status]">{{ statusMap[currentLog.status] }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="消息">{{ currentLog.message }}</el-descriptions-item>
        <el-descriptions-item label="执行时间">{{ formatTime(currentLog.executed_at) }}</el-descriptions-item>
        <el-descriptions-item label="耗时">{{ currentLog.duration ? currentLog.duration.toFixed(2) + 's' : '-' }}</el-descriptions-item>
        <el-descriptions-item label="详细信息">
          <pre>{{ JSON.stringify(currentLog.details, null, 2) }}</pre>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/api/request'

const logs = ref([])
const sites = ref([])
const loading = ref(false)
const detailVisible = ref(false)
const currentLog = ref(null)
const dateRange = ref([])

const filters = reactive({
  site_id: null,
  task_type: null,
  status: null,
  start_date: null,
  end_date: null
})

const pagination = reactive({
  page: 1,
  per_page: 50,
  total: 0
})

const taskTypeMap = {
  signin: '签到',
  reply: '回复',
  feedback: '回帖'
}

const statusMap = {
  success: '成功',
  failed: '失败',
  skipped: '跳过'
}

const statusTypeMap = {
  success: 'success',
  failed: 'danger',
  skipped: 'info'
}

onMounted(() => {
  loadSites()
  loadLogs()
})

const loadSites = async () => {
  try {
    const response = await request.get('/sites')
    sites.value = response || []
  } catch (error) {
    console.error('加载站点失败:', error)
  }
}

const loadLogs = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      per_page: pagination.per_page,
      ...filters
    }
    
    const response = await request.get('/tasks/logs', { params })
    logs.value = response.logs || []
    pagination.total = response.total || 0
  } catch (error) {
    console.error('加载日志失败:', error)
  } finally {
    loading.value = false
  }
}

const handleDateChange = (dates) => {
  if (dates && dates.length === 2) {
    filters.start_date = dates[0].toISOString().split('T')[0]
    filters.end_date = dates[1].toISOString().split('T')[0]
  } else {
    filters.start_date = null
    filters.end_date = null
  }
  loadLogs()
}

const showDetail = (log) => {
  currentLog.value = log
  detailVisible.value = true
}

const clearOldLogs = () => {
  ElMessageBox.prompt('请输入要清理多少天前的日志', '清理旧日志', {
    inputValue: '30',
    inputPattern: /^\d+$/,
    inputErrorMessage: '请输入有效的天数'
  }).then(async ({ value }) => {
    try {
      await request.delete('/tasks/logs', {
        params: { days: parseInt(value) }
      })
      ElMessage.success('清理成功')
      loadLogs()
    } catch (error) {
      console.error('清理日志失败:', error)
    }
  }).catch(() => {})
}

const formatTime = (time) => {
  if (!time) return ''
  const date = new Date(time)
  return date.toLocaleString('zh-CN')
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-bar {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

pre {
  background: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
  max-height: 300px;
  overflow-y: auto;
}
</style>
