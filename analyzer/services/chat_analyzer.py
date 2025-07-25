import asyncio
from typing import Dict

from pyrogram import Client
from pyrogram.errors import (
    ChannelPrivate, ChatAdminRequired, FloodWait, 
    UsernameNotOccupied, PeerIdInvalid, InviteHashExpired,
    InviteHashInvalid, UserAlreadyParticipant
)
from pyrogram import raw

from models.data_models import ChatAnalysisResult, LinkInfo
from utils.logger import logger

class ChatAnalyzer:
    """کلاس تحلیل چت‌ها"""
    
    def __init__(self, client: Client):
        self.client = client
    
    async def analyze_invite_link_advanced(self, invite_hash: str, original_link: str) -> ChatAnalysisResult:
        """تحلیل پیشرفته لینک‌های دعوت با استفاده از raw API"""
        result = ChatAnalysisResult(
            link=original_link,
            type="invite_link",
            status="unknown",
            invite_hash=invite_hash
        )
        
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
                result.chat_id = getattr(chat, 'id', None)
                result.title = getattr(chat, 'title', '')
                result.username = getattr(chat, 'username', '')
                result.members_count = getattr(chat, 'participants_count', 0)
                result.status = "accessible"
                result.can_join = True
                result.is_public = True
                
                # تشخیص نوع چت
                if isinstance(chat, raw.types.Channel):
                    if getattr(chat, 'broadcast', False):
                        result.type = "channel_invite"
                        result.is_channel = True
                    else:
                        result.type = "group_invite" 
                        result.is_group = True
                elif isinstance(chat, raw.types.Chat):
                    result.type = "group_invite"
                    result.is_group = True
                
                # برای چت‌های public، سعی کنیم chat_id را منفی کنیم
                if result.chat_id and isinstance(chat, raw.types.Channel):
                    result.chat_id = int(f"-100{chat.id}")
                elif result.chat_id and isinstance(chat, raw.types.Chat):
                    result.chat_id = -chat.id
                    
            elif isinstance(r, raw.types.ChatInvite):
                # چت private است اما اطلاعات محدودی در دسترس است
                result.title = getattr(r, 'title', '')
                result.members_count = getattr(r, 'participants_count', 0)
                result.status = "private"
                result.can_join = True
                result.is_public = False
                
                # تشخیص نوع
                if getattr(r, 'channel', False):
                    if getattr(r, 'broadcast', False):
                        result.type = "channel_invite"
                        result.is_channel = True
                    else:
                        result.type = "group_invite"
                        result.is_group = True
                else:
                    result.type = "group_invite"
                    result.is_group = True
                    
            else:
                result.error = f"Unexpected response type: {type(r)}"
                result.status = "error"
                
        except InviteHashExpired:
            result.error = "Invite link has expired"
            result.status = "expired"
        except InviteHashInvalid:
            result.error = "Invalid invite link"
            result.status = "invalid"
        except Exception as e:
            result.error = str(e)
            result.status = "error"
            logger.error(f"Error analyzing invite link {original_link}: {e}")
            
        return result
    
    async def analyze_public_link(self, username: str, original_link: str) -> ChatAnalysisResult:
        """تحلیل لینک‌های عمومی"""
        result = ChatAnalysisResult(
            link=original_link,
            username=username,
            is_public=True
        )
        
        try:
            chat = await self.client.get_chat(username)
            
            result.title = chat.title or ""
            result.username = chat.username or ""
            result.members_count = getattr(chat, 'members_count', 0)
            result.chat_id = chat.id
            
            if chat.type.name == "CHANNEL":
                result.type = "channel"
                result.is_channel = True
            elif chat.type.name in ["GROUP", "SUPERGROUP"]:
                result.type = "group"
                result.is_group = True
            elif chat.type.name == "PRIVATE":
                result.type = "private"
            
            result.status = "public"
            
        except ChannelPrivate:
            result.status = "private"
            result.error = "Channel/Group is private"
            result.is_public = False
        except (UsernameNotOccupied, PeerIdInvalid):
            result.error = "Invalid username or link"
            result.status = "invalid"
        except Exception as e:
            result.error = str(e)
            result.status = "error"
            logger.error(f"Error analyzing public link {original_link}: {e}")
            
        return result
    
    async def analyze_chat_type(self, link_info: LinkInfo) -> ChatAnalysisResult:
        """تحلیل نوع چت با پشتیبانی از انواع مختلف لینک"""
        
        if link_info.type == "invalid":
            return ChatAnalysisResult(
                link=link_info.original_link,
                type="invalid",
                status="invalid",
                error="Invalid or non-Telegram link",
                link_category="invalid"
            )
        
        # تحلیل بر اساس نوع لینک
        if link_info.is_invite_link:
            result = await self.analyze_invite_link_advanced(link_info.identifier, link_info.original_link)
        else:
            result = await self.analyze_public_link(link_info.identifier, link_info.original_link)
        
        # اضافه کردن اطلاعات دسته‌بندی
        result.link_category = link_info.type
        result.is_redirect = link_info.is_redirect
        
        if link_info.is_redirect:
            result.redirect_source = link_info.redirect_source
        
        return result
