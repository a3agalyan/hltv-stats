import json
import random
import time
import requests
from bs4 import BeautifulSoup


class Parser:
    @staticmethod
    def _write_to_json(data, path):
        with open(path, 'w+') as fp:
            json.dump(data, fp, indent=2)

    @staticmethod
    def _read_from_json(path):
        with open(path, 'r') as fp:
            return json.load(fp)

    @staticmethod
    def _soup_from_url(url):
        timesleep = random.uniform(0.35, 0.5)
        time.sleep(timesleep)
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        if r.status_code != 200:
            print(r.status_code, "hltv failed")
            raise
        return soup