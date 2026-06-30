"""
评论生成基类
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
from ..fetcher.base import HotspotItem


@dataclass
class GeneratedComment:
    """生成的评论"""
    title: str               # 文章标题
    content: str             # 文章正文（Markdown格式）
    hotspot: HotspotItem     # 关联的热点
    platform: str = "wechat" # 目标平台
    model: str = ""          # 使用的模型
    cover_image: str = ""    # 配图路径
    
    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "content": self.content,
            "platform": self.platform,
            "model": self.model,
            "hotspot": self.hotspot.to_dict(),
        }


class BaseGenerator(ABC):
    """评论生成基类"""
    
    def __init__(self, config: dict, comment_config: dict):
        self.config = config
        self.comment_config = comment_config
        self.identity_tags = comment_config.get("identity_tags", [])
        self.style = comment_config.get("style", {})
        self.style_samples = comment_config.get("style_samples", [])
        self.platform_styles = comment_config.get("platform_styles", {})
    
    @abstractmethod
    def generate(self, hotspot: HotspotItem, platform: str = "wechat") -> GeneratedComment:
        """生成评论"""
        pass
    
    def build_system_prompt(self, platform: str = "wechat") -> str:
        """构建系统提示词"""
        identity = "、".join(self.identity_tags) if self.identity_tags else "科技评论员"
        style = self.style
        
        prompt = f"""你是「叶芝说」，一个{identity}。

## 你的写作风格
- 语气：{style.get('tone', '犀利但不失温度')}
- 视角：{style.get('perspective', '技术专家+生活观察者')}
- 结构：{style.get('structure', '观点先行，论据支撑，结尾升华')}
- 篇幅：{style.get('length', '800-1500字')}

## 写作要求
1. 开篇直接亮明观点，不要铺垫和废话
2. 用具体数据和案例支撑论点，避免空洞说教
3. 语言生动有力，善用比喻和类比
4. 结尾要有升华或引发思考的金句
5. 保持独立思考，不随波逐流，敢于提出不同观点
6. 避免使用"笔者认为""众所周知"等陈词滥调
"""
        
        # 添加平台风格适配
        platform_style = self.platform_styles.get(platform, {})
        if platform_style:
            prompt += f"\n## {platform}平台风格要求\n"
            if platform_style.get("title_style"):
                prompt += f"- 标题风格：{platform_style['title_style']}\n"
            if platform_style.get("body_style"):
                prompt += f"- 正文风格：{platform_style['body_style']}\n"
            if platform_style.get("ending_style"):
                prompt += f"- 结尾风格：{platform_style['ending_style']}\n"
            if platform_style.get("emoji_usage"):
                prompt += f"- Emoji使用：{platform_style['emoji_usage']}\n"
        
        # 添加风格参考样本
        if self.style_samples:
            prompt += "\n## 风格参考（请模仿以下写作风格）\n"
            for i, sample in enumerate(self.style_samples, 1):
                prompt += f"\n### 参考文章{i}\n{sample}\n"
        
        return prompt
    
    def build_user_prompt(self, hotspot: HotspotItem, platform: str = "wechat") -> str:
        """构建用户提示词"""
        prompt = f"请针对以下热点事件写一篇锐评：\n\n"
        prompt += f"**热点标题**：{hotspot.title}\n"
        if hotspot.summary:
            prompt += f"**事件摘要**：{hotspot.summary}\n"
        prompt += f"**来源**：{hotspot.source}\n"
        if hotspot.url:
            prompt += f"**链接**：{hotspot.url}\n"
        
        prompt += f"\n请生成：\n"
        prompt += f"1. 一个吸引人的标题（15字以内）\n"
        prompt += f"2. 正文内容（{self.style.get('length', '800-1500字')}）\n"
        prompt += f"\n输出格式：\n"
        prompt += f"标题：xxx\n"
        prompt += f"正文：\nxxx\n"
        
        return prompt
    
    def parse_response(self, response_text: str, hotspot: HotspotItem, platform: str, model: str) -> GeneratedComment:
        """解析AI响应"""
        title = ""
        content = response_text.strip()
        
        # 尝试提取标题
        lines = content.split("\n")
        for i, line in enumerate(lines):
            line = line.strip()
            # 匹配 "标题：xxx" 或 "## xxx" 或 "# xxx" 格式
            if line.startswith("标题") and ("：" in line or ":" in line):
                title = line.split("：", 1)[-1].split(":", 1)[-1].strip()
                # 移除标题行和可能的分隔线
                remaining_lines = []
                for j in range(i + 1, len(lines)):
                    if lines[j].strip() and not lines[j].strip().startswith("---"):
                        remaining_lines.append(lines[j])
                content = "\n".join(remaining_lines).strip()
                break
            elif line.startswith("## ") or line.startswith("# "):
                title = line.lstrip("#").strip()
                remaining_lines = lines[i+1:]
                content = "\n".join(remaining_lines).strip()
                break
        
        # 如果没有提取到标题，用热点标题
        if not title:
            title = f"叶芝说：{hotspot.title}"
        
        # 清理正文中的 "正文：" 前缀
        if content.startswith("正文") and ("：" in content or ":" in content):
            content = content.split("：", 1)[-1].split(":", 1)[-1].strip()
        
        return GeneratedComment(
            title=title,
            content=content,
            hotspot=hotspot,
            platform=platform,
            model=model,
        )
