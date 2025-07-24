import os
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier

class TelegramPredictor:
    def __init__(self, model_path="telegram_model.pkl", vectorizer_path="vectorizer.pkl"):
        self.model_path = model_path
        self.vectorizer_path = vectorizer_path
        self.model = None
        self.vectorizer = None
        self.load_or_train()

    def train(self, urls, labels):
        self.vectorizer = TfidfVectorizer(analyzer="char", ngram_range=(2, 5))
        X_train_vec = self.vectorizer.fit_transform(urls)
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_train_vec, labels)
        with open(self.model_path, "wb") as f:
            pickle.dump(self.model, f)
        with open(self.vectorizer_path, "wb") as f:
            pickle.dump(self.vectorizer, f)
        print("مدل آموزش داده شد و ذخیره شد.")

    def load_or_train(self):
        if os.path.exists(self.model_path) and os.path.exists(self.vectorizer_path):
            with open(self.model_path, "rb") as f:
                self.model = pickle.load(f)
            with open(self.vectorizer_path, "rb") as f:
                self.vectorizer = pickle.load(f)
            print("مدل و vectorizer بارگذاری شدند.")
        else:
            training_data = [
                ("https://t.me/sokneoi3", 1),
                ("https://t.me/google_play_redeem_code_free_1", 1),
                ("https://t.me/RVvoenkor", 1),
                ("https://t.me/group123", 1),
                ("https://www.google.com/search?q=test", 0),
                ("https://accounts.google.com/ServiceLogin", 0),
                ("https://example.com", 0),
                ("https://www.youtube.com/watch?v=abc", 0),
                ("https://www.google.com/search?q=test", 0),
                ("https://accounts.google.com/ServiceLogin", 0),
                ("https://example.com", 0),
                ("https://www.youtube.com/watch?v=abc", 0)
            ]
            urls = [url for url, label in training_data]
            labels = [label for url, label in training_data]
            self.train(urls, labels)

    def predict(self, url):
        url_vec = self.vectorizer.transform([url])
        prediction = self.model.predict(url_vec)[0]
        probability = self.model.predict_proba(url_vec)[0][1]
        return prediction == 1 and probability > 0.8