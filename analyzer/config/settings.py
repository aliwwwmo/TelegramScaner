import os
from typing import Optional
from dataclasses import dataclass

@dataclass
class TelegramConfig:
    """تنظیمات تلگرام"""
    api_id: int
    api_hash: str
    session_string: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> 'TelegramConfig':
        """بارگذاری تنظیمات از متغیرهای محیطی"""
        api_id = os.getenv('API_ID')
        api_hash = os.getenv('API_HASH')
        session_string = os.getenv('SESSION_STRING')
        
        if not api_id:
            raise ValueError("❌ API_ID not found in environment variables")
        if not api_hash:
            raise ValueError("❌ API_HASH not found in environment variables")
        
        try:
            api_id = int(api_id)
        except ValueError:
            raise ValueError("❌ API_ID must be a valid integer")
        
        # تمیز کردن session_string
        if session_string:
            session_string = session_string.strip()
            # حذف کاراکترهای اضافی اگر وجود دارد
            if len(session_string) > 0:
                print(f"✅ SESSION_STRING loaded (length: {len(session_string)})")
        
        return cls(
            api_id=api_id,
            api_hash=api_hash,
            session_string=session_string
        )

@dataclass
class AnalysisConfig:
    """تنظیمات تحلیل"""
    input_file: str = "links.txt"
    output_dir: str = "results"
    output_file: str = "my_chats.json"
    message_limit: int = 100
    messages_per_chat: int = 1000
    results_dir: str = "results"  # اضافه شد
    users_dir: str = "users"      # اضافه شد
    links_file: str = "links.txt" # اضافه شد
    
    @classmethod
    def from_env(cls) -> 'AnalysisConfig':
        """بارگذاری تنظیمات از متغیرهای محیطی"""
        return cls(
            input_file=os.getenv('LINKS_FILE', os.getenv('INPUT_FILE', 'links.txt')),
            output_dir=os.getenv('OUTPUT_DIR', os.getenv('RESULTS_DIR', 'results')),
            output_file=os.getenv('OUTPUT_FILE', 'my_chats.json'),
            message_limit=int(os.getenv('MESSAGE_LIMIT', '100')),
            messages_per_chat=int(os.getenv('MESSAGES_PER_CHAT', '1000')),
            results_dir=os.getenv('RESULTS_DIR', 'results'),
            users_dir=os.getenv('USERS_DIR', 'users'),
            links_file=os.getenv('LINKS_FILE', 'links.txt')
        )
