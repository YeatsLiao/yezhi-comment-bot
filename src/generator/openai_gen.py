"""
OpenAI评论生成器
"""
import logging
from typing import Optional
from openai import OpenAI
from .base import BaseGenerator, GeneratedComment
from ..fetcher.base import HotspotItem

logger = logging.getLogger(__name__)


class OpenAIGenerator(BaseGenerator):
    """OpenAI GPT评论生成器"""
    
    def __init__(self, config: dict, comment_config: dict):
        super().__init__(config, comment_config)
        self.api_key = config.get("api_key", "")
        self.model = config.get("model", "gpt-4o")
        self.base_url = config.get("base_url", "https://api.openai.com/v1")
        self.max_tokens = config.get("max_tokens", 2000)
        self.temperature = config.get("temperature", 0.8)
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )
    
    def generate(self, hotspot: HotspotItem, platform: str = "wechat") -> Optional[GeneratedComment]:
        """使用OpenAI生成评论"""
        try:
            system_prompt = self.build_system_prompt(platform)
            user_prompt = self.build_user_prompt(hotspot, platform)
            
            logger.info(f"使用OpenAI {self.model} 生成评论，热点: {hotspot.title}")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            
            response_text = response.choices[0].message.content
            logger.info(f"OpenAI生成完成，字数: {len(response_text)}")
            
            return self.parse_response(response_text, hotspot, platform, self.model)
        
        except Exception as e:
            logger.error(f"OpenAI生成失败: {e}")
            return None
