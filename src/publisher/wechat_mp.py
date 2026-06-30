"""
微信公众号发布模块
支持草稿箱模式和直接发布模式
"""
import logging
import time
import requests
from typing import Optional, Dict, Any
from ..generator.base import GeneratedComment

logger = logging.getLogger(__name__)


class WeChatMPPublisher:
    """微信公众号发布器"""
    
    API_BASE = "https://api.weixin.qq.com/cgi-bin"
    TOKEN_URL = f"{API_BASE}/token"
    DRAFT_URL = f"{API_BASE}/draft/add"
    PUBLISH_URL = f"{API_BASE}/freepublish/submit"
    UPLOAD_URL = f"{API_BASE}/media/uploadimg"
    
    def __init__(self, config: dict):
        self.app_id = config.get("app_id", "")
        self.app_secret = config.get("app_secret", "")
        self.draft_mode = config.get("draft_mode", True)
        self.cover_image = config.get("cover_image", "")
        self.category = config.get("category", "")
        
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0
    
    def _get_access_token(self) -> Optional[str]:
        """获取access_token（带缓存）"""
        # 如果缓存的token未过期，直接使用
        if self._access_token and time.time() < self._token_expires_at:
            return self._access_token
        
        try:
            url = f"{self.TOKEN_URL}?grant_type=client_credential&appid={self.app_id}&secret={self.app_secret}"
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if "access_token" in data:
                self._access_token = data["access_token"]
                # 提前5分钟过期，避免边界问题
                self._token_expires_at = time.time() + data.get("expires_in", 7200) - 300
                logger.info("微信公众号access_token获取成功")
                return self._access_token
            else:
                logger.error(f"获取access_token失败: {data.get('errmsg', '未知错误')}")
                return None
        
        except Exception as e:
            logger.error(f"获取access_token异常: {e}")
            return None
    
    def _upload_image(self, image_url: str = "") -> Optional[str]:
        """上传图片到公众号素材库，返回media_id或url"""
        token = self._get_access_token()
        if not token:
            logger.error("无法上传图片：未获取到access_token")
            return None
        
        # 如果提供了图片URL，先下载图片
        if image_url:
            try:
                img_response = requests.get(image_url, timeout=30)
                img_response.raise_for_status()
                files = {"media": ("image.jpg", img_response.content, "image/jpeg")}
            except Exception as e:
                logger.warning(f"下载图片失败: {e}")
                return None
        else:
            logger.warning("未提供图片URL")
            return None
        
        try:
            url = f"{self.UPLOAD_URL}?access_token={token}"
            response = requests.post(url, files=files, timeout=30)
            data = response.json()
            
            if "url" in data:
                logger.info(f"图片上传成功: {data['url']}")
                return data["url"]
            else:
                logger.error(f"图片上传失败: {data.get('errmsg', '未知错误')}")
                return None
        
        except Exception as e:
            logger.error(f"图片上传异常: {e}")
            return None
    
    def _html_format(self, comment: GeneratedComment) -> str:
        """将Markdown内容转换为公众号HTML格式"""
        content = comment.content
        
        # 基础HTML转换
        lines = content.split("\n")
        html_parts = []
        
        for line in lines:
            line = line.strip()
            if not line:
                html_parts.append("<br/>")
                continue
            
            # 处理标题
            if line.startswith("### "):
                html_parts.append(f'<h3 style="font-size:18px;font-weight:bold;margin:20px 0 10px;">{line[4:]}</h3>')
            elif line.startswith("## "):
                html_parts.append(f'<h2 style="font-size:20px;font-weight:bold;margin:25px 0 12px;">{line[3:]}</h2>')
            elif line.startswith("# "):
                html_parts.append(f'<h1 style="font-size:22px;font-weight:bold;margin:30px 0 15px;">{line[2:]}</h1>')
            # 处理加粗
            elif line.startswith("**") and line.endswith("**"):
                html_parts.append(f'<p style="font-weight:bold;margin:10px 0;">{line[2:-2]}</p>')
            # 处理引用
            elif line.startswith("> "):
                html_parts.append(f'<blockquote style="border-left:3px solid #ddd;padding-left:15px;color:#666;margin:15px 0;">{line[2:]}</blockquote>')
            # 处理无序列表
            elif line.startswith("- ") or line.startswith("* "):
                html_parts.append(f'<p style="margin:5px 0 5px 20px;">• {line[2:]}</p>')
            # 处理有序列表
            elif len(line) > 2 and line[0].isdigit() and line[1] in ". ":
                html_parts.append(f'<p style="margin:5px 0 5px 20px;">{line}</p>')
            # 普通段落
            else:
                # 处理行内加粗 **text**
                import re
                line = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line)
                html_parts.append(f'<p style="margin:10px 0;line-height:1.8;">{line}</p>')
        
        # 包裹整体样式
        html = f'''
<section style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;font-size:16px;color:#333;line-height:1.8;padding:10px;">
{''.join(html_parts)}
</section>
'''
        return html
    
    def publish(self, comment: GeneratedComment) -> Dict[str, Any]:
        """
        发布评论到公众号
        
        Returns:
            dict: {"success": bool, "media_id": str, "publish_id": str, "url": str, "message": str}
        """
        token = self._get_access_token()
        if not token:
            return {"success": False, "message": "获取access_token失败"}
        
        # 转换内容为HTML
        html_content = self._html_format(comment)
        
        # 上传封面图
        thumb_media_id = ""
        if self.cover_image:
            uploaded_url = self._upload_image(self.cover_image)
            if uploaded_url:
                thumb_media_id = uploaded_url
        
        # 构建草稿文章
        articles = [{
            "title": comment.title,
            "author": "叶芝说",
            "digest": comment.hotspot.summary[:120] if comment.hotspot.summary else comment.title,
            "content": html_content,
            "content_source_url": comment.hotspot.url,
            "thumb_media_id": thumb_media_id,
            "need_open_comment": 1,
            "only_fans_can_comment": 0,
        }]
        
        # 如果是草稿模式，先保存到草稿箱
        if self.draft_mode:
            return self._save_draft(token, articles, comment)
        else:
            return self._publish_directly(token, articles, comment)
    
    def _save_draft(self, token: str, articles: list, comment: GeneratedComment) -> Dict[str, Any]:
        """保存到草稿箱"""
        try:
            url = f"{self.DRAFT_URL}?access_token={token}"
            payload = {"articles": articles}
            response = requests.post(url, json=payload, timeout=30)
            data = response.json()
            
            if "media_id" in data:
                media_id = data["media_id"]
                logger.info(f"草稿保存成功，media_id: {media_id}")
                return {
                    "success": True,
                    "media_id": media_id,
                    "mode": "draft",
                    "message": f"草稿已保存，请在公众号后台审核后发布。media_id: {media_id}",
                    "title": comment.title,
                }
            else:
                errcode = data.get("errcode", "unknown")
                errmsg = data.get("errmsg", "未知错误")
                logger.error(f"草稿保存失败: [{errcode}] {errmsg}")
                return {
                    "success": False,
                    "message": f"草稿保存失败: [{errcode}] {errmsg}",
                }
        
        except Exception as e:
            logger.error(f"草稿保存异常: {e}")
            return {"success": False, "message": f"草稿保存异常: {e}"}
    
    def _publish_directly(self, token: str, articles: list, comment: GeneratedComment) -> Dict[str, Any]:
        """直接发布（先存草稿再发布）"""
        # 先保存草稿
        draft_result = self._save_draft(token, articles, comment)
        if not draft_result.get("success"):
            return draft_result
        
        media_id = draft_result["media_id"]
        
        # 提交发布
        try:
            url = f"{self.PUBLISH_URL}?access_token={token}"
            payload = {"media_id": media_id}
            response = requests.post(url, json=payload, timeout=30)
            data = response.json()
            
            if "publish_id" in data:
                publish_id = data["publish_id"]
                logger.info(f"文章发布成功，publish_id: {publish_id}")
                return {
                    "success": True,
                    "media_id": media_id,
                    "publish_id": publish_id,
                    "mode": "publish",
                    "message": f"文章已发布。publish_id: {publish_id}",
                    "title": comment.title,
                }
            else:
                errcode = data.get("errcode", "unknown")
                errmsg = data.get("errmsg", "未知错误")
                logger.error(f"文章发布失败: [{errcode}] {errmsg}")
                return {
                    "success": False,
                    "media_id": media_id,
                    "message": f"草稿已保存但发布失败: [{errcode}] {errmsg}。请手动在后台发布。",
                }
        
        except Exception as e:
            logger.error(f"文章发布异常: {e}")
            return {
                "success": False,
                "media_id": media_id,
                "message": f"草稿已保存但发布异常: {e}。请手动在后台发布。",
            }
    
    def publish_text_only(self, comment: GeneratedComment) -> Dict[str, Any]:
        """
        纯文本发布模式（无需封面图）
        适用于测试或无封面图场景
        """
        token = self._get_access_token()
        if not token:
            return {"success": False, "message": "获取access_token失败"}
        
        html_content = self._html_format(comment)
        
        articles = [{
            "title": comment.title,
            "author": "叶芝说",
            "digest": comment.hotspot.summary[:120] if comment.hotspot.summary else comment.title,
            "content": html_content,
            "content_source_url": comment.hotspot.url,
            "thumb_media_id": "",  # 无封面图
            "need_open_comment": 1,
            "only_fans_can_comment": 0,
        }]
        
        return self._save_draft(token, articles, comment)
