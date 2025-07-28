import asyncio
from typing import Dict, Optional

from pyrogram import Client
from pyrogram.errors import (
    ChannelPrivate, ChatAdminRequired, FloodWait, 
    UsernameNotOccupied, PeerIdInvalid, InviteHashExpired,
    InviteHashInvalid, UserAlreadyParticipant
)
from pyrogram import raw

from models.data_models import LinkInfo
from utils.logger import logger

class ChatAnalyzer:
    """کلاس تحلیل چت‌ها"""
    
    def __init__(self, client: Client):
        self.client = client
    
    async def analyze_invite_link_advanced(self, invite_hash: str, original_link: str) -> Dict:
        """تحلیل پیشرفته لینک‌های دعوت با استفاده از raw API"""
        result = {
            'link': original_link,
            'type': "invite_link",
            'status': "unknown",
            'invite_hash': invite_hash,
            'chat_id': None,
            'title': '',
            'username': '',
            'members_count': 0,
            'can_join': False,
            'is_public': False,
            'is_channel': False,
            'is_group': False,
            'error': None
        }
        
        try:
            # استفاده از raw API برای چک کردن invite link
            r = await self.client.invoke(
                raw.functions.messages.CheckChatInvite(
                    hash=invite_hash
                )
            )
            
            if isinstance(r, raw.types.ChatInviteAlready):
                # اگر قبلاً عضو شده‌اید یا چت public است
                chat = r.chat
                result['chat_id'] = getattr(chat, 'id', None)
                result['title'] = getattr(chat, 'title', '')
                result['username'] = getattr(chat, 'username', '')
                result['members_count'] = getattr(chat, 'participants_count', 0)
                result['status'] = "accessible"
                result['can_join'] = True
                result['is_public'] = True
                
                # تشخیص نوع چت
                if isinstance(chat, raw.types.Channel):
                    if getattr(chat, 'broadcast', False):
                        result['type'] = "channel_invite"
                        result['is_channel'] = True
                    else:
                        result['type'] = "group_invite" 
                        result['is_group'] = True
                elif isinstance(chat, raw.types.Chat):
                    result['type'] = "group_invite"
                    result['is_group'] = True
                
                # برای چت‌های public، سعی کنیم chat_id را منفی کنیم
                if result['chat_id'] and isinstance(chat, raw.types.Channel):
                    result['chat_id'] = int(f"-100{chat.id}")
                elif result['chat_id'] and isinstance(chat, raw.types.Chat):
                    result['chat_id'] = -chat.id
                    
            elif isinstance(r, raw.types.ChatInvite):
                # چت private است اما اطلاعات محدودی در دسترس است
                result['title'] = getattr(r, 'title', '')
                result['members_count'] = getattr(r, 'participants_count', 0)
                result['status'] = "private"
                result['can_join'] = True
                result['is_public'] = False
                
                # تشخیص نوع
                if getattr(r, 'channel', False):
                    if getattr(r, 'broadcast', False):
                        result['type'] = "channel_invite"
                        result['is_channel'] = True
                    else:
                        result['type'] = "group_invite"
                        result['is_group'] = True
                else:
                    result['type'] = "group_invite"
                    result['is_group'] = True
                    
            else:
                result['error'] = f"Unexpected response type: {type(r)}"
                result['status'] = "error"
                
        except InviteHashExpired:
            result['error'] = "Invite link has expired"
            result['status'] = "expired"
        except InviteHashInvalid:
            result['error'] = "Invalid invite link"
            result['status'] = "invalid"
        except Exception as e:
            result['error'] = str(e)
            result['status'] = "error"
            logger.error(f"Error analyzing invite link {original_link}: {e}")
        
        return result
    
    async def analyze_public_link(self, username: str, original_link: str) -> Dict:
        """تحلیل لینک‌های عمومی"""
        result = {
            'link': original_link,
            'type': "public_link",
            'status': "unknown",
            'username': username,
            'chat_id': None,
            'title': '',
            'members_count': 0,
            'can_join': True,
            'is_public': True,
            'is_channel': False,
            'is_group': False,
            'error': None
        }
        
        try:
            # تلاش برای دریافت اطلاعات چت
            chat = await self.client.get_chat(username)
            
            result['chat_id'] = chat.id
            result['title'] = getattr(chat, 'title', '')
            result['username'] = getattr(chat, 'username', username)
            result['members_count'] = getattr(chat, 'members_count', 0)
            result['status'] = "accessible"
            
            # تشخیص نوع چت
            if hasattr(chat, 'type'):
                if str(chat.type) == 'ChatType.CHANNEL':
                    result['type'] = "channel"
                    result['is_channel'] = True
                elif str(chat.type) == 'ChatType.SUPERGROUP':
                    result['type'] = "supergroup"
                    result['is_group'] = True
                elif str(chat.type) == 'ChatType.GROUP':
                    result['type'] = "group"
                    result['is_group'] = True
                    
        except UsernameNotOccupied:
            result['error'] = "Username not occupied"
            result['status'] = "not_found"
        except ChannelPrivate:
            result['error'] = "Channel is private"
            result['status'] = "private"
        except Exception as e:
            result['error'] = str(e)
            result['status'] = "error"
            logger.error(f"Error analyzing public link {original_link}: {e}")
        
        return result
    
    async def analyze_chat_type(self, link_info: LinkInfo) -> Dict:
        """تحلیل نوع چت بر اساس لینک"""
        # این متد ساده شده و فقط اطلاعات پایه را برمی‌گرداند
        return {
            'link': link_info.original_link,
            'type': link_info.type,
            'status': "analyzed",
            'is_redirect': link_info.is_redirect,
            'redirect_source': link_info.redirect_source
        }
