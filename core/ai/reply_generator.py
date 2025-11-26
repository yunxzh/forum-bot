"""
AI回复生成器
基于OpenAI API
"""
import openai
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class ReplyGenerator:
    def __init__(self, api_key: str, base_url: str, model: str, temperature: float = 0.8, max_tokens: int = 100):
        self.client = openai.OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    def generate_reply(self, title: str, content: str, min_length: int = 1, max_length: int = 10) -> Optional[str]:
        """
        生成回复内容
        """
        try:
            system_prompt = f"""你是一个友好的论坛用户，正在浏览论坛帖子并准备发表简短的回复。
回复要求：
1. 回复长度在{min_length}-{max_length}个字之间
2. 回复要自然、口语化，不要太正式
3. 回复要与帖子内容相关
4. 不要使用"作为AI"、"我认为"等表述
5. 可以使用emoji表情
6. 回复要简洁有力，一针见血
7. 如果是技术帖，可以简短提问或表达观点
8. 如果是分享帖，可以表达感谢或赞同
"""
            
            user_prompt = f"""帖子标题：{title}

帖子内容：{content}

请生成一个简短的回复（{min_length}-{max_length}字）："""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            reply = response.choices[0].message.content.strip()
            
            # 移除可能的引号
            if reply.startswith('"') and reply.endswith('"'):
                reply = reply[1:-1]
            if reply.startswith("'") and reply.endswith("'"):
                reply = reply[1:-1]
            
            logger.info(f"生成回复: {reply}")
            return reply
            
        except Exception as e:
            logger.error(f"生成回复失败: {e}")
            return None
    
    def analyze_sentiment(self, content: str) -> str:
        """
        分析内容情感
        返回: positive, negative, neutral
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个情感分析助手，分析文本情感并只返回: positive, negative 或 neutral"},
                    {"role": "user", "content": f"请分析以下文本的情感：\n{content}"}
                ],
                temperature=0.3,
                max_tokens=10
            )
            
            sentiment = response.choices[0].message.content.strip().lower()
            return sentiment if sentiment in ['positive', 'negative', 'neutral'] else 'neutral'
            
        except Exception as e:
            logger.error(f"情感分析失败: {e}")
            return 'neutral'
