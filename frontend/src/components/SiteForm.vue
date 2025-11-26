<!-- frontend/src/components/SiteForm.vue -->
<template>
  <el-dialog title="新增站点" v-model="visible">
    <el-form :model="form" label-width="120px">
      
      <!-- 1. 基础信息 -->
      <div class="section">
        <h3>1. 基础信息</h3>
        <el-form-item label="站点名称">
          <el-input v-model="form.name" placeholder="例如: NodeLoc" />
        </el-form-item>
        <el-form-item label="基础 URL">
          <el-input v-model="form.base_url" placeholder="https://..." />
        </el-form-item>
        <el-form-item label="Cron 表达式">
          <el-input v-model="form.cron" placeholder="0 9 * * *" />
          <span class="hint">例: "0 9 * * *" (每天9点)</span>
        </el-form-item>
        <el-form-item label="快速模板">
          <el-select v-model="form.preset" @change="loadPreset">
            <el-option label="-- 选择自动填充 --" value="" />
            <el-option label="DeepFlood (Flarum架构)" value="deepflood" />
            <el-option label="NodeLoc (Discourse架构)" value="nodeloc" />
            <el-option label="LinuxDo (Discourse架构)" value="linuxdo" />
          </el-select>
        </el-form-item>
      </div>

      <!-- 2. 登录设置 -->
      <div class="section">
        <h3>2. 登录设置</h3>
        <el-form-item label="登录方式">
          <el-select v-model="form.auth_type">
            <el-option label="Cookie (推荐)" value="cookie" />
            <el-option label="账号密码 (自动登录)" value="password" />
          </el-select>
        </el-form-item>

        <!-- Cookie 登录 -->
        <template v-if="form.auth_type === 'cookie'">
          <el-form-item label="">
            <el-input 
              type="textarea" 
              v-model="form.cookie" 
              :rows="4"
              placeholder="在此处粘贴完整的 Cookie 字符串..."
            />
          </el-form-item>
        </template>

        <!-- 账号密码登录 -->
        <template v-if="form.auth_type === 'password'">
          <el-form-item label="用户名 / 邮箱">
            <el-input v-model="form.username" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input type="password" v-model="form.password" />
          </el-form-item>
          
          <div class="subsection">
            <h4>账号密码登录专用选择器</h4>
            <el-form-item label="登录入口按钮">
              <el-input v-model="form.selectors.login_modal" />
            </el-form-item>
            <el-form-item label="登录提交按钮">
              <el-input v-model="form.selectors.login_submit" />
            </el-form-item>
            <el-form-item label="用户名输入框">
              <el-input v-model="form.selectors.username_input" />
            </el-form-item>
            <el-form-item label="密码输入框">
              <el-input v-model="form.selectors.password_input" />
            </el-form-item>
          </div>
        </template>
      </div>

      <!-- 3. 自动化选择器配置 -->
      <div class="section">
        <h3>3. 自动化选择器配置</h3>
        <el-tabs v-model="activeTab">
          <el-tab-pane label="通用/签到" name="signin">
            <el-form-item label="签到按钮选择器">
              <el-input v-model="form.selectors.signin_button" />
            </el-form-item>
            <el-form-item label="签到确认按钮">
              <el-input v-model="form.selectors.signin_confirm" />
            </el-form-item>
          </el-tab-pane>

          <el-tab-pane label="读取帖子" name="read">
            <el-form-item label="帖子列表 URL">
              <el-input v-model="form.post_list_url" placeholder="/all" />
            </el-form-item>
            <el-form-item label="列表项">
              <el-input v-model="form.selectors.post_item" />
            </el-form-item>
            <el-form-item label="列表项标题选择器">
              <el-input v-model="form.selectors.post_title" />
            </el-form-item>
            <el-form-item label="列表项链接选择器">
              <el-input v-model="form.selectors.post_link" />
            </el-form-item>
            <el-form-item label="详情页标题选择器">
              <el-input v-model="form.selectors.detail_title" />
            </el-form-item>
            <el-form-item label="详情页内容选择器">
              <el-input v-model="form.selectors.detail_content" />
            </el-form-item>
          </el-tab-pane>

          <el-tab-pane label="回复功能" name="reply">
            <el-form-item label="唤起回复框按钮">
              <el-input v-model="form.selectors.reply_dropdown" />
            </el-form-item>
            <el-form-item label="编辑器输入框">
              <el-input v-model="form.selectors.reply_textarea" />
            </el-form-item>
            <el-form-item label="发送/提交按钮">
              <el-input v-model="form.selectors.reply_submit" />
            </el-form-item>
          </el-tab-pane>
        </el-tabs>
      </div>

      <!-- 任务开关 -->
      <div class="section">
        <el-form-item>
          <el-checkbox v-model="form.enable_signin">启用签到</el-checkbox>
          <el-checkbox v-model="form.enable_reply">启用回贴</el-checkbox>
          <el-checkbox v-model="form.enable_feedback">启用回帖</el-checkbox>
        </el-form-item>
      </div>

    </el-form>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" @click="save">保存配置</el-button>
    </template>
  </el-dialog>
</template>
