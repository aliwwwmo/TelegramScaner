import os
import json
import asyncio
import re
from datetime import datetime
from pyrogram import Client
from pyrogram.errors import (
    ChannelPrivate, 
    UsernameNotOccupied, 
    PeerIdInvalid,
    UserAlreadyParticipant,
    InviteHashExpired,
    UserNotParticipant,
    FloodWait,
    ChannelInvalid,
    UsernameInvalid,
    AuthKeyUnregistered
)
from dotenv import load_dotenv

load_dotenv()

class TelegramMessagesExtractor:
    def __init__(self):
        self.api_id = os.getenv('API_ID')
        self.api_hash = os.getenv('API_HASH')
        self.session_string = os.getenv('SESSION_STRING')
        
        if not all([self.api_id, self.api_hash, self.session_string]):
            raise ValueError("لطفاً تمام متغیرهای محیطی را در فایل .env تنظیم کنید")
        
        self.app = Client(
            "message_extractor",
            api_id=int(self.api_id),
            api_hash=self.api_hash,
            session_string=self.session_string
        )
    
    def sanitize_filename(self, filename):
        """escape filename"""
        if not filename:
            return "unnamed_chat"
        
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        clean_name = filename
        for char in invalid_chars:
            clean_name = clean_name.replace(char, '_')
        
        clean_name = re.sub(r'[^\w\s.-]', '_', clean_name, flags=re.UNICODE)
        clean_name = re.sub(r'\s+', '_', clean_name)
        clean_name = re.sub(r'_+', '_', clean_name)
        clean_name = clean_name.strip('_.')
        
        if len(clean_name) > 50:
            clean_name = clean_name[:50].rstrip('_.')
        
        if not clean_name:
            clean_name = "unnamed_chat"
        
        return clean_name
    
    def extract_username_from_link(self, link):
        """استخراج username از لینک تلگرام"""
        try:
            if 't.me/' in link:
                username = link.split('t.me/')[-1].split('?')[0].split('/')[0]
            elif 'telegram.me/' in link:
                username = link.split('telegram.me/')[-1].split('?')[0].split('/')[0]
            else:
                return link
            
            # حذف کاراکترهای اضافی
            username = username.strip()
            if username.startswith('@'):
                username = username[1:]
            
            return username
        except:
            return link
    
    async def try_get_chat_info_without_join(self, username):
        """تلاش برای دریافت اطلاعات چت بدون جوین"""
        methods = [
            f"@{username}",
            username,
            f"https://t.me/{username}",
        ]
        
        for method in methods:
            try:
                print(f"🔍 روش {methods.index(method)+1}: تلاش با {method}")
                chat = await self.app.get_chat(method)
                
                print(f"✅ موفق! اطلاعات چت دریافت شد:")
                print(f"   - نام: {chat.title}")
                print(f"   - شناسه: {chat.id}")
                print(f"   - نوع: {chat.type.value}")
                if hasattr(chat, 'username') and chat.username:
                    print(f"   - یوزرنیم: @{chat.username}")
                if hasattr(chat, 'members_count') and chat.members_count:
                    print(f"   - تعداد اعضا: {chat.members_count:,}")
                
                return chat
                
            except ChannelPrivate:
                print(f"❌ چت خصوصی است")
                continue
            except UsernameNotOccupied:
                print(f"❌ یوزرنیم وجود ندارد")
                continue
            except UsernameInvalid:
                print(f"❌ یوزرنیم نامعتبر")
                continue
            except ChannelInvalid:
                print(f"❌ کانال نامعتبر")
                continue
            except PeerIdInvalid:
                print(f"❌ شناسه نامعتبر")
                continue
            except Exception as e:
                print(f"❌ خطا: {e}")
                continue
        
        return None
    
    async def try_extract_messages_without_join(self, chat, message_count=20):
        """تلاش برای استخراج پیام‌ها بدون جوین"""
        messages = []
        
        methods_to_try = [
            ("get_chat_history", chat.id),
            ("get_chat_history", f"@{chat.username}") if hasattr(chat, 'username') and chat.username else None,
            ("iter_chat_history", chat.id),
            ("iter_chat_history", f"@{chat.username}") if hasattr(chat, 'username') and chat.username else None,
        ]
        
        # حذف موارد None
        methods_to_try = [m for m in methods_to_try if m is not None]
        
        for method_name, chat_identifier in methods_to_try:
            try:
                print(f"🔍 روش {methods_to_try.index((method_name, chat_identifier))+1}: {method_name} با {chat_identifier}")
                
                message_counter = 0
                
                if method_name == "get_chat_history":
                    async for message in self.app.get_chat_history(chat_identifier, limit=message_count):
                        message_data = await self.process_message(message)
                        messages.append(message_data)
                        message_counter += 1
                        print(f"✅ پیام {message_counter}/{message_count} - ID: {message.id}")
                        
                        if message_counter >= message_count:
                            break
                
                elif method_name == "iter_chat_history":
                    async for message in self.app.iter_chat_history(chat_identifier):
                        message_data = await self.process_message(message)
                        messages.append(message_data)
                        message_counter += 1
                        print(f"✅ پیام {message_counter}/{message_count} - ID: {message.id}")
                        
                        if message_counter >= message_count:
                            break
                
                if messages:
                    print(f"🎉 {len(messages)} پیام با موفقیت استخراج شد!")
                    return messages
                    
            except ChannelPrivate:
                print(f"❌ چت خصوصی - نیاز به دسترسی")
                continue
            except UserNotParticipant:
                print(f"❌ شما عضو نیستید")
                continue
            except PeerIdInvalid:
                print(f"❌ شناسه نامعتبر")
                continue
            except Exception as e:
                print(f"❌ خطا: {e}")
                continue
        
        return messages
    
    async def process_message(self, message):
        """پردازش یک پیام و استخراج اطلاعات"""
        from_user_info = None
        if message.from_user:
            from_user_info = {
                'id': message.from_user.id,
                'first_name': message.from_user.first_name,
                'last_name': message.from_user.last_name,
                'username': message.from_user.username,
                'is_bot': getattr(message.from_user, 'is_bot', False)
            }
        
        message_data = {
            'message_id': message.id,
            'date': message.date.isoformat() if message.date else None,
            'date_formatted': message.date.strftime('%Y-%m-%d %H:%M:%S') if message.date else None,
            'text': message.text or message.caption or '',
            'from_user': from_user_info,
            'media_type': None,
            'has_media': False,
            'views': getattr(message, 'views', None),
            'forwards': getattr(message, 'forwards', None),
            'reply_to_message_id': message.reply_to_message_id,
            'edit_date': message.edit_date.isoformat() if message.edit_date else None
        }
        
        # بررسی نوع رسانه
        if message.photo:
            message_data['media_type'] = 'photo'
            message_data['has_media'] = True
        elif message.video:
            message_data['media_type'] = 'video'
            message_data['has_media'] = True
        elif message.document:
            message_data['media_type'] = 'document'
            message_data['has_media'] = True
        elif message.audio:
            message_data['media_type'] = 'audio'
            message_data['has_media'] = True
        elif message.voice:
            message_data['media_type'] = 'voice'
            message_data['has_media'] = True
        elif message.sticker:
            message_data['media_type'] = 'sticker'
            message_data['has_media'] = True
        elif message.animation:
            message_data['media_type'] = 'gif'
            message_data['has_media'] = True
        
        return message_data
    
    async def save_messages_json(self, messages, chat_info, filename):
        """ذخیره پیام‌ها در فایل JSON"""
        data = {
            'extraction_date': datetime.now().isoformat(),
            'extraction_date_formatted': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'chat_info': chat_info,
            'message_count': len(messages),
            'messages': messages
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"📁 فایل JSON در {filename} ذخیره شد")
            return True
        except Exception as e:
            print(f"❌ خطا در ذخیره فایل JSON: {e}")
            return False
    
    async def save_messages_txt(self, messages, chat_info, filename):
        """ذخیره پیام‌ها در فایل متنی"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("📱 استخراج پیام‌های تلگرام (بدون جوین)\n")
                f.write("=" * 60 + "\n")
                f.write(f"📅 تاریخ استخراج: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"📊 تعداد پیام‌ها: {len(messages)}\n")
                
                if chat_info:
                    f.write(f"📋 نام چت: {chat_info['title']}\n")
                    f.write(f"🆔 شناسه چت: {chat_info['id']}\n")
                    if chat_info.get('username'):
                        f.write(f"👤 یوزرنیم: @{chat_info['username']}\n")
                    f.write(f"📂 نوع چت: {chat_info['type']}\n")
                    if chat_info.get('members_count'):
                        f.write(f"👥 تعداد اعضا: {chat_info['members_count']:,}\n")
                
                f.write("=" * 60 + "\n\n")
                
                for i, msg in enumerate(messages, 1):
                    f.write(f"📝 پیام {i}:\n")
                    f.write(f"├── شناسه: {msg['message_id']}\n")
                    f.write(f"├── تاریخ: {msg['date_formatted'] or 'نامشخص'}\n")
                    
                    if msg['from_user']:
                        user_name = f"{msg['from_user']['first_name'] or ''} {msg['from_user']['last_name'] or ''}".strip()
                        if msg['from_user']['username']:
                            user_name += f" (@{msg['from_user']['username']})"
                        if msg['from_user']['is_bot']:
                            user_name += " [BOT]"
                        f.write(f"├── فرستنده: {user_name}\n")
                    else:
                        f.write(f"├── فرستنده: نامشخص (احتمالاً کانال)\n")
                    
                    if msg['text']:
                        text_preview = msg['text'][:200] + "..." if len(msg['text']) > 200 else msg['text']
                        f.write(f"├── متن: {text_preview}\n")
                    
                    if msg['has_media']:
                        f.write(f"├── رسانه: {msg['media_type']}\n")
                    
                    if msg['views']:
                        f.write(f"├── بازدید: {msg['views']:,}\n")
                    
                    if msg['forwards']:
                        f.write(f"├── فوروارد: {msg['forwards']:,}\n")
                    
                    if msg['reply_to_message_id']:
                        f.write(f"└── پاسخ به پیام: {msg['reply_to_message_id']}\n")
                    else:
                        f.write(f"└── (پایان پیام)\n")
                    
                    f.write("\n" + "-" * 50 + "\n\n")
            
            print(f"📄 فایل متنی در {filename} ذخیره شد")
            return True
        except Exception as e:
            print(f"❌ خطا در ذخیره فایل TXT: {e}")
            return False
    
    async def run(self, link, message_count=20):
        """اجرای برنامه اصلی"""
        try:
            print("🔄 در حال اتصال به تلگرام...")
            await self.app.start()
            print("✅ اتصال به تلگرام برقرار شد")
            
            # استخراج username از لینک
            username = self.extract_username_from_link(link)
            print(f"🎯 Username استخراج شده: {username}")
            
            # تلاش برای دریافت اطلاعات چت بدون جوین
            print(f"\n🔍 تلاش برای دسترسی به چت بدون جوین...")
            chat = await self.try_get_chat_info_without_join(username)
            
            if not chat:
                print("❌ نتوانستیم به اطلاعات چت دسترسی پیدا کنیم")
                return False
            
            # تبدیل اطلاعات چت به dictionary
            chat_info = {
                'id': chat.id,
                'title': chat.title,
                'username': getattr(chat, 'username', None),
                'type': chat.type.value,
                'members_count': getattr(chat, 'members_count', None),
                'description': getattr(chat, 'description', None)
            }
            
            # تلاش برای استخراج پیام‌ها بدون جوین
            print(f"\n📥 تلاش برای استخراج {message_count} پیام بدون جوین...")
            messages = await self.try_extract_messages_without_join(chat, message_count)
            
            if not messages:
                print("❌ نتوانستیم پیام‌ها را بدون جوین استخراج کنیم")
                print("💡 احتمالاً این چت خصوصی است و نیاز به عضویت دارد")
                return False
            
            # تولید نام فایل امن
            chat_name = self.sanitize_filename(chat.title)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            base_filename = f"messages_{chat_name}_{timestamp}"
            
            json_filename = f"{base_filename}.json"
            txt_filename = f"{base_filename}.txt"
            
            counter = 1
            while os.path.exists(json_filename) or os.path.exists(txt_filename):
                json_filename = f"{base_filename}_{counter}.json"
                txt_filename = f"{base_filename}_{counter}.txt"
                counter += 1
            
            print(f"\n💾 در حال ذخیره فایل‌ها...")
            json_saved = await self.save_messages_json(messages, chat_info, json_filename)
            txt_saved = await self.save_messages_txt(messages, chat_info, txt_filename)
            
            print(f"\n🎉 عملیات با موفقیت تکمیل شد!")
            print(f"📊 خلاصه:")
            print(f"├── تعداد پیام‌های استخراج شده: {len(messages)}")
            if json_saved:
                print(f"├── فایل JSON: ✅ {json_filename}")
            if txt_saved:
                print(f"└── فایل TXT: ✅ {txt_filename}")
            
            if messages:
                print(f"\n📝 نمونه پیام‌ها:")
                for i, msg in enumerate(messages[:3], 1):
                    text_preview = msg['text'][:80] + "..." if len(msg['text']) > 80 else msg['text']
                    print(f"  {i}. {text_preview or '[رسانه]'}")
                    
            return True
                
        except Exception as e:
            print(f"❌ خطا در اجرای برنامه: {e}")
            return False
        finally:
            try:
                await self.app.stop()
                print("🔄 اتصال به تلگرام قطع شد")
            except:
                pass

async def main():
    print("🚀 استخراج‌کننده پیام‌های تلگرام (بدون جوین)")
    print("=" * 60)
    
    # لینک تست
    test_link = "https://t.me/R6FanGp"
    message_count = 20
    
    print(f"🎯 لینک: {test_link}")
    print(f"📊 تعداد پیام: {message_count}")
    print(f"🔐 روش: بدون جوین شدن")
    print("-" * 60)
    
    try:
        extractor = TelegramMessagesExtractor()
        success = await extractor.run(test_link, message_count)
        
        if success:
            print("✅ عملیات با موفقیت انجام شد!")
        else:
            print("❌ عملیات ناموفق بود")
            
    except KeyboardInterrupt:
        print("\n⏹️ عملیات توسط کاربر متوقف شد")
    except Exception as e:
        print(f"❌ خطا: {e}")

if __name__ == "__main__":
    asyncio.run(main())
