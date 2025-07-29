import os
from typing import Optional
from dataclasses import dataclass
from pathlib import Path

def str_to_bool(value: str) -> bool:
    """تبدیل string به boolean"""
    return value.lower() in ('true', '1', 'yes', 'on')

def ensure_dir(path: str) -> str:
    """اطمینان از وجود پوشه و ایجاد آن در صورت عدم وجود"""
    try:
        # تبدیل به Path object برای مدیریت بهتر مسیرها
        path_obj = Path(path)
        
        # اگر مسیر نسبی است، آن را نسبت به مسیر فعلی بساز
        if not path_obj.is_absolute():
            # مسیر فعلی پروژه (پوشه analyzer)
            current_dir = Path(__file__).parent.parent
            path_obj = current_dir / path
        
        # ایجاد پوشه با parents=True برای ایجاد پوشه‌های والد
        path_obj.mkdir(parents=True, exist_ok=True)
        
        # برگرداندن مسیر به صورت string
        return str(path_obj)
    except Exception as e:
        print(f"⚠️ Could not create directory {path}: {e}")
        # در صورت خطا، مسیر فعلی را برگردان
        return str(Path.cwd() / path)

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
            if len(session_string) > 0:
                print(f"✅ SESSION_STRING loaded (length: {len(session_string)})")
        
        return cls(
            api_id=api_id,
            api_hash=api_hash,
            session_string=session_string
        )

@dataclass
class MessageSettings:
    """تنظیمات پیام‌ها"""
    limit: int
    batch_size: int
    delay_between_batches: int
    
    @classmethod
    def from_env(cls) -> 'MessageSettings':
        return cls(
            limit=int(os.getenv('MESSAGE_LIMIT', '1000')),
            batch_size=int(os.getenv('MESSAGE_BATCH_SIZE', '100')),
            delay_between_batches=int(os.getenv('DELAY_BETWEEN_BATCHES', '1'))
        )

@dataclass
class MemberSettings:
    """تنظیمات اعضا"""
    get_members: bool
    member_limit: int
    member_batch_size: int
    include_bots: bool
    
    @classmethod
    def from_env(cls) -> 'MemberSettings':
        return cls(
            get_members=str_to_bool(os.getenv('GET_MEMBERS', 'true')),
            member_limit=int(os.getenv('MEMBER_LIMIT', '5000')),
            member_batch_size=int(os.getenv('MEMBER_BATCH_SIZE', '200')),
            include_bots=str_to_bool(os.getenv('INCLUDE_BOTS', 'true'))
        )

@dataclass
class AnalysisSettings:
    """تنظیمات تحلیل"""
    save_message_text: bool
    analyze_media: bool
    track_reactions: bool
    track_forwards: bool
    deep_scan: bool
    
    @classmethod
    def from_env(cls) -> 'AnalysisSettings':
        return cls(
            save_message_text=str_to_bool(os.getenv('SAVE_MESSAGE_TEXT', 'true')),
            analyze_media=str_to_bool(os.getenv('ANALYZE_MEDIA', 'true')),
            track_reactions=str_to_bool(os.getenv('TRACK_REACTIONS', 'true')),
            track_forwards=str_to_bool(os.getenv('TRACK_FORWARDS', 'true')),
            deep_scan=str_to_bool(os.getenv('DEEP_SCAN', 'true'))
        )

@dataclass
class FileSettings:
    """تنظیمات فایل‌ها"""
    users_dir: str
    results_dir: str
    logs_dir: str
    backup_results: bool
    input_file: str
    output_file: str
    
    @classmethod
    def from_env(cls) -> 'FileSettings':
        # دریافت مسیرها از environment variables
        users_dir = ensure_dir(os.getenv('USERS_DIR', 'users'))
        results_dir = ensure_dir(os.getenv('RESULTS_DIR', 'results'))
        logs_dir = ensure_dir(os.getenv('LOGS_DIR', 'logs'))
        
        # ایجاد نمونه فایل links.txt اگر وجود نداشته باشد
        input_file = os.getenv('INPUT_FILE', os.getenv('LINKS_FILE', 'links.txt'))
        if not os.path.exists(input_file):
            try:
                with open(input_file, 'w', encoding='utf-8') as f:
                    f.write("# Add your Telegram chat links here, one per line\n")
                    f.write("# Examples:\n")
                    f.write("# https://t.me/example_channel\n")
                    f.write("# @example_group\n")
                    f.write("# +1234567890  (for private chats)\n")
                print(f"✅ Created sample input file: {input_file}")
            except Exception as e:
                print(f"⚠️ Could not create input file {input_file}: {e}")
        
        return cls(
            users_dir=users_dir,
            results_dir=results_dir,
            logs_dir=logs_dir,
            backup_results=str_to_bool(os.getenv('BACKUP_RESULTS', 'true')),
            input_file=input_file,
            output_file=os.getenv('OUTPUT_FILE', 'my_chats.json')
        )

@dataclass
class FilterSettings:
    """تنظیمات فیلتر پیام‌ها"""
    filter_scan_messages: bool
    filter_bot_messages: bool
    filter_system_messages: bool
    scan_keywords: list
    bot_keywords: list
    
    @classmethod
    def from_env(cls) -> 'FilterSettings':
        return cls(
            filter_scan_messages=str_to_bool(os.getenv('FILTER_SCAN_MESSAGES', 'true')),
            filter_bot_messages=str_to_bool(os.getenv('FILTER_BOT_MESSAGES', 'true')),
            filter_system_messages=str_to_bool(os.getenv('FILTER_SYSTEM_MESSAGES', 'true')),
            scan_keywords=[
                'scan_start_message',
                'scan start',
                'اسکن شروع',
                'شروع اسکن',
                'scanning started',
                'scan initiated'
            ],
            bot_keywords=[
                'bot',
                'system',
                'automated',
                'scan',
                'analysis'
            ]
        )

@dataclass
class MongoConfig:
    """تنظیمات MongoDB"""
    connection_string: str
    database_name: str
    collection_name: str
    
    @classmethod
    def from_env(cls) -> 'MongoConfig':
        """بارگذاری تنظیمات MongoDB از متغیرهای محیطی"""
        return cls(
            connection_string=os.getenv('MONGO_CONNECTION_STRING', 'mongodb://localhost:27017/'),
            database_name=os.getenv('MONGO_DATABASE', 'telegram_scanner'),
            collection_name=os.getenv('MONGO_COLLECTION', 'groups')
        )

@dataclass
class AnalysisConfig:
    """تنظیمات تحلیل (سازگاری با کد قبلی)"""
    input_file: str
    output_dir: str
    output_file: str
    message_limit: int
    messages_per_chat: int
    results_dir: str
    users_dir: str
    links_file: str
    use_database_for_groups: bool  # تنظیم جدید
    scan_interval_minutes: int  # فاصله زمانی اسکن
    resume_from_last_message: bool  # ادامه از آخرین پیام
    show_remaining_time: bool  # نمایش زمان باقی‌مانده
    
    @classmethod
    def from_env(cls) -> 'AnalysisConfig':
        """بارگذاری تنظیمات از متغیرهای محیطی"""
        # ایجاد پوشه‌ها قبل از تنظیم مسیرها
        results_dir = ensure_dir(os.getenv('RESULTS_DIR', 'results'))
        users_dir = ensure_dir(os.getenv('USERS_DIR', 'users'))
        output_dir = ensure_dir(os.getenv('OUTPUT_DIR', results_dir))
        
        # فایل ورودی
        input_file = os.getenv('LINKS_FILE', os.getenv('INPUT_FILE', 'links.txt'))
        links_file = input_file
        
        # تنظیم جدید برای انتخاب منبع گروه‌ها
        use_database_for_groups = str_to_bool(os.getenv('USE_DATABASE_FOR_GROUPS', 'true'))
        
        # تنظیمات اسکن هوشمند
        scan_interval_minutes = int(os.getenv('SCAN_INTERVAL_MINUTES', '30'))
        resume_from_last_message = str_to_bool(os.getenv('RESUME_FROM_LAST_MESSAGE', 'true'))
        show_remaining_time = str_to_bool(os.getenv('SHOW_REMAINING_TIME', 'true'))
        
        # ایجاد فایل نمونه اگر وجود ندارد
        if not os.path.exists(input_file):
            try:
                with open(input_file, 'w', encoding='utf-8') as f:
                    f.write("# Add your Telegram chat links here, one per line\n")
                    f.write("# Examples:\n")
                    f.write("# https://t.me/example_channel\n")
                    f.write("# @example_group\n")
                    f.write("# +1234567890  (for private chats)\n")
                print(f"✅ Created sample links file: {input_file}")
            except Exception as e:
                print(f"⚠️ Could not create links file {input_file}: {e}")
        
        return cls(
            input_file=input_file,
            output_dir=output_dir,
            output_file=os.getenv('OUTPUT_FILE', 'my_chats.json'),
            message_limit=int(os.getenv('MESSAGE_LIMIT', '100')),
            messages_per_chat=int(os.getenv('MESSAGES_PER_CHAT', '1000')),
            results_dir=results_dir,
            users_dir=users_dir,
            links_file=links_file,
            use_database_for_groups=use_database_for_groups,
            scan_interval_minutes=scan_interval_minutes,
            resume_from_last_message=resume_from_last_message,
            show_remaining_time=show_remaining_time
        )

# بارگذاری تنظیمات از environment variables
try:
    # بارگذاری فایل .env
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Environment variables loaded from .env file")
except ImportError:
    print("⚠️ python-dotenv not installed. Using system environment variables only.")
except Exception as e:
    print(f"⚠️ Could not load .env file: {e}")

# ایجاد نمونه‌های global
TELEGRAM_CONFIG = TelegramConfig.from_env()
MESSAGE_SETTINGS = MessageSettings.from_env()
MEMBER_SETTINGS = MemberSettings.from_env()
ANALYSIS_SETTINGS = AnalysisSettings.from_env()
FILE_SETTINGS = FileSettings.from_env()
ANALYSIS_CONFIG = AnalysisConfig.from_env()
MONGO_CONFIG = MongoConfig.from_env()
FILTER_SETTINGS = FilterSettings.from_env()

# برای سازگاری با کد قبلی
telegram_config = TELEGRAM_CONFIG
analysis_config = ANALYSIS_CONFIG

# نمایش وضعیت پوشه‌ها
def show_directory_status():
    """نمایش وضعیت پوشه‌های ایجاد شده"""
    dirs_to_check = {
        'Results': FILE_SETTINGS.results_dir,
        'Users': FILE_SETTINGS.users_dir,
        'Logs': FILE_SETTINGS.logs_dir,
    }
    
    print("📁 Directory Status:")
    for name, path in dirs_to_check.items():
        if os.path.exists(path):
            print(f"   ✅ {name}: {path}")
        else:
            print(f"   ❌ {name}: {path} (not found)")
    
    # بررسی فایل ورودی
    if os.path.exists(FILE_SETTINGS.input_file):
        print(f"   ✅ Input file: {FILE_SETTINGS.input_file}")
    else:
        print(f"   ❌ Input file: {FILE_SETTINGS.input_file} (not found)")

print("🔧 Configuration loaded successfully:")
print(f"   📱 API ID: {TELEGRAM_CONFIG.api_id}")
print(f"   📥 Message Limit: {MESSAGE_SETTINGS.limit}")
print(f"   👥 Get Members: {MEMBER_SETTINGS.get_members}")
print(f"   📁 Results Dir: {FILE_SETTINGS.results_dir}")

# نمایش وضعیت پوشه‌ها
show_directory_status()
