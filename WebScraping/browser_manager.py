import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By  # اضافه شده برای استفاده از By.ID
from selenium.common.exceptions import TimeoutException

class BrowserManager:
    def __init__(self):
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
        ]
        options = webdriver.ChromeOptions()
        options.add_argument("--proxy-server=socks5://127.0.0.1:9150")
        options.add_argument(f'user-agent={random.choice(self.user_agents)}')
        service = Service(ChromeDriverManager().install())
        self.browser = webdriver.Chrome(service=service, options=options)

    def check_for_captcha(self):
        try:
            WebDriverWait(self.browser, 5).until(EC.presence_of_element_located((By.ID, "recaptcha")))
            print("CAPTCHA شناسایی شد! لطفاً آن را حل کنید و Enter را فشار دهید.")
            input("پس از حل CAPTCHA، Enter را فشار دهید...")
            return True
        except TimeoutException:
            return False

    def quit(self):
        self.browser.quit()