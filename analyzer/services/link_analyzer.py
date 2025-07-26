import re
from typing import Dict, List, Optional
from urllib.parse import urlparse, parse_qs, unquote

from models.data_models import LinkInfo
from utils.logger import logger
from .url_resolver import URLResolver

class LinkAnalyzer:
    """کلاس تحلیل لینک‌ها"""
    
    def __init__(self):
        self.redirect_mapping: Dict[str, str] = {}
        self.url_resolver: Optional[URLResolver] = None
    
    async def initialize_resolver(self):
        """شروع کردن URL resolver"""
        self.url_resolver = URLResolver(timeout=10, max_redirects=5)
        await self.url_resolver.__aenter__()
    
    async def cleanup_resolver(self):
        """پاکسازی URL resolver"""
        if self.url_resolver:
            await self.url_resolver.__aexit__(None, None, None)
    
    async def resolve_links_with_http(self, links: List[str]) -> List[str]:
        """حل کردن لینک‌ها با استفاده از HTTP requests"""
        if not self.url_resolver:
            await self.initialize_resolver()
        
        resolved_links = []
        logger.info(f"🔍 Resolving {len(links)} links with HTTP requests...")
        
        # حل کردن همه لینک‌ها
        resolved_urls = await self.url_resolver.resolve_multiple_urls(links)
        
        for original_link, resolved_link in resolved_urls.items():
            if resolved_link and self.url_resolver.is_telegram_link(resolved_link):
                logger.info(f"✅ Resolved to Telegram: {original_link[:50]}... -> {resolved_link}")
                self.redirect_mapping[original_link] = resolved_link
                resolved_links.append(resolved_link)
            elif resolved_link:
                logger.warning(f"⚠️ Resolved but not Telegram: {original_link[:50]}... -> {resolved_link}")
                # اگر لینک حل شد ولی تلگرام نیست، آن را اضافه نمی‌کنیم
            else:
                logger.error(f"❌ Could not resolve: {original_link[:50]}...")
                # اگر نتوانستیم حل کنیم، لینک اصلی را نگه می‌داریم
                resolved_links.append(original_link)
        
        # نمایش آمار
        stats = self.url_resolver.get_redirect_stats()
        logger.info(f"📊 URL Resolution Stats:")
        logger.info(f"   • Total resolved: {stats['total_resolved']}")
        logger.info(f"   • Telegram redirects: {stats['telegram_redirects']}")
        logger.info(f"   • Non-Telegram redirects: {stats['non_telegram_redirects']}")
        logger.info(f"   • Failed redirects: {stats['failed_redirects']}")
        
        return resolved_links
    
    def extract_telegram_link_from_redirect(self, redirect_url: str) -> Optional[str]:
        """استخراج لینک تلگرام اصلی از لینک‌های ریدایرکت (legacy method)"""
        try:
            # Google Translate links
            if 'translate.google.com' in redirect_url:
                parsed = urlparse(redirect_url)
                params = parse_qs(parsed.query)
                
                if 'u' in params:
                    original_url = unquote(params['u'][0])
                    if 't.me' in original_url:
                        return original_url
            
            # سایر انواع ریدایرکت‌ها
            # می‌توانید اینجا انواع دیگر ریدایرکت را اضافه کنید
            
            return None
        except Exception as e:
            logger.error(f"Error extracting from redirect {redirect_url}: {e}")
            return None
    
    async def resolve_redirect_links(self, links: List[str]) -> List[str]:
        """حل کردن لینک‌های ریدایرکت و استخراج لینک‌های اصلی (updated method)"""
        # استفاده از روش جدید HTTP-based resolution
        return await self.resolve_links_with_http(links)
    
    def categorize_telegram_link(self, link: str) -> LinkInfo:
        """دسته‌بندی لینک‌های تلگرام"""
        link_info = LinkInfo(
            original_link=link,
            type="unknown",
            identifier="",
            is_invite_link=False,
            is_redirect=False
        )
        
        # بررسی ریدایرکت
        if link in self.redirect_mapping:
            link_info.is_redirect = True
            link_info.redirect_source = link
            link = self.redirect_mapping[link]  # استفاده از لینک اصلی
        
        if not 't.me' in link:
            link_info.type = "invalid"
            return link_info
        
        try:
            # پاکسازی لینک
            clean_link = link.split('?')[0]  # حذف query parameters
            
            if '/joinchat/' in clean_link:
                # لینک دعوت
                link_info.type = "invite_link"
                link_info.is_invite_link = True
                # استخراج invite hash
                hash_part = clean_link.split('/joinchat/')[-1]
                link_info.identifier = hash_part
                
            elif '/+' in clean_link:
                # فرمت جدید لینک دعوت
                link_info.type = "invite_link"
                link_info.is_invite_link = True
                hash_part = clean_link.split('/+')[-1]
                link_info.identifier = hash_part
                
            else:
                # لینک عمومی با username
                link_info.type = "public_link"
                # استخراج username
                username = clean_link.replace("https://t.me/", "").replace("@", "")
                if '/' in username:
                    username = username.split('/')[0]
                link_info.identifier = username
                
        except Exception as e:
            logger.error(f"Error categorizing link {link}: {e}")
            link_info.type = "invalid"
        
        return link_info
    
    def extract_links_from_text(self, text: str) -> List[str]:
        """استخراج لینک‌ها از متن"""
        if not text:
            return []
            
        # الگوهای مختلف لینک
        patterns = [
            r'https?://[^\s<>"\']+',
            r'www\.[^\s<>"\']+',
            r't\.me/[^\s<>"\']+',
            r'@[a-zA-Z0-9_]+',
        ]
        
        links = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            links.extend(matches)
        
        # پاکسازی لینک‌ها
        cleaned_links = []
        for link in links:
            # حذف کاراکترهای اضافی از انتها
            link = re.sub(r'[.,;:!?)\\]}]+$', '', link)
            if link:
                cleaned_links.append(link)
        
        return cleaned_links
