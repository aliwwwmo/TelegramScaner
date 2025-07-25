import asyncio
import json
import os
import re
from datetime import datetime
from typing import List, Dict, Set, Optional
from urllib.parse import urlparse

from pyrogram import Client
from pyrogram.types import Chat, Message, User
from pyrogram.errors import (
    ChannelPrivate, ChatAdminRequired, FloodWait, 
    UsernameNotOccupied, PeerIdInvalid
)
from pymongo import MongoClient
from bson import ObjectId
import logging
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی
load_dotenv()
# تنظیم لاگ
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TelegramAnalyzer:
    def __init__(self, api_id: int, api_hash: str):
        self.api_id = api_id
        self.api_hash = api_hash
        self.app = Client("telegram_analyzer", api_id=api_id, api_hash=api_hash)
        
 # ایجاد فولدرها
        os.makedirs("results", exist_ok=True)
        os.makedirs("users", exist_ok=True)
        
        # مجموعه‌های نگهداری داده
        self.processed_users: Dict[int, Dict] = {}
        self.extracted_links: Set[str] = set()

    def extract_links_from_text(self, text: str) -> List[str]:
        """استخراج لینک‌ها از متن"""
        if not text:
            return []
            
        # الگوهای مختلف لینک
        patterns = [
            r'https?://[^\s]+',
            r'www\.[^\s]+',
            r't\.me/[^\s]+',
            r'@\w+',
        ]
        
        links = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            links.extend(matches)
        
        return links