"""
微博热搜抓取器
支持多种方式获取微博热搜数据
"""
import json
import logging
import re
import requests
import feedparser
from typing import List, Optional
from .base import BaseFetcher, HotspotItem

logger = logging.getLogger(__name__)


class WeiboFetcher(BaseFetcher):
    """微博热搜抓取器"""
    
    # 微博热搜分类
    CATEGORIES = {
        "热搜": "hot",
        "科技": "tech",
        "财经": "finance",
    }
    
    def __init__(self, config: dict, focus_keywords: List[str] = None):
        super().__init__(config, focus_keywords)
        self.api_url = config.get("api_url", "https://weibo.com/ajax/side/hotSearch")
        self.rss_url = config.get("rss_url", "https://rsshub.app/weibo/hot")
        self.max_items = config.get("max_items", 50)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://weibo.com/",
        }
    
    def fetch(self) -> List[HotspotItem]:
        """抓取微博热搜，优先使用API，失败则使用RSS"""
        items = self._fetch_from_api()
        if not items:
            logger.info("微博API抓取失败，尝试RSS源...")
            items = self._fetch_from_rss()
        
        if items:
            logger.info(f"微博热搜抓取成功，共 {len(items)} 条")
            items = self.filter_by_keywords(items)
            logger.info(f"关键词过滤后剩余 {len(items)} 条")
        else:
            logger.warning("微博热搜抓取失败，所有源均不可用")
        
        return items[:self.max_items]
    
    def _fetch_from_api(self) -> List[HotspotItem]:
        """通过微博API抓取热搜"""
        items = []
        try:
            response = requests.get(self.api_url, headers=self.headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if data.get("ok") == 1:
                realtime = data.get("data", {}).get("realtime", [])
                for idx, item in enumerate(realtime):
                    try:
                        word = item.get("word", "")
                        # 过滤广告和推广
                        if word.startswith("广告") or word.startswith("推广"):
                            continue
                        # 提取热搜排名数字
                        label_name = item.get("label_name", "")
                        num_str = item.get("num", "0")
                        
                        hotspot = HotspotItem(
                            title=word,
                            source="微博热搜",
                            url=f"https://s.weibo.com/weibo?q={word}",
                            hot_score=float(num_str) if num_str else 0,
                            category=label_name if label_name else "热搜",
                            summary=f"微博热搜第{idx+1}名",
                            extra={
                                "rank": idx + 1,
                                "label_name": label_name,
                                "raw_num": num_str,
                            }
                        )
                        items.append(hotspot)
                    except Exception as e:
                        logger.debug(f"解析微博热搜条目失败: {e}")
                        continue
                
            return items
        
        except requests.RequestException as e:
            logger.warning(f"微博API请求失败: {e}")
            return []
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"微博API数据解析失败: {e}")
            return []
    
    def _fetch_from_rss(self) -> List[HotspotItem]:
        """通过RSS源抓取热搜"""
        items = []
        try:
            feed = feedparser.parse(self.rss_url)
            
            for idx, entry in enumerate(feed.entries):
                title = entry.get("title", "").strip()
                if not title:
                    continue
                
                # 从标题中提取排名和热度
                rank = idx + 1
                hot_score = 0
                
                # 尝试从标题中提取排名数字（格式如 "1. xxx"）
                match = re.match(r'^(\d+)\.\s*(.+)', title)
                if match:
                    rank = int(match.group(1))
                    title = match.group(2)
                
                hotspot = HotspotItem(
                    title=title,
                    source="微博热搜(RSS)",
                    url=entry.get("link", ""),
                    hot_score=max(0, 1000 - rank * 10),  # RSS无热度数据，用排名模拟
                    category="热搜",
                    summary=entry.get("summary", ""),
                    extra={"rank": rank}
                )
                items.append(hotspot)
            
            return items
        
        except Exception as e:
            logger.warning(f"微博RSS抓取失败: {e}")
            return []
