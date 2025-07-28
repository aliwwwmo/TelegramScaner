from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

class ChatType(Enum):
    """نوع چت"""
    CHANNEL = "channel"
    GROUP = "group"
    SUPERGROUP = "supergroup"
    PRIVATE = "private"

class ScanStatus(Enum):
    """وضعیت اسکن"""
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"

@dataclass
class LinkInfo:
    """اطلاعات لینک تلگرام"""
    original_link: str
    type: str = "unknown"
    identifier: str = ""
    is_invite_link: bool = False
    is_redirect: bool = False
    redirect_source: str = ""

@dataclass
class GroupInfo:
    """اطلاعات پایه گروه/کانال برای ذخیره در MongoDB"""
    chat_id: int
    username: Optional[str] = None
    link: Optional[str] = None
    chat_type: ChatType = ChatType.GROUP
    is_public: bool = True
    last_scan_time: Optional[datetime] = None
    last_message_id: Optional[int] = None
    start_message_id: Optional[int] = None  # ID پیامی که اسکن شروع می‌شود
    last_scan_status: ScanStatus = ScanStatus.FAILED
    scan_count: int = 0
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """تبدیل به دیکشنری برای ذخیره در MongoDB"""
        data = asdict(self)
        data['chat_type'] = self.chat_type.value
        data['last_scan_status'] = self.last_scan_status.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GroupInfo':
        """ایجاد از دیکشنری MongoDB"""
        # تبدیل enum strings به enum objects
        if 'chat_type' in data and isinstance(data['chat_type'], str):
            data['chat_type'] = ChatType(data['chat_type'])
        if 'last_scan_status' in data and isinstance(data['last_scan_status'], str):
            data['last_scan_status'] = ScanStatus(data['last_scan_status'])
        
        # تبدیل datetime strings به datetime objects
        for field in ['last_scan_time', 'created_at', 'updated_at']:
            if field in data and isinstance(data[field], str):
                try:
                    data[field] = datetime.fromisoformat(data[field].replace('Z', '+00:00'))
                except:
                    data[field] = None
        
        return cls(**data)
    
    def update_scan_info(self, message_id: Optional[int] = None, 
                        start_message_id: Optional[int] = None,
                        status: ScanStatus = ScanStatus.SUCCESS):
        """به‌روزرسانی اطلاعات اسکن"""
        self.last_scan_time = datetime.utcnow()
        self.last_scan_status = status
        self.scan_count += 1
        self.updated_at = datetime.utcnow()
        
        if message_id is not None:
            self.last_message_id = message_id
        
        if start_message_id is not None:
            self.start_message_id = start_message_id
