<template>
  <el-card>
    <el-form :model="form" :rules="rules" ref="formRef" label-width="140px">
      <el-form-item label="AI 提供商" prop="provider">
        <el-input v-model="form.provider" placeholder="openai" />
        <div class="hint">例如: openai, new-api, one-api</div>
      </el-form-item>
      
      <el-form-item label="API 基础地址" prop="base_url">
        <el-input v-model="form.base_url" placeholder="https://api.openai.com/v1" />
        <div class="hint">若在Docker中，可使用 http://host.docker.internal:xxxx</div>
      </el-form-item>
      
      <el-form-item label="API 密钥" prop="api_key">
        <el-input v-model="form.api_key" type="password" show-password />
      </el-form-item>
      
      <el-form-item label="模型名称" prop="model">
        <el-input v-model="form.model" placeholder="gpt-3.5-turbo" />
        <div class="hint">例如: gpt-3.5-turbo, gpt-4, claude-3-sonnet</div>
      </el-form-item>
      
      <el-form-item label="Temperature">
        <el-slider v-model="form.temperature" :min="0" :max="2" :step="0.1" show-input />
        <div class="hint">控制回复的随机性，0-2之间，默认0.8</div>
      </el-form-item>
      
      <el-form-item label="最大Token数">
        <el-input-number v-model="form.max_tokens" :min="50" :max="500" />
        <div class="hint">单次回复的最大Token数量</div>
      </el-form-item>
      
      <el-form-item>
        <el-button type="primary" @click="handleSave" :loading="saving">
          保存配置
        </el-button>
        <el-button @click="handleTest" :loading="testing">
          测试连接
        </el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/api/request'

const formRef = ref()
const saving = ref(false)
const testing = ref(false)

const form = ref({
  provider: 'openai',
  base_url: 'https://api.openai.com/v1',
  api_key: '',
  model: 'gpt-3.5-turbo',
  temperature: 0.8,
  max_tokens: 100
})

const rules = {
  base_url: [{ required: true, message: '请输入API基础地址', trigger: 'blur' }],
  api_key: [{ required: true, message: '请输入API密钥', trigger: 'blur' }],
  model: [{ required: true, message: '请输入模型名称', trigger: 'blur' }]
}

onMounted(() => {
  loadConfig()
})

const loadConfig = async () => {
  try {
    const response = await request.get('/ai/config')
    Object.assign(form.value, response)
  } catch (error) {
    console.error('加载AI配置失败:', error)
  }
}

const handleSave = async () => {
  try {
    await formRef.value.validate()
    saving.value = true
    
    await request.put('/ai/config', form.value)
    ElMessage.success('AI配置保存成功')
    
  } catch (error) {
    console.error('保存AI配置失败:', error)
  } finally {
    saving.value = false
  }
}

const handleTest = async () => {
  try {
    testing.value = true
    await request.post('/ai/config/test', form.value)
    ElMessage.success('AI连接测试成功')
  } catch (error) {
    ElMessage.error('AI连接测试失败')
    console.error('测试AI配置失败:', error)
  } finally {
    testing.value = false
  }
}
</script>

<style scoped>
.hint {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}
</style>
