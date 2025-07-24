import time
import random
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from file_handler import FileHandler

class DataCollector:
    def __init__(self, browser_manager):
        self.browser_manager = browser_manager
        self.data_filename = "training_data.csv"

    def collect(self, query, max_pages=3):
        links_collected = set()
        base_url = "https://www.google.com/search?q="

        # پرسیدن فیلتر زمانی از کاربر
        time_filter_options = {
            "روز": "&tbs=qdr:d",
            "هفته": "&tbs=qdr:w",
            "ماه": "&tbs=qdr:m",
            "سال": "&tbs=qdr:y",
            "همه": ""
        }
        print("فیلتر زمانی را انتخاب کنید: روز، هفته، ماه، سال، همه")
        time_filter_choice = input("فیلتر زمانی (روز/هفته/ماه/سال/همه): ").strip().lower()
        time_filter = time_filter_options.get(time_filter_choice, "")

        for page in range(max_pages):
            url = f"{base_url}{query}{time_filter}&start={page * 10}"
            self.browser_manager.browser.get(url)
            print(f"صفحه {page + 1} بارگذاری شد برای جمع‌آوری داده.")
            self.browser_manager.check_for_captcha()
            time.sleep(random.uniform(2, 5))

            try:
                results = self.browser_manager.browser.find_elements(By.CSS_SELECTOR, "a")
                for result in results:
                    try:
                        href = result.get_attribute("href")
                        if href and href not in links_collected:
                            links_collected.add(href)
                            label = 1 if "t.me" in href else 0
                            FileHandler.save_to_csv([href, label], self.data_filename, ["URL", "Label"])
                            print(f"داده جمع شد: {href} -> {label}")
                    except StaleElementReferenceException:
                        print("المان قدیمی شد، ادامه می‌دهیم...")
                        continue

                try:
                    self.browser_manager.browser.find_element(By.ID, "pnnext")
                except NoSuchElementException:
                    print(f"صفحه بعدی وجود نداره. جمع‌آوری در صفحه {page + 1} متوقف شد.")
                    break
            except Exception as e:
                print(f"خطای کلی در صفحه {page + 1}: {e}")
                break