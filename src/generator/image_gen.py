"""
配图生成模块
根据文章主题自动生成无文字配图，用于公众号封面/文章插图
"""
import logging
import os
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class ImageGenerator:
    """配图生成器"""

    def __init__(self, config: dict):
        self.enabled = config.get("enabled", True)
        self.style = config.get("style", "digital_art")
        self.aspect_ratio = config.get("aspect_ratio", "landscape_16_9")
        self.output_dir = config.get("output_dir", "data/images")
        self.brand_colors = config.get("brand_colors", ["#1a1a2e", "#16213e", "#0f3460", "#e94560"])
        self.brand_name = config.get("brand_name", "叶芝说")

        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_image_prompt(self, title: str, content: str, hotspot_title: str) -> str:
        """
        根据文章内容生成图片提示词（不带文字要求）
        """
        # 从文章中提取核心主题关键词
        content_snippet = content[:500] if content else title

        prompt = (
            f"Cover image for a tech commentary article about: {hotspot_title}. "
            f"Style: {self.style}, modern, clean composition, professional editorial illustration. "
            f"No text, no letters, no words, no typography in the image. "
            f"Color palette: deep navy blue, dark teal, with a vibrant accent color. "
            f"Mood: thoughtful, intellectual, slightly futuristic. "
            f"Abstract geometric elements combined with thematic visual metaphors. "
            f"High quality, 4K, suitable for a professional media publication cover."
        )
        return prompt

    def generate(self, title: str, content: str, hotspot_title: str,
                 generate_func=None) -> Optional[str]:
        """
        生成配图

        Args:
            title: 文章标题
            content: 文章正文
            hotspot_title: 热点标题
            generate_func: 实际的图片生成函数签名 (prompt, path, size) -> str
                          如果为None，则仅生成提示词不实际生成

        Returns:
            生成的图片路径，失败返回None
        """
        if not self.enabled:
            logger.info("配图生成已禁用")
            return None

        prompt = self.generate_image_prompt(title, content, hotspot_title)
        logger.info(f"配图提示词: {prompt[:100]}...")

        if generate_func is None:
            logger.info("未提供图片生成函数，跳过实际生成")
            return None

        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"cover_{timestamp}.png"
        filepath = os.path.join(self.output_dir, filename)

        try:
            result_path = generate_func(
                prompt=prompt,
                path=filepath,
                image_size=self.aspect_ratio,
            )
            logger.info(f"配图生成成功: {result_path}")
            return result_path
        except Exception as e:
            logger.error(f"配图生成失败: {e}")
            return None

    def get_image_for_wechat(self, title: str, content: str, hotspot_title: str,
                             generate_func=None) -> dict:
        """
        生成公众号所需的配图信息

        Returns:
            dict: {"cover_path": str, "prompt": str}
        """
        prompt = self.generate_image_prompt(title, content, hotspot_title)
        image_path = self.generate(title, content, hotspot_title, generate_func)

        return {
            "cover_path": image_path or "",
            "prompt": prompt,
        }
