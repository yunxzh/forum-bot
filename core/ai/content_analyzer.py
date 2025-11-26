"""
内容分析器
用于分析帖子内容，判断是否应该回复
"""
import re
from typing import Tuple
import logging

logger = logging.getLogger(__name__)

class ContentAnalyzer:
    # 跳过的关键词列表
    SKIP_KEYWORDS = [
        '广告', '推广', '加群', '微信', 'qq', 'QQ', '代理', '刷单', '兼职',
        '招聘', '出售', '购买', '低价', '优惠', '折扣', '红包', '赚钱',
        '投资', '理财', '股票', '期货', '贷款', '信用卡'
    ]
    
    @staticmethod
    def should_skip(title: str, content: str) -> Tuple[bool, str]:
        """
        判断是否应该跳过该帖子
        返回: (是否跳过, 原因)
        """
        # 检查标题和内容是否为空
        if not title or not title.strip():
            return True, "标题为空"
        
        if not content or not content.strip():
            return True, "内容为空"
        
        # 检查标题和内容长度
        if len(title.strip()) < 3:
            return True, "标题过短"
        
        if len(content.strip()) < 10:
            return True, "内容过短"
        
        # 检查是否包含广告关键词
        combined_text = (title + ' ' + content).lower()
        for keyword in ContentAnalyzer.SKIP_KEYWORDS:
            if keyword.lower() in combined_text:
                return True, f"包含广告关键词: {keyword}"
        
        # 检查是否包含过多链接
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, combined_text)
        if len(urls) > 3:
            return True, "包含过多链接"
        
        return False, ""
    
    @staticmethod
    def categorize(title: str, content: str) -> str:
        """
        对帖子进行分类
        返回: 分类标签 (tech, share, question, discussion, other)
        """
        combined_text = (title + ' ' + content).lower()
        
        # 技术类关键词
        tech_keywords = ['代码', 'code', '编程', '开发', 'api', '服务器', 'server', 'bug', '错误', '部署']
        if any(keyword in combined_text for keyword in tech_keywords):
            return 'tech'
        
        # 分享类关键词
        share_keywords = ['分享', 'share', '推荐', '发现', '资源', '工具', '网站']
        if any(keyword in combined_text for keyword in share_keywords):
            return 'share'
        
        # 提问类关键词
        question_keywords = ['怎么', '如何', '为什么', '?', '？', '求助', '请问', '有没有']
        if any(keyword in combined_text for keyword in question_keywords):
            return 'question'
        
        # 讨论类关键词
        discussion_keywords = ['讨论', '觉得', '认为', '看法', '观点']
        if any(keyword in combined_text for keyword in discussion_keywords):
            return 'discussion'
        
        return 'other'
    
    @staticmethod
    def extract_keywords(text: str, top_n: int = 5) -> list:
        """
        提取关键词（简单实现）
        """
        # 移除标点符号
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # 分词（简单按空格分割）
        words = text.split()
        
        # 统计词频
        word_freq = {}
        for word in words:
            word = word.strip().lower()
            if len(word) > 1:  # 过滤单字
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # 排序并返回top_n
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:top_n]]
