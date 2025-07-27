import asyncio
import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from pyrogram.types import Message, User, ChatMember
from config.settings import ANALYSIS_SETTINGS
from utils.logger import logger

class ComprehensiveAnalyzer:
    """تحلیلگر جامع برای استخراج تمام اطلاعات گروه‌ها"""
    
    def __init__(self):
        self.extracted_data = {
            'chat_info': {},
            'messages': [],
            'members': [],
            'media_files': [],
            'reactions': [],
            'forwards': [],
            'links': [],
            'statistics': {}
        }
        self.all_links = set()  # برای ذخیره تمام لینک‌های یافت شده
    
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
            r'telegram\.me/[^\s<>"\']+',
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
    
    def categorize_link(self, link: str) -> Dict[str, Any]:
        """دسته‌بندی لینک"""
        link_info = {
            'original_link': link,
            'type': 'unknown',
            'identifier': '',
            'is_telegram': False,
            'is_invite_link': False
        }
        
        if not link:
            return link_info
        
        # بررسی لینک‌های تلگرام
        if 't.me' in link or 'telegram.me' in link:
            link_info['is_telegram'] = True
            
            if '/joinchat/' in link:
                link_info['type'] = 'invite_link'
                link_info['is_invite_link'] = True
                hash_part = link.split('/joinchat/')[-1].split('?')[0]
                link_info['identifier'] = hash_part
                
            elif '/+' in link:
                link_info['type'] = 'invite_link'
                link_info['is_invite_link'] = True
                hash_part = link.split('/+')[-1].split('?')[0]
                link_info['identifier'] = hash_part
                
            else:
                link_info['type'] = 'public_link'
                username = link.replace("https://t.me/", "").replace("https://telegram.me/", "").replace("@", "")
                if '/' in username:
                    username = username.split('/')[0]
                link_info['identifier'] = username
        
        # بررسی سایر انواع لینک‌ها
        elif 'youtube.com' in link or 'youtu.be' in link:
            link_info['type'] = 'youtube'
        elif 'instagram.com' in link:
            link_info['type'] = 'instagram'
        elif 'twitter.com' in link or 'x.com' in link:
            link_info['type'] = 'twitter'
        elif 'facebook.com' in link:
            link_info['type'] = 'facebook'
        elif 'linkedin.com' in link:
            link_info['type'] = 'linkedin'
        elif 'github.com' in link:
            link_info['type'] = 'github'
        elif 'reddit.com' in link:
            link_info['type'] = 'reddit'
        elif 'discord.gg' in link:
            link_info['type'] = 'discord'
        elif 'whatsapp.com' in link:
            link_info['type'] = 'whatsapp'
        else:
            link_info['type'] = 'other'
        
        return link_info
    
    async def analyze_chat_comprehensive(self, chat, messages: List[Message], members: List[ChatMember]):
        """تحلیل جامع چت با استخراج تمام اطلاعات"""
        logger.info("🔍 Starting comprehensive analysis...")
        
        try:
            # اطلاعات چت
            self.extracted_data['chat_info'] = self._extract_chat_info(chat)
            
            # تحلیل پیام‌ها
            if ANALYSIS_SETTINGS.extract_all_messages and messages:
                await self._analyze_messages_comprehensive(messages)
            else:
                logger.info("📝 Message extraction is disabled or no messages available")
            
            # تحلیل اعضا
            if ANALYSIS_SETTINGS.extract_all_members and members:
                self._analyze_members_comprehensive(members)
            else:
                logger.info("👥 Member extraction is disabled or no members available")
            
            # محاسبه آمار
            self._calculate_statistics()
            
            return self.extracted_data
            
        except Exception as e:
            logger.error(f"❌ Error in comprehensive analysis: {e}")
            # Return partial data if available
            return self.extracted_data
    
    def _extract_chat_info(self, chat) -> Dict[str, Any]:
        """استخراج اطلاعات کامل چت"""
        chat_info = {
            'id': chat.id,
            'title': chat.title,
            'username': getattr(chat, 'username', None),
            'type': str(chat.type),
            'members_count': getattr(chat, 'members_count', 0),
            'description': getattr(chat, 'description', ''),
            'linked_chat': getattr(chat, 'linked_chat', None),
            'slow_mode_delay': getattr(chat, 'slow_mode_delay', None),
            'is_forum': getattr(chat, 'is_forum', False),
            'is_verified': getattr(chat, 'is_verified', False),
            'is_restricted': getattr(chat, 'is_restricted', False),
            'is_scam': getattr(chat, 'is_scam', False),
            'is_fake': getattr(chat, 'is_fake', False),
            'created_at': getattr(chat, 'date', None),
            'last_activity': None
        }
        
        logger.info(f"📊 Chat Info: {chat_info['title']} ({chat_info['members_count']} members)")
        return chat_info
    
    async def _analyze_messages_comprehensive(self, messages: List[Message]):
        """تحلیل جامع پیام‌ها"""
        logger.info(f"📝 Analyzing {len(messages)} messages comprehensively...")
        
        for i, message in enumerate(messages):
            try:
                message_data = self._extract_message_data(message)
                
                # استخراج لینک‌ها از متن پیام
                message_text = message_data.get('text', '') or message_data.get('caption', '')
                if message_text:
                    links = self.extract_links_from_text(message_text)
                    if links:
                        message_data['links'] = []
                        for link in links:
                            link_info = self.categorize_link(link)
                            message_data['links'].append(link_info)
                            self.all_links.add(link)  # اضافه کردن به مجموعه کلی
                
                self.extracted_data['messages'].append(message_data)
                
                # استخراج اطلاعات اضافی
                if ANALYSIS_SETTINGS.extract_media_info:
                    try:
                        await self._extract_media_info(message, message_data)
                    except Exception as e:
                        logger.warning(f"⚠️ Error extracting media info for message {message.id}: {e}")
                
                if ANALYSIS_SETTINGS.track_reactions:
                    try:
                        await self._extract_reactions(message, message_data)
                    except Exception as e:
                        logger.warning(f"⚠️ Error extracting reactions for message {message.id}: {e}")
                
                if ANALYSIS_SETTINGS.track_forwards:
                    try:
                        await self._extract_forward_info(message, message_data)
                    except Exception as e:
                        logger.warning(f"⚠️ Error extracting forward info for message {message.id}: {e}")
                
                # نمایش پیشرفت
                if (i + 1) % 100 == 0:
                    logger.info(f"📝 Processed {i + 1}/{len(messages)} messages...")
                    
            except Exception as e:
                logger.error(f"❌ Error processing message {getattr(message, 'id', 'unknown')}: {e}")
                continue
        
        logger.info(f"✅ Message analysis completed: {len(self.extracted_data['messages'])} messages processed")
        logger.info(f"🔗 Total unique links found: {len(self.all_links)}")
    
    def _extract_message_data(self, message: Message) -> Dict[str, Any]:
        """استخراج اطلاعات کامل پیام"""
        
        # تولید لینک پیام
        message_link = ""
        if hasattr(message, 'chat') and message.chat:
            chat_username = getattr(message.chat, 'username', '')
            if chat_username:
                # حذف @ از ابتدای username اگر وجود داشته باشد
                username = chat_username.lstrip('@')
                message_link = f"https://t.me/{username}/{message.id}"
        
        message_data = {
            'id': message.id,
            'date': message.date.isoformat() if message.date else None,
            'text': message.text if message.text else None,
            'caption': message.caption if message.caption else None,
            'media_type': str(message.media) if message.media else None,
            'has_media': message.media is not None,
            'is_forwarded': message.forward_from is not None,
            'has_reply': message.reply_to_message is not None,
            'reply_to_message_id': message.reply_to_message.id if message.reply_to_message else None,
            'views': getattr(message, 'views', None),
            'forwards': getattr(message, 'forwards', None),
            'edit_date': message.edit_date.isoformat() if message.edit_date else None,
            'author': self._extract_user_data(message.from_user) if message.from_user else None,
            'chat_id': message.chat.id,
            'chat_title': message.chat.title,
            'entities': self._extract_entities(message.entities) if message.entities else None,
            'media_info': {},
            'reactions': [],
            'forward_info': {},
            'message_link': message_link  # اضافه کردن لینک پیام
        }
        
        return message_data
    
    def _extract_user_data(self, user: User) -> Dict[str, Any]:
        """استخراج اطلاعات کاربر"""
        if not user:
            return None
        
        return {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_bot': user.is_bot,
            'is_verified': user.is_verified,
            'is_restricted': user.is_restricted,
            'is_scam': user.is_scam,
            'is_fake': user.is_fake,
            'language_code': user.language_code,
            'status': str(user.status) if hasattr(user, 'status') else None
        }
    
    def _extract_entities(self, entities) -> List[Dict[str, Any]]:
        """استخراج entities پیام"""
        if not entities:
            return []
        
        extracted_entities = []
        for entity in entities:
            entity_data = {
                'type': str(entity.type),
                'offset': entity.offset,
                'length': entity.length,
                'url': getattr(entity, 'url', None),
                'user': self._extract_user_data(getattr(entity, 'user', None))
            }
            extracted_entities.append(entity_data)
        
        return extracted_entities
    
    async def _extract_media_info(self, message: Message, message_data: Dict[str, Any]):
        """استخراج اطلاعات مدیا"""
        if not message.media:
            return
        
        media_info = {
            'type': str(message.media),
            'file_id': None,
            'file_unique_id': None,
            'file_size': None,
            'duration': None,
            'width': None,
            'height': None,
            'mime_type': None,
            'file_name': None
        }
        
        # استخراج اطلاعات بر اساس نوع مدیا
        if hasattr(message, 'photo') and message.photo is not None:
            media_info.update({
                'file_id': message.photo.file_id,
                'file_unique_id': message.photo.file_unique_id,
                'file_size': message.photo.file_size,
                'width': message.photo.width,
                'height': message.photo.height
            })
        elif hasattr(message, 'video') and message.video is not None:
            media_info.update({
                'file_id': message.video.file_id,
                'file_unique_id': message.video.file_unique_id,
                'file_size': message.video.file_size,
                'duration': message.video.duration,
                'width': message.video.width,
                'height': message.video.height,
                'mime_type': message.video.mime_type
            })
        elif hasattr(message, 'document') and message.document is not None:
            media_info.update({
                'file_id': message.document.file_id,
                'file_unique_id': message.document.file_unique_id,
                'file_size': message.document.file_size,
                'mime_type': message.document.mime_type,
                'file_name': message.document.file_name
            })
        elif hasattr(message, 'audio') and message.audio is not None:
            media_info.update({
                'file_id': message.audio.file_id,
                'file_unique_id': message.audio.file_unique_id,
                'file_size': message.audio.file_size,
                'duration': message.audio.duration,
                'mime_type': message.audio.mime_type,
                'title': getattr(message.audio, 'title', None),
                'performer': getattr(message.audio, 'performer', None)
            })
        elif hasattr(message, 'voice') and message.voice is not None:
            media_info.update({
                'file_id': message.voice.file_id,
                'file_unique_id': message.voice.file_unique_id,
                'file_size': message.voice.file_size,
                'duration': message.voice.duration,
                'mime_type': message.voice.mime_type
            })
        elif hasattr(message, 'sticker') and message.sticker is not None:
            media_info.update({
                'file_id': message.sticker.file_id,
                'file_unique_id': message.sticker.file_unique_id,
                'file_size': message.sticker.file_size,
                'width': message.sticker.width,
                'height': message.sticker.height,
                'emoji': getattr(message.sticker, 'emoji', None),
                'set_name': getattr(message.sticker, 'set_name', None)
            })
        elif hasattr(message, 'animation') and message.animation is not None:
            media_info.update({
                'file_id': message.animation.file_id,
                'file_unique_id': message.animation.file_unique_id,
                'file_size': message.animation.file_size,
                'duration': message.animation.duration,
                'width': message.animation.width,
                'height': message.animation.height,
                'mime_type': message.animation.mime_type
            })
        elif hasattr(message, 'video_note') and message.video_note is not None:
            media_info.update({
                'file_id': message.video_note.file_id,
                'file_unique_id': message.video_note.file_unique_id,
                'file_size': message.video_note.file_size,
                'duration': message.video_note.duration,
                'length': message.video_note.length
            })
        elif hasattr(message, 'contact') and message.contact is not None:
            media_info.update({
                'phone_number': message.contact.phone_number,
                'first_name': message.contact.first_name,
                'last_name': getattr(message.contact, 'last_name', None),
                'user_id': getattr(message.contact, 'user_id', None)
            })
        elif hasattr(message, 'location') and message.location is not None:
            media_info.update({
                'latitude': message.location.latitude,
                'longitude': message.location.longitude,
                'live_period': getattr(message.location, 'live_period', None)
            })
        elif hasattr(message, 'venue') and message.venue is not None:
            media_info.update({
                'title': message.venue.title,
                'address': message.venue.address,
                'foursquare_id': getattr(message.venue, 'foursquare_id', None),
                'foursquare_type': getattr(message.venue, 'foursquare_type', None)
            })
        elif hasattr(message, 'poll') and message.poll is not None:
            media_info.update({
                'question': message.poll.question,
                'options': [option.text for option in message.poll.options],
                'total_voter_count': message.poll.total_voter_count,
                'is_closed': message.poll.is_closed,
                'is_anonymous': message.poll.is_anonymous,
                'type': str(message.poll.type)
            })
        
        message_data['media_info'] = media_info
        self.extracted_data['media_files'].append({
            'message_id': message.id,
            'chat_id': message.chat.id,
            'media_info': media_info
        })
    
    async def _extract_reactions(self, message: Message, message_data: Dict[str, Any]):
        """استخراج اطلاعات reactions"""
        if not hasattr(message, 'reactions') or not message.reactions:
            return
        
        reactions = []
        for reaction in message.reactions.reactions:
            reaction_data = {
                'emoji': reaction.emoji,
                'count': reaction.count,
                'recent_reactions': []
            }
            
            # استخراج اطلاعات کاربران اخیر
            if hasattr(reaction, 'recent_reactions'):
                for recent in reaction.recent_reactions:
                    reaction_data['recent_reactions'].append({
                        'user': self._extract_user_data(recent.peer_id),
                        'date': recent.date.isoformat() if recent.date else None
                    })
            
            reactions.append(reaction_data)
        
        message_data['reactions'] = reactions
        self.extracted_data['reactions'].append({
            'message_id': message.id,
            'chat_id': message.chat.id,
            'reactions': reactions
        })
    
    async def _extract_forward_info(self, message: Message, message_data: Dict[str, Any]):
        """استخراج اطلاعات forward"""
        if not message.forward_from and not message.forward_from_chat:
            return
        
        forward_info = {
            'is_forwarded': True,
            'forward_from_user': self._extract_user_data(message.forward_from) if message.forward_from else None,
            'forward_from_chat': None,
            'forward_date': message.forward_date.isoformat() if message.forward_date else None
        }
        
        if message.forward_from_chat:
            forward_info['forward_from_chat'] = {
                'id': message.forward_from_chat.id,
                'title': message.forward_from_chat.title,
                'username': getattr(message.forward_from_chat, 'username', None),
                'type': str(message.forward_from_chat.type)
            }
        
        message_data['forward_info'] = forward_info
        self.extracted_data['forwards'].append({
            'message_id': message.id,
            'chat_id': message.chat.id,
            'forward_info': forward_info
        })
    
    def _analyze_members_comprehensive(self, members: List[ChatMember]):
        """تحلیل جامع اعضا"""
        logger.info(f"👥 Analyzing {len(members)} members comprehensively...")
        
        for member in members:
            try:
                member_data = {
                    'user': self._extract_user_data(member.user),
                    'status': str(member.status),
                    'joined_date': member.joined_date.isoformat() if member.joined_date else None,
                    'invited_by': self._extract_user_data(member.invited_by) if hasattr(member, 'invited_by') and member.invited_by else None,
                    'promoted_by': self._extract_user_data(member.promoted_by) if hasattr(member, 'promoted_by') and member.promoted_by else None,
                    'restricted_by': self._extract_user_data(member.restricted_by) if hasattr(member, 'restricted_by') and member.restricted_by else None,
                    'is_member': getattr(member, 'is_member', True),
                    'is_administrator': getattr(member, 'is_administrator', False),
                    'is_creator': getattr(member, 'is_creator', False),
                    'can_manage_chat': getattr(member, 'can_manage_chat', False),
                    'can_delete_messages': getattr(member, 'can_delete_messages', False),
                    'can_manage_video_chats': getattr(member, 'can_manage_video_chats', False),
                    'can_restrict_members': getattr(member, 'can_restrict_members', False),
                    'can_promote_members': getattr(member, 'can_promote_members', False),
                    'can_change_info': getattr(member, 'can_change_info', False),
                    'can_invite_users': getattr(member, 'can_invite_users', False),
                    'can_pin_messages': getattr(member, 'can_pin_messages', False),
                    'can_post_messages': getattr(member, 'can_post_messages', False),
                    'can_edit_messages': getattr(member, 'can_edit_messages', False),
                    'can_delete_stories': getattr(member, 'can_delete_stories', False),
                    'can_edit_stories': getattr(member, 'can_edit_stories', False),
                    'can_post_stories': getattr(member, 'can_post_stories', False),
                    'until_date': member.until_date.isoformat() if hasattr(member, 'until_date') and member.until_date else None
                }
                
                self.extracted_data['members'].append(member_data)
                
            except Exception as e:
                user_id = getattr(member.user, 'id', 'unknown') if hasattr(member, 'user') and member.user else 'unknown'
                logger.error(f"❌ Error processing member {user_id}: {e}")
                continue
        
        logger.info(f"✅ Member analysis completed: {len(self.extracted_data['members'])} members processed")
    
    def _calculate_statistics(self):
        """محاسبه آمار کلی"""
        stats = {
            'total_messages': len(self.extracted_data['messages']),
            'total_members': len(self.extracted_data['members']),
            'total_media_files': len(self.extracted_data['media_files']),
            'total_reactions': len(self.extracted_data['reactions']),
            'total_forwards': len(self.extracted_data['forwards']),
            'message_types': {},
            'media_types': {},
            'member_statuses': {},
            'user_activity': {},
            'bot_count': 0,
            'verified_users': 0,
            'restricted_users': 0
        }
        
        # آمار پیام‌ها
        for message in self.extracted_data['messages']:
            media_type = message.get('media_type', 'text')
            stats['message_types'][media_type] = stats['message_types'].get(media_type, 0) + 1
        
        # آمار مدیا
        for media in self.extracted_data['media_files']:
            media_type = media['media_info'].get('type', 'unknown')
            stats['media_types'][media_type] = stats['media_types'].get(media_type, 0) + 1
        
        # آمار اعضا
        for member in self.extracted_data['members']:
            status = member.get('status', 'unknown')
            stats['member_statuses'][status] = stats['member_statuses'].get(status, 0) + 1
            
            user = member.get('user')
            if user:
                if user.get('is_bot'):
                    stats['bot_count'] += 1
                if user.get('is_verified'):
                    stats['verified_users'] += 1
                if user.get('is_restricted'):
                    stats['restricted_users'] += 1
        
        self.extracted_data['statistics'] = stats
        logger.info(f"📊 Statistics calculated: {stats['total_messages']} messages, {stats['total_members']} members")
    
    def save_comprehensive_results(self, output_path: str):
        """ذخیره نتایج جامع"""
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # تبدیل datetime objects به string
            def convert_datetime(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                return obj
            
            # ذخیره با فرمت JSON
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.extracted_data, f, ensure_ascii=False, indent=2, default=convert_datetime)
            
            logger.info(f"💾 Comprehensive results saved to: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving comprehensive results: {e}")
            return False 
    
    def save_links_to_file(self, output_path: str):
        """ذخیره تمام لینک‌های استخراج شده در فایل جداگانه"""
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # دسته‌بندی لینک‌ها
            categorized_links = {
                'telegram_invite_links': [],
                'telegram_public_links': [],
                'youtube_links': [],
                'instagram_links': [],
                'twitter_links': [],
                'facebook_links': [],
                'other_links': []
            }
            
            # دسته‌بندی لینک‌ها
            for link in self.all_links:
                link_info = self.categorize_link(link)
                
                if link_info['is_telegram']:
                    if link_info['is_invite_link']:
                        categorized_links['telegram_invite_links'].append(link_info)
                    else:
                        categorized_links['telegram_public_links'].append(link_info)
                elif link_info['type'] == 'youtube':
                    categorized_links['youtube_links'].append(link_info)
                elif link_info['type'] == 'instagram':
                    categorized_links['instagram_links'].append(link_info)
                elif link_info['type'] == 'twitter':
                    categorized_links['twitter_links'].append(link_info)
                elif link_info['type'] == 'facebook':
                    categorized_links['facebook_links'].append(link_info)
                else:
                    categorized_links['other_links'].append(link_info)
            
            # ذخیره در فایل JSON
            links_data = {
                'extraction_date': datetime.now().isoformat(),
                'total_links': len(self.all_links),
                'categorized_links': categorized_links,
                'all_links': list(self.all_links)
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(links_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"💾 Links saved to: {output_file}")
            
            # نمایش آمار
            logger.info(f"📊 Links Statistics:")
            logger.info(f"   🔗 Total unique links: {len(self.all_links)}")
            logger.info(f"   📱 Telegram invite links: {len(categorized_links['telegram_invite_links'])}")
            logger.info(f"   📱 Telegram public links: {len(categorized_links['telegram_public_links'])}")
            logger.info(f"   📺 YouTube links: {len(categorized_links['youtube_links'])}")
            logger.info(f"   📷 Instagram links: {len(categorized_links['instagram_links'])}")
            logger.info(f"   🐦 Twitter links: {len(categorized_links['twitter_links'])}")
            logger.info(f"   👥 Facebook links: {len(categorized_links['facebook_links'])}")
            logger.info(f"   🌐 Other links: {len(categorized_links['other_links'])}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving links: {e}")
            return False
    
    def save_links_to_txt(self, output_path: str):
        """ذخیره لینک‌ها در فایل متنی ساده"""
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("🔗 لینک‌های استخراج شده از گروه تلگرام\n")
                f.write("=" * 50 + "\n")
                f.write(f"📅 تاریخ استخراج: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"📊 تعداد کل لینک‌ها: {len(self.all_links)}\n\n")
                
                # دسته‌بندی و ذخیره
                categories = {
                    '📱 لینک‌های دعوت تلگرام': [],
                    '📱 لینک‌های عمومی تلگرام': [],
                    '📺 لینک‌های یوتیوب': [],
                    '📷 لینک‌های اینستاگرام': [],
                    '🐦 لینک‌های توییتر': [],
                    '👥 لینک‌های فیسبوک': [],
                    '🌐 سایر لینک‌ها': []
                }
                
                for link in self.all_links:
                    link_info = self.categorize_link(link)
                    
                    if link_info['is_telegram']:
                        if link_info['is_invite_link']:
                            categories['📱 لینک‌های دعوت تلگرام'].append(link)
                        else:
                            categories['📱 لینک‌های عمومی تلگرام'].append(link)
                    elif link_info['type'] == 'youtube':
                        categories['📺 لینک‌های یوتیوب'].append(link)
                    elif link_info['type'] == 'instagram':
                        categories['📷 لینک‌های اینستاگرام'].append(link)
                    elif link_info['type'] == 'twitter':
                        categories['🐦 لینک‌های توییتر'].append(link)
                    elif link_info['type'] == 'facebook':
                        categories['👥 لینک‌های فیسبوک'].append(link)
                    else:
                        categories['🌐 سایر لینک‌ها'].append(link)
                
                # نوشتن در فایل
                for category, links in categories.items():
                    if links:
                        f.write(f"\n{category} ({len(links)}):\n")
                        f.write("-" * 30 + "\n")
                        for link in links:
                            f.write(f"{link}\n")
                        f.write("\n")
            
            logger.info(f"💾 Links TXT saved to: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving links TXT: {e}")
            return False 