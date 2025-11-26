<template>
  <el-card>
    <el-collapse v-model="activeNames">
      <!-- Telegram -->
      <el-collapse-item name="telegram">
        <template #title>
          <div class="collapse-title">
            <el-icon><Message /></el-icon>
            <span>Telegram (推荐)</span>
            <el-tag v-if="form.tg_enabled" type="success" size="small">已启用</el-tag>
          </div>
        </template>
        
        <el-form label-width="120px">
          <el-form-item>
            <el-switch v-model="form.tg_enabled" active-text="启用" />
          </el-form-item>
          
          <template v-if="form.tg_enabled">
            <el-form-item label="Bot Token">
              <el-input v-model="form.tg_bot_token" placeholder="从 @BotFather 获取" />
            </el-form-item>
            
            <el-form-item label="User ID">
              <el-input v-model="form.tg_user_id" placeholder="发送 /start 给 @userinfobot 获取" />
            </el-form-item>
            
            <el-form-item label="Thread ID">
              <el-input v-model="form.tg_thread_id" placeholder="超级群组话题ID（可选）" />
            </el-form-item>
            
            <el-form-item label="API Host">
              <el-input v-model="form.tg_api_host" placeholder="https://api.telegram.org" />
            </el-form-item>
            
            <el-form-item label="代理地址">
              <el-input v-model="form.tg_proxy_host" placeholder="可选" />
            </el-form-item>
            
            <el-form-item label="代理端口">
              <el-input v-model="form.tg_proxy_port" placeholder="可选" />
            </el-form-item>
          </template>
        </el-form>
      </el-collapse-item>
      
      <!-- 企业微信 -->
      <el-collapse-item name="wecom">
        <template #title>
          <div class="collapse-title">
            <el-icon><ChatDotRound /></el-icon>
            <span>企业微信机器人</span>
            <el-tag v-if="form.wecom_enabled" type="success" size="small">已启用</el-tag>
          </div>
        </template>
        
        <el-form label-width="120px">
          <el-form-item>
            <el-switch v-model="form.wecom_enabled" active-text="启用" />
          </el-form-item>
          
          <el-form-item label="Webhook Key" v-if="form.wecom_enabled">
            <el-input v-model="form.wecom_key" placeholder="企业微信机器人Webhook Key" />
          </el-form-item>
        </el-form>
      </el-collapse-item>
      
      <!-- PushPlus -->
      <el-collapse-item name="pushplus">
        <template #title>
          <div class="collapse-title">
            <el-icon><Promotion /></el-icon>
            <span>PushPlus 微信推送</span>
            <el-tag v-if="form.pushplus_enabled" type="success" size="small">已启用</el-tag>
          </div>
        </template>
        
        <el-form label-width="120px">
          <el-form-item>
            <el-switch v-model="form.pushplus_enabled" active-text="启用" />
          </el-form-item>
          
          <template v-if="form.pushplus_enabled">
            <el-form-item label="Token">
              <el-input v-model="form.pushplus_token" placeholder="PushPlus Token" />
            </el-form-item>
            
            <el-form-item label="群组编码">
              <el-input v-model="form.pushplus_user" placeholder="可选" />
            </el-form-item>
          </template>
        </el-form>
      </el-collapse-item>
      
      <!-- 钉钉机器人 -->
      <el-collapse-item name="dingding">
        <template #title>
          <div class="collapse-title">
            <el-icon><Bell /></el-icon>
            <span>钉钉机器人</span>
            <el-tag v-if="form.dingding_enabled" type="success" size="small">已启用</el-tag>
          </div>
        </template>
        
        <el-form label-width="120px">
          <el-form-item>
            <el-switch v-model="form.dingding_enabled" active-text="启用" />
          </el-form-item>
          
          <template v-if="form.dingding_enabled">
            <el-form-item label="Access Token">
              <el-input v-model="form.dingding_token" />
            </el-form-item>
            
            <el-form-item label="Secret">
              <el-input v-model="form.dingding_secret" />
            </el-form-item>
          </template>
        </el-form>
      </el-collapse-item>
      
      <!-- 飞书机器人 -->
      <el-collapse-item name="feishu">
        <template #title>
          <div class="collapse-title">
            <el-icon><ChatLineRound /></el-icon>
            <span>飞书机器人</span>
            <el-tag v-if="form.feishu_enabled" type="success" size="small">已启用</el-tag>
          </div>
        </template>
        
        <el-form label-width="120px">
          <el-form-item>
            <el-switch v-model="form.feishu_enabled" active-text="启用" />
          </el-form-item>
          
          <el-form-item label="Webhook Key" v-if="form.feishu_enabled">
            <el-input v-model="form.feishu_key" />
          </el-form-item>
        </el-form>
      </el-collapse-item>
      
      <!-- Bark -->
      <el-collapse-item name="bark">
        <template #title>
          <div class="collapse-title">
            <el-icon><Iphone /></el-icon>
            <span>Bark (iOS)</span>
            <el-tag v-if="form.bark_enabled" type="success" size="small">已启用</el-tag>
          </div>
        </template>
        
        <el-form label-width="120px">
          <el-form-item>
            <el-switch v-model="form.bark_enabled" active-text="启用" />
          </el-form-item>
          
          <template v-if="form.bark_enabled">
            <el-form-item label="推送地址">
              <el-input v-model="form.bark_push" placeholder="设备码或完整URL" />
            </el-form-item>
            
            <el-form-item label="提示音">
              <el-input v-model="form.bark_sound" placeholder="可选" />
            </el-form-item>
          </template>
        </el-form>
      </el-collapse-item>
      
      <!-- SMTP 邮件 -->
      <el-collapse-item name="smtp">
        <template #title>
          <div class="collapse-title">
            <el-icon><Message /></el-icon>
            <span>SMTP 邮件推送</span>
            <el-tag v-if="form.smtp_enabled" type="success" size="small">已启用</el-tag>
          </div>
        </template>
        
        <el-form label-width="120px">
          <el-form-item>
            <el-switch v-model="form.smtp_enabled" active-text="启用" />
          </el-form-item>
          
          <template v-if="form.smtp_enabled">
            <el-form-item label="SMTP服务器">
              <el-input v-model="form.smtp_server" placeholder="smtp.gmail.com:465" />
            </el-form-item>
            
            <el-form-item label="发件邮箱">
              <el-input v-model="form.smtp_email" />
            </el-form-item>
            
            <el-form-item label="密码/授权码">
              <el-input v-model="form.smtp_password" type="password" show-password />
            </el-form-item>
            
            <el-form-item label="发件人名称">
              <el-input v-model="form.smtp_name" placeholder="Forum-Bot" />
            </el-form-item>
            
            <el-form-item label="使用SSL">
              <el-switch v-model="form.smtp_ssl" />
            </el-form-item>
          </template>
        </el-form>
      </el-collapse-item>
      
      <!-- Gotify -->
      <el-collapse-item name="gotify">
        <template #title>
          <div class="collapse-title">
            <el-icon><BellFilled /></el-icon>
            <span>Gotify</span>
            <el-tag v-if="form.gotify_enabled" type="success" size="small">已启用</el-tag>
          </div>
        </template>
        
        <el-form label-width="120px">
          <el-form-item>
            <el-switch v-model="form.gotify_enabled" active-text="启用" />
          </el-form-item>
          
          <template v-if="form.gotify_enabled">
            <el-form-item label="服务器地址">
              <el-input v-model="form.gotify_url" placeholder="https://gotify.example.com" />
            </el-form-item>
            
            <el-form-item label="应用Token">
              <el-input v-model="form.gotify_token" />
            </el-form-item>
            
            <el-form-item label="优先级">
              <el-input-number v-model="form.gotify_priority" :min="0" :max="10" />
            </el-form-item>
          </template>
        </el-form>
      </el-collapse-item>
    </el-collapse>
    
    <div class="footer-actions">
      <el-button type="primary" @click="handleSave" :loading="saving">
        保存所有配置
      </el-button>
      <el-button @click="handleTest">
        发送测试通知
      </el-button>
    </div>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/api/request'

const activeNames = ref(['telegram'])
const saving = ref(false)

const form = ref({
  tg_enabled: false,
  tg_bot_token: '',
  tg_user_id: '',
  tg_thread_id: '',
  tg_api_host: 'https://api.telegram.org',
  tg_proxy_host: '',
  tg_proxy_port: '',
  
  wecom_enabled: false,
  wecom_key: '',
  
  pushplus_enabled: false,
  pushplus_token: '',
  pushplus_user: '',
  
  dingding_enabled: false,
  dingding_token: '',
  dingding_secret: '',
  
  feishu_enabled: false,
  feishu_key: '',
  
  bark_enabled: false,
  bark_push: '',
  bark_sound: '',
  
  smtp_enabled: false,
  smtp_server: '',
  smtp_email: '',
  smtp_password: '',
  smtp_name: 'Forum-Bot',
  smtp_ssl: true,
  smtp_port: 465,
  
  gotify_enabled: false,
  gotify_url: '',
  gotify_token: '',
  gotify_priority: 5
})

onMounted(() => {
  loadConfig()
})

const loadConfig = async () => {
  try {
    const response = await request.get('/notifications/config')
    Object.assign(form.value, response)
  } catch (error) {
    console.error('加载通知配置失败:', error)
  }
}

const handleSave = async () => {
  try {
    saving.value = true
    await request.put('/notifications/config', form.value)
    ElMessage.success('通知配置保存成功')
  } catch (error) {
    console.error('保存通知配置失败:', error)
  } finally {
    saving.value = false
  }
}

const handleTest = async () => {
  try {
    // 获取启用的渠道
    const enabledChannels = []
    if (form.value.tg_enabled) enabledChannels.push('telegram')
    if (form.value.wecom_enabled) enabledChannels.push('wecom')
    if (form.value.pushplus_enabled) enabledChannels.push('pushplus')
    if (form.value.dingding_enabled) enabledChannels.push('dingding')
    if (form.value.feishu_enabled) enabledChannels.push('feishu')
    if (form.value.bark_enabled) enabledChannels.push('bark')
    if (form.value.smtp_enabled) enabledChannels.push('smtp')
    if (form.value.gotify_enabled) enabledChannels.push('gotify')
    
    if (enabledChannels.length === 0) {
      ElMessage.warning('请先启用至少一个通知渠道')
      return
    }
    
    for (const channel of enabledChannels) {
      await request.post('/notifications/test', { channel })
    }
    
    ElMessage.success('测试通知已发送，请检查接收情况')
  } catch (error) {
    console.error('发送测试通知失败:', error)
  }
}
</script>

<style scoped>
.collapse-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 500;
}

.footer-actions {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
  display: flex;
  gap: 10px;
}
</style>
