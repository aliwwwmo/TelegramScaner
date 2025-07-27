import os
from typing import Optional

class TelegramStorageConfig:
    """تنظیمات ذخیره‌سازی تلگرام"""
    
    @staticmethod
    def get_target_chat_id() -> Optional[int]:
        """دریافت ID چت مقصد از متغیرهای محیطی"""
        chat_id = os.getenv('TELEGRAM_STORAGE_CHAT_ID')
        if chat_id:
            try:
                return int(chat_id)
            except ValueError:
                print(f"⚠️ Invalid TELEGRAM_STORAGE_CHAT_ID: {chat_id}")
                return None
        return None
    
    @staticmethod
    def get_storage_mode() -> str:
        """دریافت حالت ذخیره‌سازی"""
        return os.getenv('TELEGRAM_STORAGE_MODE', 'saved_messages')
    
    @staticmethod
    def should_use_saved_messages() -> bool:
        """آیا باید از Saved Messages استفاده کند؟"""
        mode = TelegramStorageConfig.get_storage_mode()
        return mode == 'saved_messages' or TelegramStorageConfig.get_target_chat_id() is None 