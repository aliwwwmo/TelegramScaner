import csv
import os

class FileHandler:
    @staticmethod
    def save_to_csv(data, filename, header=None):
        mode = "w" if header and not os.path.exists(filename) else "a"
        with open(filename, mode, newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            if mode == "w" and header:
                writer.writerow(header)
            writer.writerow(data)