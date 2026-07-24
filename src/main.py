"""
叶芝说·实时评论AI助手 - 主入口
每天自动抓取科技热点 → 生成锐评 → 发布到公众号
"""
import argparse
import logging
import os
import sys

# 将项目根目录加入路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.utils import setup_logging, load_config, load_published_record, save_published_record, save_comment_to_file
from src.fetcher.weibo import WeiboFetcher
from src.fetcher.news import NewsFetcher
from src.generator.openai_gen import OpenAIGenerator
from src.generator.claude_gen import ClaudeGenerator
from src.generator.image_gen import ImageGenerator
from src.publisher.wechat_mp import WeChatMPPublisher
from src.scheduler import TaskScheduler

logger = logging.getLogger("yeats")


class YeatsBot:
    """叶芝说评论机器人"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = load_config(config_path)
        self.config_path = config_path
        
        # 初始化各模块
        self._init_fetchers()
        self._init_generator()
        self._init_image_generator()
        self._init_publisher()
        
        # 加载已发布记录
        record_file = self.config.get("general", {}).get(
            "published_record", "data/published.json"
        )
        self.published_titles = load_published_record(record_file)
        self.record_file = record_file
    
    def _init_fetchers(self):
        """初始化热点抓取器"""
        hotspot_config = self.config.get("hotspot", {})
        focus_keywords = hotspot_config.get("focus_keywords", [])
        
        self.fetchers = []
        
        # 微博热搜
        weibo_config = hotspot_config.get("weibo", {})
        if weibo_config.get("enabled", True):
            self.fetchers.append(WeiboFetcher(weibo_config, focus_keywords))
            logger.info("微博热搜抓取器已初始化")
        
        # 新闻API
        news_config = hotspot_config.get("news", {})
        if news_config.get("enabled", True):
            self.fetchers.append(NewsFetcher(news_config, focus_keywords))
            logger.info("新闻热点抓取器已初始化")
    
    def _init_generator(self):
        """初始化评论生成器"""
        ai_config = self.config.get("ai", {})
        comment_config = self.config.get("comment", {})
        default_model = ai_config.get("default_model", "openai")
        
        self.generators = {}
        
        # OpenAI
        openai_config = ai_config.get("openai", {})
        if openai_config.get("api_key") and "your-" not in openai_config.get("api_key", ""):
            self.generators["openai"] = OpenAIGenerator(openai_config, comment_config)
            logger.info(f"OpenAI生成器已初始化 (model: {openai_config.get('model', 'gpt-4o')})")
        
        # Claude
        claude_config = ai_config.get("claude", {})
        if claude_config.get("api_key") and "sk-ant-your-" not in claude_config.get("api_key", ""):
            self.generators["claude"] = ClaudeGenerator(claude_config, comment_config)
            logger.info(f"Claude生成器已初始化 (model: {claude_config.get('model', 'claude-sonnet-4-20250514')})")
        
        self.default_model = default_model
        
        if not self.generators:
            logger.error("⚠️  未配置任何AI模型！请在config.yaml中配置OpenAI或Claude的API密钥")
    
    def _init_image_generator(self):
        """初始化配图生成器"""
        image_config = self.config.get("image", {})
        self.image_generator = ImageGenerator(image_config)
        if image_config.get("enabled", True):
            logger.info("配图生成器已初始化")
        else:
            logger.info("配图生成已禁用")
    
    def _init_publisher(self):
        """初始化发布器"""
        mp_config = self.config.get("wechat_mp", {})
        self.publisher = None
        
        if mp_config.get("enabled", True) and mp_config.get("app_id"):
            if "your-" not in mp_config.get("app_id", ""):
                self.publisher = WeChatMPPublisher(mp_config)
                mode = "草稿箱" if mp_config.get("draft_mode", True) else "直接发布"
                logger.info(f"公众号发布器已初始化 (模式: {mode})")
            else:
                logger.warning("⚠️  公众号AppID未配置，将仅生成评论不发布")
        else:
            logger.warning("⚠️  公众号发布未启用，将仅生成评论不发布")
    
    def fetch_hotspots(self):
        """抓取所有热点源"""
        all_hotspots = []
        
        for fetcher in self.fetchers:
            try:
                items = fetcher.fetch()
                all_hotspots.extend(items)
            except Exception as e:
                logger.error(f"抓取器 {fetcher.__class__.__name__} 执行失败: {e}")
        
        # 去重（按标题）
        seen_titles = set()
        unique_hotspots = []
        for item in all_hotspots:
            if item.title not in seen_titles:
                seen_titles.add(item.title)
                unique_hotspots.append(item)
        
        # 按热度排序
        unique_hotspots.sort(key=lambda x: x.hot_score, reverse=True)
        
        # 去除已发布的热点
        if self.config.get("general", {}).get("auto_dedup", True):
            unique_hotspots = fetcher.dedup(unique_hotspots, self.published_titles) if self.fetchers else unique_hotspots
        
        logger.info(f"共获取 {len(unique_hotspots)} 条不重复热点")
        return unique_hotspots
    
    def generate_comment(self, hotspot):
        """生成评论"""
        # 选择生成器
        model_name = self.default_model
        generator = self.generators.get(model_name)
        
        if not generator:
            # 回退到可用的生成器
            available = list(self.generators.keys())
            if available:
                model_name = available[0]
                generator = self.generators[model_name]
                logger.warning(f"默认模型 {self.default_model} 不可用，回退到 {model_name}")
            else:
                logger.error("没有可用的AI生成器")
                return None
        
        # 确定目标平台
        platform = "wechat"
        
        # 生成评论
        comment = generator.generate(hotspot, platform)
        return comment
    
    def publish_comment(self, comment):
        """发布评论"""
        if not self.publisher:
            logger.info("发布器未配置，跳过发布")
            return {"success": False, "message": "发布器未配置"}
        
        # 如果有配图，传递给发布器
        if hasattr(comment, 'cover_image') and comment.cover_image:
            self.publisher.cover_image = comment.cover_image
        
        result = self.publisher.publish(comment)
        return result
    
    def _generate_image_func(self, prompt, path, image_size):
        """
        图片生成回调函数
        在实际部署时，可替换为OpenAI DALL-E或其他图片生成API的调用
        """
        import requests
        
        ai_config = self.config.get("ai", {})
        openai_config = ai_config.get("openai", {})
        api_key = openai_config.get("api_key", "")
        base_url = openai_config.get("base_url", "https://api.openai.com/v1").rstrip("/v1")
        
        if not api_key or "your-" in api_key:
            logger.warning("未配置OpenAI API密钥，无法生成配图")
            return None
        
        try:
            # 使用DALL-E 3生成图片
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            
            # 映射尺寸
            size_map = {
                "landscape_16_9": "1792x1024",
                "landscape_4_3": "1792x1024",
                "square_hd": "1024x1024",
                "portrait_4_3": "1024x1024",
            }
            dall_e_size = size_map.get(image_size, "1792x1024")
            
            payload = {
                "model": "dall-e-3",
                "prompt": prompt,
                "n": 1,
                "size": dall_e_size,
                "quality": "standard",
            }
            
            response = requests.post(
                f"{base_url}/v1/images/generations",
                headers=headers,
                json=payload,
                timeout=120,
            )
            response.raise_for_status()
            data = response.json()
            
            # 下载图片
            image_url = data["data"][0]["url"]
            img_response = requests.get(image_url, timeout=60)
            img_response.raise_for_status()
            
            with open(path, "wb") as f:
                f.write(img_response.content)
            
            return path
        
        except Exception as e:
            logger.error(f"DALL-E图片生成失败: {e}")
            return None
    
    def run(self):
        """执行一次完整的评论生成流程"""
        logger.info("=" * 60)
        logger.info("叶芝说·实时评论AI助手 开始运行")
        logger.info("=" * 60)
        
        # Step 1: 抓取热点
        logger.info("\n📡 Step 1: 抓取热点...")
        hotspots = self.fetch_hotspots()
        
        if not hotspots:
            logger.warning("未获取到任何热点，本次运行结束")
            return
        
        # Step 2: 选择热点（取热度最高的N条）
        comments_per_run = self.config.get("general", {}).get("comments_per_run", 1)
        selected_hotspots = hotspots[:comments_per_run]
        
        logger.info(f"\n🎯 Step 2: 已选择 {len(selected_hotspots)} 条热点进行评论")
        for i, h in enumerate(selected_hotspots, 1):
            logger.info(f"  {i}. [{h.source}] {h.title} (热度: {h.hot_score})")
        
        # Step 3: 生成评论
        logger.info("\n✍️  Step 3: 生成评论...")
        for i, hotspot in enumerate(selected_hotspots, 1):
            logger.info(f"\n--- 处理第 {i}/{len(selected_hotspots)} 条热点 ---")
            logger.info(f"热点: {hotspot.title}")
            
            comment = self.generate_comment(hotspot)
            
            if not comment:
                logger.error(f"评论生成失败: {hotspot.title}")
                continue
            
            logger.info(f"标题: {comment.title}")
            logger.info(f"字数: {len(comment.content)}")
            
            # 保存评论到文件
            filepath = save_comment_to_file(comment)
            logger.info(f"评论已保存: {filepath}")
            
            # Step 3.5: 生成配图
            logger.info("\n🎨 Step 3.5: 生成配图...")
            image_info = self.image_generator.get_image_for_wechat(
                title=comment.title,
                content=comment.content,
                hotspot_title=hotspot.title,
                generate_func=self._generate_image_func,
            )
            cover_path = image_info.get("cover_path", "")
            if cover_path:
                logger.info(f"配图已生成: {cover_path}")
                # 将配图路径附加到评论对象上，供发布器使用
                comment.cover_image = cover_path
            else:
                logger.info("配图未生成（可能未配置图片生成函数）")
            
            # Step 4: 发布
            logger.info("\n📤 Step 4: 发布评论...")
            result = self.publish_comment(comment)
            
            if result.get("success"):
                logger.info(f"✅ 发布成功: {result.get('message', '')}")
                # 记录已发布
                self.published_titles.append(hotspot.title)
                save_published_record(self.record_file, self.published_titles)
            else:
                logger.warning(f"⚠️  发布未成功: {result.get('message', '')}")
                logger.info("评论已保存到本地文件，可手动发布")
        
        logger.info("\n" + "=" * 60)
        logger.info("叶芝说·实时评论AI助手 本次运行完成")
        logger.info("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="叶芝说·实时评论AI助手")
    parser.add_argument(
        "--config", "-c",
        default="config/config.yaml",
        help="配置文件路径 (默认: config/config.yaml)"
    )
    parser.add_argument(
        "--schedule", "-s",
        action="store_true",
        help="启用定时调度模式"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="试运行模式：只生成评论不发布"
    )
    args = parser.parse_args()
    
    # 加载配置并初始化日志
    config = load_config(args.config)
    logger = setup_logging(config)
    
    # 创建机器人实例
    bot = YeatsBot(args.config)
    
    if args.dry_run:
        logger.info("🔧 试运行模式：将只生成评论，不发布到公众号")
        if bot.publisher:
            bot.publisher = None
    
    if args.schedule:
        # 定时调度模式
        scheduler = TaskScheduler(config)
        scheduler.run_loop(bot.run)
    else:
        # 单次运行
        bot.run()


if __name__ == "__main__":
    main()
