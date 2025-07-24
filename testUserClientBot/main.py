import os
import json
import asyncio
from datetime import datetime
from pyrogram import Client
from pyrogram.types import Chat
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی
load_dotenv()

class TelegramGroupsChannelsExporter:
    def __init__(self):
        self.api_id = os.getenv('API_ID')
        self.api_hash = os.getenv('API_HASH')
        self.session_string = os.getenv('SESSION_STRING')
        
        if not all([self.api_id, self.api_hash, self.session_string]):
            raise ValueError("لطفاً تمام متغیرهای محیطی را در فایل .env تنظیم کنید")
        
        # استفاده از Session String
        self.app = Client(
            "my_account",
            api_id=int(self.api_id),
            api_hash=self.api_hash,
            session_string=self.session_string
        )
    
    async def get_chats_info(self):
        """دریافت اطلاعات گروه‌ها و کانال‌ها"""
        groups = []
        channels = []
        supergroups = []
        
        print("در حال دریافت لیست چت‌ها...")
        
        try:
            async for dialog in self.app.get_dialogs():
                chat = dialog.chat
                
                chat_info = {
                    'id': chat.id,
                    'title': chat.title or chat.first_name or 'بدون نام',
                    'username': f"@{chat.username}" if chat.username else None,
                    'type': chat.type.value,
                    'members_count': getattr(chat, 'members_count', None),
                    'description': getattr(chat, 'description', None),
                    'is_verified': getattr(chat, 'is_verified', False),
                    'is_scam': getattr(chat, 'is_scam', False),
                    'is_fake': getattr(chat, 'is_fake', False)
                }
                
                # تفکیک بر اساس نوع چت
                if chat.type.value == 'group':
                    groups.append(chat_info)
                elif chat.type.value == 'channel':
                    channels.append(chat_info)
                elif chat.type.value == 'supergroup':
                    supergroups.append(chat_info)
                
                print(f"✅ {chat_info['title']} - {chat_info['type']}")
        
        except Exception as e:
            print(f"خطا در دریافت چت‌ها: {e}")
            return {'groups': [], 'channels': [], 'supergroups': []}
        
        return {
            'groups': groups,
            'channels': channels,
            'supergroups': supergroups
        }
    
    async def save_to_json(self, data, filename='telegram_chats.json'):
        """ذخیره داده‌ها در فایل JSON"""
        export_data = {
            'export_date': datetime.now().isoformat(),
            'total_groups': len(data['groups']),
            'total_channels': len(data['channels']),
            'total_supergroups': len(data['supergroups']),
            'total_all': len(data['groups']) + len(data['channels']) + len(data['supergroups']),
            'chats': data
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        print(f"📁 داده‌ها در فایل {filename} ذخیره شد")
    
    async def save_to_txt(self, data, filename='telegram_chats.txt'):
        """ذخیره داده‌ها در فایل متنی"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"تاریخ استخراج: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n\n")
            
            # گروه‌های عادی
            f.write(f"🔸 گروه‌های عادی ({len(data['groups'])} عدد):\n")
            f.write("-" * 30 + "\n")
            for i, group in enumerate(data['groups'], 1):
                f.write(f"{i}. {group['title']}\n")
                f.write(f"   ID: {group['id']}\n")
                if group['username']:
                    f.write(f"   Username: {group['username']}\n")
                if group['members_count']:
                    f.write(f"   تعداد اعضا: {group['members_count']}\n")
                if group['is_verified']:
                    f.write(f"   ✅ تایید شده\n")
                f.write("\n")
            
            # سوپرگروه‌ها
            f.write(f"\n🔹 سوپرگروه‌ها ({len(data['supergroups'])} عدد):\n")
            f.write("-" * 30 + "\n")
            for i, supergroup in enumerate(data['supergroups'], 1):
                f.write(f"{i}. {supergroup['title']}\n")
                f.write(f"   ID: {supergroup['id']}\n")
                if supergroup['username']:
                    f.write(f"   Username: {supergroup['username']}\n")
                if supergroup['members_count']:
                    f.write(f"   تعداد اعضا: {supergroup['members_count']}\n")
                if supergroup['is_verified']:
                    f.write(f"   ✅ تایید شده\n")
                f.write("\n")
            
            # کانال‌ها
            f.write(f"\n📢 کانال‌ها ({len(data['channels'])} عدد):\n")
            f.write("-" * 30 + "\n")
            for i, channel in enumerate(data['channels'], 1):
                f.write(f"{i}. {channel['title']}\n")
                f.write(f"   ID: {channel['id']}\n")
                if channel['username']:
                    f.write(f"   Username: {channel['username']}\n")
                if channel['members_count']:
                    f.write(f"   تعداد اعضا: {channel['members_count']}\n")
                if channel['is_verified']:
                    f.write(f"   ✅ تایید شده\n")
                f.write("\n")
        
        print(f"📄 داده‌ها در فایل {filename} ذخیره شد")
    
    async def save_to_csv(self, data, filename='telegram_chats.csv'):
        """ذخیره داده‌ها در فایل CSV"""
        import csv
        
        all_chats = data['groups'] + data['supergroups'] + data['channels']
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['title', 'username', 'type', 'id', 'members_count', 'description', 'is_verified', 'is_scam']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for chat in all_chats:
                writer.writerow({
                    'title': chat['title'],
                    'username': chat['username'] or '',
                    'type': chat['type'],
                    'id': chat['id'],
                    'members_count': chat['members_count'] or 0,
                    'description': (chat['description'] or '')[:200],  # محدود کردن توضیحات
                    'is_verified': chat.get('is_verified', False),
                    'is_scam': chat.get('is_scam', False)
                })
        
        print(f"📊 فایل CSV در {filename} ذخیره شد")
    
    async def get_user_info(self):
        """دریافت اطلاعات کاربر"""
        try:
            me = await self.app.get_me()
            return {
                'id': me.id,
                'first_name': me.first_name,
                'last_name': me.last_name,
                'username': me.username,
                'phone_number': me.phone_number
            }
        except Exception as e:
            print(f"خطا در دریافت اطلاعات کاربر: {e}")
            return None
    
    async def run(self):
        """اجرای برنامه اصلی"""
        try:
            await self.app.start()
            print("✅ اتصال به تلگرام برقرار شد")
            
            # نمایش اطلاعات کاربر
            user_info = await self.get_user_info()
            if user_info:
                print(f"👤 کاربر: {user_info['first_name']} {user_info['last_name'] or ''}")
                if user_info['username']:
                    print(f"🔗 یوزرنیم: @{user_info['username']}")
                print()
            
            # دریافت اطلاعات چت‌ها
            chats_data = await self.get_chats_info()
            
            # نمایش آمار
            print(f"\n📊 آمار کلی:")
            print(f"├── گروه‌های عادی: {len(chats_data['groups'])}")
            print(f"├── سوپرگروه‌ها: {len(chats_data['supergroups'])}")
            print(f"├── کانال‌ها: {len(chats_data['channels'])}")
            print(f"└── مجموع: {len(chats_data['groups']) + len(chats_data['supergroups']) + len(chats_data['channels'])}")
            
            print("\n💾 در حال ذخیره فایل‌ها...")
            
            # ذخیره در فرمت‌های مختلف
            await self.save_to_json(chats_data)
            await self.save_to_txt(chats_data)
            await self.save_to_csv(chats_data)
            
            print("\n🎉 عملیات با موفقیت انجام شد!")
            
        except Exception as e:
            print(f"❌ خطا در اجرای برنامه: {e}")
        finally:
            await self.app.stop()

async def main():
    try:
        exporter = TelegramGroupsChannelsExporter()
        await exporter.run()
    except Exception as e:
        print(f"❌ خطا: {e}")

if __name__ == "__main__":
    asyncio.run(main())
