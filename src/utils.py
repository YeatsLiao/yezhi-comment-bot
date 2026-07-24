"""
工具函数
"""
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional


def setup_logging(config: dict) -> logging.Logger:
    """配置日志"""
    log_config = config.get("logging", {})
    log_level = getattr(logging, log_config.get("level", "INFO").upper())
    log_file = log_config.get("file", "logs/yeats-bot.log")
    
    # 确保日志目录存在
    log_dir = os.path.dirname(log_file)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
    
    # 配置根logger
    logger = logging.getLogger("yeats")
    logger.setLevel(log_level)
    
    # 控制台handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_format = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # 文件handler
    try:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(log_level)
        file_handler.setFormatter(console_format)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"无法创建日志文件 {log_file}: {e}")
    
    return logger


def load_config(config_path: str = "config/config.yaml") -> dict:
    """加载配置文件"""
    import yaml
    
    # 尝试加载用户配置
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        return config
    
    # 尝试加载示例配置
    example_path = config_path.replace("config.yaml", "config.example.yaml")
    if os.path.exists(example_path):
        with open(example_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        print(f"⚠️  未找到 {config_path}，使用示例配置 {example_path}")
        print(f"⚠️  请复制 config.example.yaml 为 config.yaml 并填入真实配置")
        return config
    
    raise FileNotFoundError(f"配置文件不存在: {config_path}")


def load_published_record(record_file: str) -> List[str]:
    """加载已发布热点记录"""
    if os.path.exists(record_file):
        try:
            with open(record_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("published_titles", [])
        except (json.JSONDecodeError, KeyError):
            return []
    return []


def save_published_record(record_file: str, titles: List[str]):
    """保存已发布热点记录"""
    record_dir = os.path.dirname(record_file)
    if record_dir:
        os.makedirs(record_dir, exist_ok=True)
    
    data = {
        "published_titles": titles,
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    
    with open(record_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def save_comment_to_file(comment, output_dir: str = "data") -> str:
    """保存评论到文件"""
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"comment_{timestamp}.md"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# {comment.title}\n\n")
        f.write(f"> 来源: {comment.hotspot.source} | 热点: {comment.hotspot.title}\n\n")
        f.write(f"> 链接: {comment.hotspot.url}\n\n")
        f.write("---\n\n")
        f.write(comment.content)
        f.write(f"\n\n---\n*生成时间: {comment.hotspot.fetched_at} | 模型: {comment.model}*")
    
    return filepath
