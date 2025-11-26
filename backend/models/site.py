# backend/models/site.py
class Site:
    id: int
    name: str                    # 站点名称
    base_url: str               # 基础 URL
    cron_expression: str        # Cron 表达式
    preset_template: str        # 预设模板（可选）
    
    # 登录配置
    auth_type: str              # 'cookie' 或 'password'
    cookie_string: str          # Cookie 字符串
    username: str               # 用户名（密码登录用）
    password: str               # 密码
    
    # CSS 选择器配置
    selectors: dict = {
        # 签到相关
        'signin_button': '.Button--uCheckIn',
        'signin_confirm': None,
        
        # 读取帖子
        'post_list_url': '/all',
        'post_item': 'li[data-id]',
        'post_title': '.DiscussionListItem-title',
        'post_link': '.DiscussionListItem-main a',
        'post_content': '.Post-body',
        
        # 回复相关
        'reply_dropdown': '.SplitDropdown-button',
        'reply_textarea': 'textarea.FormControl',
        'reply_submit': '.item-submit button',
        
        # 登录相关（密码登录用）
        'login_modal': '.LogInModal-content',
        'login_submit': '.LogInModal-footer .Button',
        'username_input': 'input[name=identification]',
        'password_input': 'input[name=password]'
    }
    
    # 任务配置
    enable_signin: bool = True
    enable_reply: bool = True
    enable_feedback: bool = True
    
    # 回复策略
    max_daily_replies: int = 20
    reply_interval_min: int = 60
    reply_interval_max: int = 300
