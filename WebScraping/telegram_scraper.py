import time
import random
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from file_handler import FileHandler


class TelegramScraper:
    def __init__(self, browser_manager, predictor):
        self.browser_manager = browser_manager
        self.predictor = predictor
        self.output_filename = "telegram_groups.csv"

    def search(self, query, max_pages=5):
        links_seen = set()
        base_url = "https://www.google.com/search?q="

        # پرسیدن فیلتر زمانی از کاربر
        time_filter_options = {
            "d": "&tbs=qdr:d",
            "w": "&tbs=qdr:w",
            "m": "&tbs=qdr:m",
            "y": "&tbs=qdr:y",
            "a": ""
        }
        print("فیلتر زمانی را انتخاب کنید: d، w، m، y، a")
        time_filter_choice = input("فیلتر زمانی (روز/هفته/ماه/سال/همه): ").strip().lower()
        time_filter = time_filter_options.get(time_filter_choice, "")

        FileHandler.save_to_csv([], self.output_filename, ["Group Links"])

        for page in range(max_pages):
            url = f"{base_url}{query}{time_filter}&start={page * 10}"
            self.browser_manager.browser.get(url)
            print(f"صفحه {page + 1} بارگذاری شد.")
            self.browser_manager.check_for_captcha()
            time.sleep(random.uniform(2, 5))

            try:
                results = self.browser_manager.browser.find_elements(By.CSS_SELECTOR, "a")
                for result in results:
                    try:
                        href = result.get_attribute("href")
                        if not href or href in links_seen:
                            continue

                        if self.predictor.predict(href):
                            links_seen.add(href)
                            FileHandler.save_to_csv([href], self.output_filename)
                            print(f"لینک تلگرام پیش‌بینی شد: {href}")
                        else:
                            print(f"لینک رد شده: {href}")
                    except StaleElementReferenceException:
                        print("المان قدیمی شد، ادامه...")
                        continue

                try:
                    self.browser_manager.browser.find_element(By.ID, "pnnext")
                except NoSuchElementException:
                    print(f"صفحه بعدی وجود نداره. جستجو در صفحه {page + 1} متوقف شد.")
                    break
            except Exception as e:
                print(f"خطای کلی در صفحه {page + 1}: {e}")
                break

        return links_seen
