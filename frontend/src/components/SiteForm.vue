<template>
  <el-dialog
    v-model="visible"
    :title="isEdit ? '编辑站点' : '新增站点'"
    width="800px"
    @close="handleClose"
  >
    <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
      <!-- 1. 基础信息 -->
      <div class="section">
        <h3>1. 基础信息</h3>
        <el-form-item label="站点名称" prop="name">
          <el-input v-model="form.name" placeholder="例如: NodeLoc" />
        </el-form-item>
        
        <el-form-item label="基础 URL" prop="base_url">
          <el-input v-model="form.base_url" placeholder="https://..." />
        </el-form-item>
        
        <el-form-item label="Cron 表达式" prop="cron_expression">
          <el-input v-model="form.cron_expression" placeholder="0 9 * * *" />
          <div class="hint">例: "0 9 * * *" (每天9点)</div>
        </el-form-item>
        
        <el-form-item label="快速模板">
          <el-select v-model="selectedPreset" placeholder="-- 选择自动填充 --" @change="loadPreset">
            <el-option label="-- 选择自动填充 --" :value="null" />
            <el-option
              v-for="preset in presets"
              :key="preset.id"
              :label="`${preset.name} (${preset.architecture})`"
              :value="preset.id"
            />
          </el-select>
        </el-form-item>
      </div>
      
      <!-- 2. 登录设置 -->
      <div class="section">
        <h3>2. 登录设置</h3>
        <el-form-item label="登录方式" prop="auth_type">
          <el-select v-model="form.auth_type">
            <el-option label="Cookie (推荐)" value="cookie" />
            <el-option label="账号密码 (自动登录)" value="password" />
          </el-select>
        </el-form-item>
        
        <!-- Cookie 登录 -->
        <template v-if="form.auth_type === 'cookie'">
          <el-form-item label="Cookie" prop="cookie_string">
            <el-input
              type="textarea"
              v-model="form.cookie_string"
              :rows="4"
              placeholder="在此处粘贴完整的 Cookie 字符串..."
            />
          </el-form-item>
        </template>
        
        <!-- 账号密码登录 -->
        <template v-if="form.auth_type === 'password'">
          <el-form-item label="用户名/邮箱" prop="username">
            <el-input v-model="form.username" />
          </el-form-item>
          
          <el-form-item label="密码" prop="password">
            <el-input type="password" v-model="form.password" show-password />
          </el-form-item>
        </template>
      </div>
      
      <!-- 3. 选择器配置 -->
      <div class="section">
        <h3>3. 自动化选择器配置</h3>
        <el-tabs v-model="selectorTab">
          <el-tab-pane label="签到" name="signin">
            <el-form-item label="签到按钮">
              <el-input v-model="form.selectors.signin_button" />
            </el-form-item>
            <el-form-item label="确认按钮">
              <el-input v-model="form.selectors.signin_confirm" />
            </el-form-item>
          </el-tab-pane>
          
          <el-tab-pane label="读取帖子" name="posts">
            <el-form-item label="帖子列表URL">
              <el-input v-model="form.selectors.post_list_url" placeholder="/all" />
            </el-form-item>
            <el-form-item label="列表项">
              <el-input v-model="form.selectors.post_item" />
            </el-form-item>
            <el-form-item label="标题选择器">
              <el-input v-model="form.selectors.post_title" />
            </el-form-item>
            <el-form-item label="链接选择器">
              <el-input v-model="form.selectors.post_link" />
            </el-form-item>
            <el-form-item label="详情页标题">
              <el-input v-model="form.selectors.detail_title" />
            </el-form-item>
            <el-form-item label="详情页内容">
              <el-input v-model="form.selectors.detail_content" />
            </el-form-item>
          </el-tab-pane>
          
          <el-tab-pane label="回复" name="reply">
            <el-form-item label="回复按钮">
              <el-input v-model="form.selectors.reply_dropdown" />
            </el-form-item>
            <el-form-item label="输入框">
              <el-input v-model="form.selectors.reply_textarea" />
            </el-form-item>
            <el-form-item label="提交按钮">
              <el-input v-model="form.selectors.reply_submit" />
            </el-form-item>
          </el-tab-pane>
          
          <el-tab-pane label="登录" name="login" v-if="form.auth_type === 'password'">
            <el-form-item label="登录入口">
              <el-input v-model="form.selectors.login_modal" />
            </el-form-item>
            <el-form-item label="登录按钮">
              <el-input v-model="form.selectors.login_submit" />
            </el-form-item>
            <el-form-item label="用户名输入框">
              <el-input v-model="form.selectors.username_input" />
            </el-form-item>
            <el-form-item label="密码输入框">
              <el-input v-model="form.selectors.password_input" />
            </el-form-item>
          </el-tab-pane>
        </el-tabs>
      </div>
      
      <!-- 4. 任务配置 -->
      <div class="section">
        <h3>4. 任务配置</h3>
        <el-form-item label="启用任务">
          <el-checkbox v-model="form.enable_signin">签到</el-checkbox>
          <el-checkbox v-model="form.enable_reply">回复</el-checkbox>
          <el-checkbox v-model="form.enable_feedback">回帖</el-checkbox>
        </el-form-item>
        
        <el-form-item label="每日最大回复">
          <el-input-number v-model="form.max_daily_replies" :min="1" :max="100" />
        </el-form-item>
        
        <el-form-item label="回复字数范围">
          <el-col :span="11">
            <el-input-number v-model="form.min_reply_count" :min="1" :max="50" />
          </el-col>
          <el-col :span="2" style="text-align: center;">-</el-col>
          <el-col :span="11">
            <el-input-number v-model="form.max_reply_count" :min="1" :max="50" />
          </el-col>
        </el-form-item>
        
        <el-form-item label="回复间隔(秒)">
          <el-col :span="11">
            <el-input-number v-model="form.reply_interval_min" :min="10" :max="600" />
          </el-col>
          <el-col :span="2" style="text-align: center;">-</el-col>
          <el-col :span="11">
            <el-input-number v-model="form.reply_interval_max" :min="10" :max="600" />
          </el-col>
        </el-form-item>
      </div>
    </el-form>
    
    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" @click="handleSubmit" :loading="submitting">
        保存配置
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/api/request'

const props = defineProps({
  modelValue: Boolean,
  site: Object
})

const emit = defineEmits(['update:modelValue', 'success'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const isEdit = computed(() => !!props.site?.id)

const formRef = ref()
const submitting = ref(false)
const selectorTab = ref('signin')
const selectedPreset = ref(null)
const presets = ref([])

const form = ref({
  name: '',
  base_url: '',
  cron_expression: '0 9 * * *',
  preset_template: null,
  auth_type: 'cookie',
  cookie_string: '',
  username: '',
  password: '',
  selectors: {
    signin_button: '',
    signin_confirm: '',
    post_list_url: '/all',
    post_item: '',
    post_title: '',
    post_link: '',
    detail_title: '',
    detail_content: '',
    reply_dropdown: '',
    reply_textarea: '',
    reply_submit: '',
    login_modal: '',
    login_submit: '',
    username_input: '',
    password_input: ''
  },
  enable_signin: true,
  enable_reply: true,
  enable_feedback: false,
  max_daily_replies: 20,
  min_reply_count: 1,
  max_reply_count: 10,
  reply_interval_min: 60,
  reply_interval_max: 300
})

const rules = {
  name: [{ required: true, message: '请输入站点名称', trigger: 'blur' }],
  base_url: [{ required: true, message: '请输入基础URL', trigger: 'blur' }],
  cron_expression: [{ required: true, message: '请输入Cron表达式', trigger: 'blur' }],
  auth_type: [{ required: true, message: '请选择登录方式', trigger: 'change' }]
}

watch(() => props.site, (newSite) => {
  if (newSite) {
    Object.assign(form.value, newSite)
  } else {
    resetForm()
  }
}, { immediate: true, deep: true })

onMounted(() => {
  loadPresets()
})

const loadPresets = async () => {
  try {
    const response = await request.get('/sites/presets')
    presets.value = response || []
  } catch (error) {
    console.error('加载预设失败:', error)
  }
}

const loadPreset = async () => {
  if (!selectedPreset.value) return
  
  try {
    const response = await request.get(`/sites/presets/${selectedPreset.value}`)
    
    form.value.preset_template = selectedPreset.value
    form.value.base_url = response.base_url || form.value.base_url
    Object.assign(form.value.selectors, response.selectors || {})
    
    ElMessage.success('预设模板已加载')
  } catch (error) {
    console.error('加载预设详情失败:', error)
  }
}

const resetForm = () => {
  form.value = {
    name: '',
    base_url: '',
    cron_expression: '0 9 * * *',
    preset_template: null,
    auth_type: 'cookie',
    cookie_string: '',
    username: '',
    password: '',
    selectors: {
      signin_button: '',
      signin_confirm: '',
      post_list_url: '/all',
      post_item: '',
      post_title: '',
      post_link: '',
      detail_title: '',
      detail_content: '',
      reply_dropdown: '',
      reply_textarea: '',
      reply_submit: '',
      login_modal: '',
      login_submit: '',
      username_input: '',
      password_input: ''
    },
    enable_signin: true,
    enable_reply: true,
    enable_feedback: false,
    max_daily_replies: 20,
    min_reply_count: 1,
    max_reply_count: 10,
    reply_interval_min: 60,
    reply_interval_max: 300
  }
  selectedPreset.value = null
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    submitting.value = true
    
    if (isEdit.value) {
      await request.put(`/sites/${props.site.id}`, form.value)
      ElMessage.success('站点更新成功')
    } else {
      await request.post('/sites', form.value)
      ElMessage.success('站点创建成功')
    }
    
    emit('success')
    handleClose()
    
  } catch (error) {
    console.error('保存失败:', error)
  } finally {
    submitting.value = false
  }
}

const handleClose = () => {
  visible.value = false
  resetForm()
  formRef.value?.clearValidate()
}
</script>

<style scoped>
.section {
  margin-bottom: 30px;
}

.section h3 {
  font-size: 16px;
  color: #409eff;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #ebeef5;
}

.hint {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}
</style>
