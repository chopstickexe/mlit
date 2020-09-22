import csv
from datetime import datetime

class Parser:
    def __init__(self, csv_path: str):
        self.csv_path = csv_path

    def __enter__(self):
        self.file = open(self.csv_path, newline='', encoding="UTf-8")
        self.reader = csv.DictReader(self.file)
        return self

    def __exit__(self, ex_type, ex_value, traceback):
        if self.file:
            self.file.close()

    def __iter__(self):
        return self

    def __next__(self):
        return self.reader.__next__()
