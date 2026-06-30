"""
热点抓取基类
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class HotspotItem:
    """热点条目"""
    title: str                    # 热点标题
    source: str                   # 来源平台
    url: str = ""                 # 原文链接
    hot_score: float = 0.0        # 热度分数
    category: str = ""            # 分类
    summary: str = ""             # 摘要
    fetched_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    extra: dict = field(default_factory=dict)  # 额外信息
    
    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "source": self.source,
            "url": self.url,
            "hot_score": self.hot_score,
            "category": self.category,
            "summary": self.summary,
            "fetched_at": self.fetched_at,
            "extra": self.extra,
        }


class BaseFetcher(ABC):
    """热点抓取基类"""
    
    def __init__(self, config: dict, focus_keywords: List[str] = None):
        self.config = config
        self.focus_keywords = focus_keywords or []
    
    @abstractmethod
    def fetch(self) -> List[HotspotItem]:
        """抓取热点列表"""
        pass
    
    def filter_by_keywords(self, items: List[HotspotItem]) -> List[HotspotItem]:
        """根据关键词过滤和排序热点"""
        if not self.focus_keywords:
            return items
        
        scored_items = []
        for item in items:
            score = 0
            title_lower = item.title.lower()
            summary_lower = item.summary.lower()
            for keyword in self.focus_keywords:
                keyword_lower = keyword.lower()
                if keyword_lower in title_lower:
                    score += 10  # 标题匹配权重高
                if keyword_lower in summary_lower:
                    score += 5   # 摘要匹配
            item.hot_score = max(float(item.hot_score), float(score))
            scored_items.append(item)
        
        # 按热度分数排序，过滤掉分数为0的（无关键词匹配）
        filtered = [item for item in scored_items if item.hot_score > 0]
        filtered.sort(key=lambda x: x.hot_score, reverse=True)
        
        # 如果过滤后为空，返回原始列表（避免无内容可评论）
        return filtered if filtered else items
    
    def dedup(self, items: List[HotspotItem], published_titles: List[str]) -> List[HotspotItem]:
        """去除已发布的热点"""
        result = []
        for item in items:
            is_dup = False
            for published in published_titles:
                # 简单的标题相似度判断
                if item.title == published or \
                   (len(item.title) > 4 and published in item.title) or \
                   (len(published) > 4 and item.title in published):
                    is_dup = True
                    break
            if not is_dup:
                result.append(item)
        return result
