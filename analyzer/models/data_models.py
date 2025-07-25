from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from datetime import datetime

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
class ChatAnalysisResult:
    """نتیجه تحلیل چت"""
    link: str
    type: str = "unknown"
    status: str = "unknown"
    title: str = ""
    username: str = ""
    members_count: int = 0
    chat_id: Optional[int] = None
    error: Optional[str] = None
    link_category: str = ""
    is_channel: bool = False
    is_group: bool = False
    is_public: bool = False
    is_redirect: bool = False
    redirect_source: str = ""
    invite_hash: str = ""
    can_join: bool = False

@dataclass
class MessageData:
    """داده‌های پیام"""
    group_id: str
    message_id: int
    text: str
    timestamp: str
    reactions: List[str] = field(default_factory=list)
    reply_to: Optional[int] = None
    edited: bool = False
    is_forwarded: bool = False

@dataclass
class GroupInfo:
    """اطلاعات گروه"""
    group_id: str
    group_title: str
    joined_at: str
    role: str = "member"
    is_admin: bool = False

@dataclass
class UserData:
    """داده‌های کاربر"""
    user_id: int
    current_username: Optional[str] = None
    current_name: str = ""
    username_history: List[Dict] = field(default_factory=list)
    name_history: List[Dict] = field(default_factory=list)
    is_bot: bool = False
    is_deleted: bool = False
    joined_groups: List[GroupInfo] = field(default_factory=list)
    messages: List[MessageData] = field(default_factory=list)

@dataclass
class AnalysisResults:
    """نتایج کلی تحلیل"""
    chat_analysis_results: List[ChatAnalysisResult] = field(default_factory=list)
    extracted_links: Set[str] = field(default_factory=set)
    processed_users: Dict[int, UserData] = field(default_factory=dict)
    redirect_mapping: Dict[str, str] = field(default_factory=dict)
    analysis_date: str = field(default_factory=lambda: datetime.utcnow().isoformat())
