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
        
