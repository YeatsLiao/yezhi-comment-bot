"""
Claude评论生成器
"""
import logging
from typing import Optional
from anthropic import Anthropic
from .base import BaseGenerator, GeneratedComment
from ..fetcher.base import HotspotItem

logger = logging.getLogger(__name__)


class ClaudeGenerator(BaseGenerator):
    """Claude评论生成器"""
    
    def __init__(self, config: dict, comment_config: dict):
        super().__init__(config, comment_config)
        self.api_key = config.get("api_key", "")
        self.model = config.get("model", "claude-sonnet-4-20250514")
        self.max_tokens = config.get("max_tokens", 2000)
        self.temperature = config.get("temperature", 0.8)
        
        self.client = Anthropic(api_key=self.api_key)
    
    def generate(self, hotspot: HotspotItem, platform: str = "wechat") -> Optional[GeneratedComment]:
        """使用Claude生成评论"""
        try:
            system_prompt = self.build_system_prompt(platform)
            user_prompt = self.build_user_prompt(hotspot, platform)
            
            logger.info(f"使用Claude {self.model} 生成评论，热点: {hotspot.title}")
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt},
                ],
            )
            
            response_text = response.content[0].text
            logger.info(f"Claude生成完成，字数: {len(response_text)}")
            
            return self.parse_response(response_text, hotspot, platform, self.model)
        
        except Exception as e:
            logger.error(f"Claude生成失败: {e}")
            return None
