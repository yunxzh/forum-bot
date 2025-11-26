<template>
  <div class="settings">
    <el-tabs v-model="activeTab">
      <el-tab-pane label="AI配置" name="ai">
        <AIConfig />
      </el-tab-pane>
      
      <el-tab-pane label="通知配置" name="notification">
        <NotifyConfig />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import AIConfig from '@/components/AIConfig.vue'
import NotifyConfig from '@/components/NotifyConfig.vue'

const activeTab = ref('ai')
</script>

<style scoped>
.settings {
  width: 100%;
}
</style>
