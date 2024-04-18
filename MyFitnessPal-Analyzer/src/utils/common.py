import csv
from typing import Dict, Any


def read_csv(csv_filename: str) -> csv.DictReader:
    csv_file =  open(csv_filename, 'r')
    csv_reader = csv.DictReader(csv_file)
    return csv_reader


