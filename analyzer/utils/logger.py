import logging
import os
from datetime import datetime

def setup_logger():
    """تنظیم logger"""
    # تنظیم سطح لاگ
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    # تنظیم فرمت
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # ایجاد logger
    logger = logging.getLogger('telegram_analyzer')
    logger.setLevel(getattr(logging, log_level))
    
    # پاک کردن handlerهای قبلی
    logger.handlers.clear()
    
    # console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # file handler
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

# ایجاد logger برای استفاده در کل پروژه
logger = setup_logger()

# کلاس Logger برای سازگاری
class Logger:
    @staticmethod
    def info(message):
        logger.info(message)
    
    @staticmethod
    def error(message):
        logger.error(message)
    
    @staticmethod
    def warning(message):
        logger.warning(message)
    
    @staticmethod
    def debug(message):
        logger.debug(message)
