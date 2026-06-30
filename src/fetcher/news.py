"""
新闻热点抓取器
支持多种新闻源：36氪、知乎热榜、头条、IT之家等
支持RSS源、NewsAPI、以及直接网页抓取三种方式
"""
import json
import logging
import re
import requests
import feedparser
from typing import List
from .base import BaseFetcher, HotspotItem

logger = logging.getLogger(__name__)


class NewsFetcher(BaseFetcher):
    """新闻热点抓取器"""
    
    # 各新闻源的RSS地址
    RSS_SOURCES = {
        "36kr": "https://rsshub.app/36kr/hot-list",
        "zhihu": "https://rsshub.app/zhihu/hotlist",
        "toutiao": "https://rsshub.app/toutiao/hot",
        "ithome": "https://rsshub.app/ithome/ranking/daily",
        "huxiu": "https://rsshub.app/huxiu/article",
        "jiqizhixin": "https://rsshub.app/jiqizhixin/daily",
    }
    
    # 直接抓取的API地址（不依赖RSSHub）
    DIRECT_API_SOURCES = {
        "36kr": "https://36kr.com/api/newsflash",
        "zhihu": "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total?limit=20",
        "toutiao": "https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc",
        "ithome": "https://m.ithome.com/api/news/newslistpage?type=0&page=1&ot=0",
    }
    
    def __init__(self, config: dict, focus_keywords: List[str] = None):
        super().__init__(config, focus_keywords)
        self.provider = config.get("provider", "36kr")
        self.rss_url = config.get("rss_url", self.RSS_SOURCES.get(self.provider, ""))
        self.max_items = config.get("max_items", 30)
        self.newsapi_config = config.get("newsapi", {})
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }
    
    def fetch(self) -> List[HotspotItem]:
        """抓取新闻热点"""
        items = []
        
        # 优先使用RSS源
        if self.rss_url:
            items = self._fetch_from_rss(self.rss_url, self.provider)
        
        # 如果主源失败，尝试备用源
        if not items:
            for source_name, rss_url in self.RSS_SOURCES.items():
                if source_name != self.provider:
                    logger.info(f"尝试备用新闻源: {source_name}")
                    items = self._fetch_from_rss(rss_url, source_name)
                    if items:
                        break
        
        # 尝试NewsAPI
        if not items and self.newsapi_config.get("api_key"):
            items = self._fetch_from_newsapi()
        
        # 最后尝试直接API抓取（不依赖RSSHub）
        if not items:
            for source_name, api_url in self.DIRECT_API_SOURCES.items():
                logger.info(f"尝试直接API抓取: {source_name}")
                items = self._fetch_from_direct_api(api_url, source_name)
                if items:
                    break
        
        if items:
            logger.info(f"新闻热点抓取成功，共 {len(items)} 条")
            items = self.filter_by_keywords(items)
            logger.info(f"关键词过滤后剩余 {len(items)} 条")
        else:
            logger.warning("新闻热点抓取失败，所有源均不可用")
        
        return items[:self.max_items]
    
    def _fetch_from_rss(self, rss_url: str, source_name: str) -> List[HotspotItem]:
        """通过RSS源抓取新闻"""
        items = []
        try:
            feed = feedparser.parse(rss_url)
            
            if not feed.entries:
                logger.warning(f"RSS源 {source_name} 返回空数据")
                return []
            
            for idx, entry in enumerate(feed.entries):
                title = entry.get("title", "").strip()
                if not title:
                    continue
                
                # 清理标题
                title = re.sub(r'\s+', ' ', title).strip()
                
                # 提取摘要
                summary = entry.get("summary", "")
                # 去除HTML标签
                summary = re.sub(r'<[^>]+>', '', summary).strip()
                # 截断过长摘要
                if len(summary) > 200:
                    summary = summary[:200] + "..."
                
                hotspot = HotspotItem(
                    title=title,
                    source=source_name,
                    url=entry.get("link", ""),
                    hot_score=max(0, 500 - idx * 5),  # 用排名模拟热度
                    category="科技",
                    summary=summary,
                    extra={
                        "rank": idx + 1,
                        "published": entry.get("published", ""),
                    }
                )
                items.append(hotspot)
            
            return items
        
        except Exception as e:
            logger.warning(f"RSS源 {source_name} 抓取失败: {e}")
            return []
    
    def _fetch_from_newsapi(self) -> List[HotspotItem]:
        """通过NewsAPI抓取新闻"""
        items = []
        try:
            api_key = self.newsapi_config.get("api_key")
            url = self.newsapi_config.get("url", "https://newsapi.org/v2/top-headlines")
            
            params = {
                "apiKey": api_key,
                "country": "cn",
                "category": "technology",
                "pageSize": self.max_items,
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            for idx, article in enumerate(data.get("articles", [])):
                title = article.get("title", "").strip()
                if not title:
                    continue
                
                hotspot = HotspotItem(
                    title=title,
                    source="NewsAPI",
                    url=article.get("url", ""),
                    hot_score=0,
                    category="科技",
                    summary=article.get("description", "") or "",
                    extra={
                        "source_name": article.get("source", {}).get("name", ""),
                        "published_at": article.get("publishedAt", ""),
                    }
                )
                items.append(hotspot)
            
            return items
        
        except Exception as e:
            logger.warning(f"NewsAPI抓取失败: {e}")
            return []
    
    def _fetch_from_direct_api(self, api_url: str, source_name: str) -> List[HotspotItem]:
        """直接通过API抓取新闻（不依赖RSSHub）"""
        items = []
        try:
            response = requests.get(api_url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            if source_name == "36kr":
                data = response.json()
                flash_list = data.get("data", {}).get("list", [])
                for idx, item in enumerate(flash_list):
                    title = item.get("title", "").strip()
                    if not title:
                        continue
                    hotspot = HotspotItem(
                        title=title,
                        source="36氪",
                        url=f"https://36kr.com/newsflashes/{item.get('id', '')}",
                        hot_score=max(0, 500 - idx * 5),
                        category="科技",
                        summary=item.get("description", "")[:200],
                        extra={"rank": idx + 1}
                    )
                    items.append(hotspot)
            
            elif source_name == "zhihu":
                data = response.json()
                for idx, item in enumerate(data.get("data", [])):
                    target = item.get("target", {})
                    title = target.get("title", "").strip()
                    if not title:
                        continue
                    hotspot = HotspotItem(
                        title=title,
                        source="知乎热榜",
                        url=target.get("url", ""),
                        hot_score=item.get("detail_text", "").replace("万热度", "").strip() or 0,
                        category="科技",
                        summary=target.get("excerpt", "")[:200],
                        extra={"rank": idx + 1}
                    )
                    items.append(hotspot)
            
            elif source_name == "toutiao":
                data = response.json()
                for idx, item in enumerate(data.get("data", [])):
                    title = item.get("Title", "").strip()
                    if not title:
                        continue
                    hotspot = HotspotItem(
                        title=title,
                        source="今日头条",
                        url=item.get("Url", ""),
                        hot_score=item.get("HotValue", 0),
                        category="科技",
                        summary="",
                        extra={"rank": idx + 1}
                    )
                    items.append(hotspot)
            
            elif source_name == "ithome":
                data = response.json()
                news_list = data.get("Data", {}).get("List", []) or data.get("newsList", [])
                if isinstance(news_list, list):
                    for idx, item in enumerate(news_list):
                        title = item.get("title", "") or item.get("Title", "").strip()
                        if not title:
                            continue
                        hotspot = HotspotItem(
                            title=title,
                            source="IT之家",
                            url=item.get("url", "") or item.get("Url", ""),
                            hot_score=max(0, 300 - idx * 5),
                            category="科技",
                            summary=(item.get("description", "") or item.get("summary", ""))[:200],
                            extra={"rank": idx + 1}
                        )
                        items.append(hotspot)
            
            return items
        
        except Exception as e:
            logger.warning(f"直接API抓取 {source_name} 失败: {e}")
            return []
