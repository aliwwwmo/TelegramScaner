import aiohttp
import asyncio
from typing import Optional, Dict, List
from urllib.parse import urlparse, urljoin
import re
from utils.logger import logger

class URLResolver:
    """کلاس حل کردن URL ها و بررسی ریدایرکت‌ها"""
    
    def __init__(self, timeout: int = 10, max_redirects: int = 5):
        self.timeout = timeout
        self.max_redirects = max_redirects
        self.session: Optional[aiohttp.ClientSession] = None
        self.redirect_cache: Dict[str, str] = {}
        
    async def __aenter__(self):
        """شروع session"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout),
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """بستن session"""
        if self.session:
            await self.session.close()
    
    def is_telegram_link(self, url: str) -> bool:
        """بررسی اینکه آیا URL یک لینک تلگرام است"""
        # بررسی اینکه آیا URL مستقیماً لینک تلگرام است (نه شامل آن)
        telegram_direct_patterns = [
            r'^https?://t\.me/[a-zA-Z0-9_/]+$',
            r'^https?://telegram\.me/[a-zA-Z0-9_/]+$',
            r'^https?://web\.telegram\.org/[a-zA-Z0-9_/]+$',
            r'^@[a-zA-Z0-9_]{5,}$',  # username format
            r'^\+[0-9]{10,}$',  # phone number format
        ]
        
        for pattern in telegram_direct_patterns:
            if re.match(pattern, url, re.IGNORECASE):
                return True
        return False
    
    def extract_telegram_link(self, url: str) -> Optional[str]:
        """استخراج لینک تلگرام از URL"""
        telegram_patterns = [
            r'(https?://t\.me/[a-zA-Z0-9_/]+)',
            r'(https?://telegram\.me/[a-zA-Z0-9_/]+)',
            r'(https?://web\.telegram\.org/[a-zA-Z0-9_/]+)',
            r'(@[a-zA-Z0-9_]{5,})',  # username format
            r'(\+[0-9]{10,})',  # phone number format
        ]
        
        for pattern in telegram_patterns:
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    async def resolve_url(self, url: str) -> Optional[str]:
        """حل کردن URL و بررسی ریدایرکت‌ها"""
        if not self.session:
            logger.error("❌ Session not initialized. Use async context manager.")
            return None
        
        # اگر قبلاً حل شده، از cache استفاده کن
        if url in self.redirect_cache:
            return self.redirect_cache[url]
        
        try:
            logger.info(f"🔍 Resolving URL: {url}")
            
            # ابتدا بررسی کنیم که آیا URL شامل لینک تلگرام است
            extracted_telegram = self.extract_telegram_link(url)
            if extracted_telegram:
                logger.info(f"✅ Found Telegram link in URL: {url} -> {extracted_telegram}")
                self.redirect_cache[url] = extracted_telegram
                return extracted_telegram
            
            # اگر URL از قبل لینک تلگرام است، نیازی به حل کردن نیست
            if self.is_telegram_link(url):
                logger.info(f"✅ Already a Telegram link: {url}")
                self.redirect_cache[url] = url
                return url
            
            # حل کردن URL
            final_url = await self._follow_redirects(url)
            
            if final_url and self.is_telegram_link(final_url):
                logger.info(f"✅ Redirect resolved to Telegram: {url} -> {final_url}")
                self.redirect_cache[url] = final_url
                return final_url
            elif final_url:
                logger.warning(f"⚠️ Redirect not to Telegram: {url} -> {final_url}")
                self.redirect_cache[url] = final_url
                return None
            else:
                logger.error(f"❌ Could not resolve URL: {url}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error resolving URL {url}: {e}")
            return None
    
    async def _follow_redirects(self, url: str) -> Optional[str]:
        """دنبال کردن ریدایرکت‌ها"""
        if not self.session:
            return None
        
        try:
            redirect_count = 0
            current_url = url
            
            while redirect_count < self.max_redirects:
                logger.debug(f"🔗 Following redirect {redirect_count + 1}: {current_url}")
                
                async with self.session.get(current_url, allow_redirects=False) as response:
                    if response.status in [301, 302, 303, 307, 308]:
                        # ریدایرکت
                        redirect_url = response.headers.get('Location')
                        if redirect_url:
                            # تبدیل به absolute URL اگر relative باشد
                            if not redirect_url.startswith(('http://', 'https://')):
                                redirect_url = urljoin(current_url, redirect_url)
                            
                            current_url = redirect_url
                            redirect_count += 1
                            continue
                        else:
                            logger.warning(f"⚠️ Redirect status but no Location header: {current_url}")
                            break
                    else:
                        # ریدایرکت تمام شد
                        return str(response.url)
            
            logger.warning(f"⚠️ Max redirects reached for: {url}")
            return current_url
            
        except asyncio.TimeoutError:
            logger.error(f"❌ Timeout resolving URL: {url}")
            return None
        except Exception as e:
            logger.error(f"❌ Error following redirects for {url}: {e}")
            return None
    
    async def resolve_multiple_urls(self, urls: List[str]) -> Dict[str, Optional[str]]:
        """حل کردن چندین URL همزمان"""
        if not self.session:
            logger.error("❌ Session not initialized. Use async context manager.")
            return {}
        
        tasks = []
        for url in urls:
            task = self.resolve_url(url)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        resolved_urls = {}
        for url, result in zip(urls, results):
            if isinstance(result, Exception):
                logger.error(f"❌ Error resolving {url}: {result}")
                resolved_urls[url] = None
            else:
                resolved_urls[url] = result
        
        return resolved_urls
    
    def get_redirect_stats(self) -> Dict[str, int]:
        """آمار ریدایرکت‌ها"""
        telegram_redirects = sum(1 for url in self.redirect_cache.values() if url and self.is_telegram_link(url))
        non_telegram_redirects = sum(1 for url in self.redirect_cache.values() if url and not self.is_telegram_link(url))
        failed_redirects = sum(1 for url in self.redirect_cache.values() if not url)
        
        return {
            'total_resolved': len(self.redirect_cache),
            'telegram_redirects': telegram_redirects,
            'non_telegram_redirects': non_telegram_redirects,
            'failed_redirects': failed_redirects
        } 