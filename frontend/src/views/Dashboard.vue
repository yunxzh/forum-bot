<template>
  <div class="dashboard">
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" color="#409eff"><Monitor /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_sites }}</div>
              <div class="stat-label">站点总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" color="#67c23a"><CircleCheck /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.success_tasks }}</div>
              <div class="stat-label">成功任务</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" color="#f56c6c"><CircleClose /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.failed_tasks }}</div>
              <div class="stat-label">失败任务</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" color="#e6a23c"><Document /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_replies }}</div>
              <div class="stat-label">总回复数</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>任务执行趋势</span>
              <el-radio-group v-model="chartDays" size="small" @change="loadStats">
                <el-radio-button :label="7">7天</el-radio-button>
                <el-radio-button :label="30">30天</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="chartRef" style="height: 300px;"></div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>最近任务</span>
          </template>
          <el-timeline>
            <el-timeline-item
              v-for="log in recentLogs"
              :key="log.id"
              :timestamp="formatTime(log.executed_at)"
              :type="log.status === 'success' ? 'success' : 'danger'"
            >
              <div class="timeline-content">
                <div class="timeline-title">{{ log.site_name }}</div>
                <div class="timeline-desc">{{ log.task_type }} - {{ log.message }}</div>
              </div>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>站点列表</span>
          </template>
          <el-table :data="sites" style="width: 100%">
            <el-table-column prop="name" label="站点名称" />
            <el-table-column prop="base_url" label="URL" />
            <el-table-column label="任务状态">
              <template #default="{ row }">
                <el-tag v-if="row.enable_signin" type="success" size="small">签到</el-tag>
                <el-tag v-if="row.enable_reply" type="primary" size="small">回复</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="最后运行">
              <template #default="{ row }">
                {{ row.last_run_at ? formatTime(row.last_run_at) : '未运行' }}
              </template>
            </el-table-column>
            <el-table-column label="状态">
              <template #default="{ row }">
                <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
                  {{ row.is_active ? '活跃' : '禁用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180">
              <template #default="{ row }">
                <el-button size="small" @click="runTask(row.id)">立即运行</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import request from '@/api/request'

const stats = ref({
  total_sites: 0,
  success_tasks: 0,
  failed_tasks: 0,
  total_replies: 0
})

const chartDays = ref(7)
const chartRef = ref()
let chartInstance = null

const recentLogs = ref([])
const sites = ref([])

onMounted(() => {
  loadStats()
  loadRecentLogs()
  loadSites()
})

const loadStats = async () => {
  try {
    const response = await request.get('/tasks/stats', {
      params: { days: chartDays.value }
    })
    
    // 更新统计数据
    const statusStats = response.status_stats || {}
    stats.value.success_tasks = statusStats.success || 0
    stats.value.failed_tasks = statusStats.failed || 0
    
    const typeStats = response.type_stats || {}
    stats.value.total_replies = typeStats.reply || 0
    
    // 渲染图表
    await nextTick()
    renderChart(response.daily_stats || {})
    
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

const loadRecentLogs = async () => {
  try {
    const response = await request.get('/tasks/logs', {
      params: { per_page: 10 }
    })
    recentLogs.value = response.logs || []
  } catch (error) {
    console.error('加载最近日志失败:', error)
  }
}

const loadSites = async () => {
  try {
    const response = await request.get('/sites')
    sites.value = response || []
    stats.value.total_sites = response.length
  } catch (error) {
    console.error('加载站点列表失败:', error)
  }
}

const renderChart = (dailyStats) => {
  if (!chartRef.value) return
  
  if (chartInstance) {
    chartInstance.dispose()
  }
  
  chartInstance = echarts.init(chartRef.value)
  
  // 处理数据
  const dates = Object.keys(dailyStats).sort().reverse().slice(0, chartDays.value)
  const successData = dates.map(date => dailyStats[date]?.success || 0)
  const failedData = dates.map(date => dailyStats[date]?.failed || 0)
  
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['成功', '失败']
    },
    xAxis: {
      type: 'category',
      data: dates.map(date => date.slice(5))
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '成功',
        type: 'line',
        data: successData,
        smooth: true,
        itemStyle: { color: '#67c23a' }
      },
      {
        name: '失败',
        type: 'line',
        data: failedData,
        smooth: true,
        itemStyle: { color: '#f56c6c' }
      }
    ]
  }
  
  chartInstance.setOption(option)
}

const runTask = async (siteId) => {
  try {
    await request.post(`/tasks/run/${siteId}`)
    ElMessage.success('任务已加入执行队列')
    setTimeout(loadRecentLogs, 2000)
  } catch (error) {
    console.error('运行任务失败:', error)
  }
}

const formatTime = (time) => {
  if (!time) return ''
  const date = new Date(time)
  return date.toLocaleString('zh-CN')
}
</script>

<style scoped>
.dashboard {
  width: 100%;
}

.stat-card {
  cursor: pointer;
  transition: all 0.3s;
}

.stat-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.stat-icon {
  font-size: 48px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.timeline-content {
  padding-left: 10px;
}

.timeline-title {
  font-weight: bold;
  margin-bottom: 5px;
}

.timeline-desc {
  font-size: 12px;
  color: #909399;
}
</style>
