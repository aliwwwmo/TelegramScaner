import pandas as pd
from telegram_predictor import TelegramPredictor

# خوندن داده از training_data.csv
data = pd.read_csv("training_data.csv")
urls = data["URL"]
labels = data["Label"]

# آموزش مدل
predictor = TelegramPredictor()
predictor.train(urls, labels)