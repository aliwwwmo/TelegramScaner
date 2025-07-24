import pandas as pd
from browser_manager import BrowserManager
from data_collector import DataCollector
from telegram_predictor import TelegramPredictor
from telegram_scraper import TelegramScraper

# ساخت اشیاء
browser_manager = BrowserManager()
collector = DataCollector(browser_manager)
predictor = TelegramPredictor()
scraper = TelegramScraper(browser_manager, predictor)

# پرسیدن از کاربر برای جمع‌آوری داده
response = input("آیا می‌خواهید داده برای یادگیری ماشین جمع‌آوری شود؟ (بله/خیر): ").strip().lower()

if response in ["بله", "yes", "y"]:
    print("شروع جمع‌آوری داده برای یادگیری ماشین...")
    collector.collect("site:t.me/joinchat", max_pages=3)

    # آموزش مدل با داده‌های جدید
    data = pd.read_csv("training_data.csv")
    urls = data["URL"]
    labels = data["Label"]
    predictor.train(urls, labels)
else:
    print("جمع‌آوری داده رد شد، مستقیم به جستجوی لینک‌ها می‌رویم...")

# جستجو و ذخیره لینک‌ها
dorks = ["site:t.me/", "site:t.me/joinchat"]
all_links = set()
for dork in dorks:
    print(f"در حال جستجو با: {dork}")
    links = scraper.search(dork, max_pages=1000)
    all_links.update(links)

browser_manager.quit()
print(f"✅ استخراج {len(all_links)} لینک گروه تلگرام کامل شد!")
