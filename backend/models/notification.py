# backend/models/notification.py
class NotificationConfig:
    # Telegram
    tg_enabled: bool = False
    tg_bot_token: str = ""
    tg_user_id: str = ""
    tg_api_host: str = "https://api.telegram.org"
    
    # 企业微信
    wecom_enabled: bool = False
    wecom_key: str = ""
    
    # PushPlus
    pushplus_enabled: bool = False
    pushplus_token: str = ""
    
    # 邮件
    smtp_enabled: bool = False
    smtp_server: str = ""
    smtp_email: str = ""
    smtp_password: str = ""
    
    # Bark / Gotify / 钉钉等...
