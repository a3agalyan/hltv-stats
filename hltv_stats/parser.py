import json
import random
import time
import requests
from bs4 import BeautifulSoup
from loguru import logger

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
            logger.info("hltv request failed with status code: " + str(r.status_code))
            raise
        return soup