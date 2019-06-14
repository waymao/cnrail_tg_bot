# TrainNoDB.py
# Retrieves the trainNO and indexes it.
# Contains a implementation of TrainNoDB class.

import json
import logging
import requests
from datetime import datetime

class TrainNoDB:
    # Update the trainlist
    def update(self):
        response  = requests.get("https://kyfw.12306.cn/otn/resources/js/query/train_list.js",headers=header)
        result = response.content.decode('utf-8')
        real_json = result[16:]
        self.db = json.loads(real_json)
        logging.info('TrainInfo Updated')
        self.make_index()
    
    # Make an index (for search) from the train list.
    def make_index(self):
        self.train_index = {}
        self.train_no = []
        for t_type in self.db[datetime.now(tz).strftime("%Y-%m-%d")]:
            for train in self.db[datetime.now(tz).strftime("%Y-%m-%d")][t_type]:
                train_search = re.search(r'([A-Z]?\d+)', train['station_train_code'])
                # if found
                if train_search:
                    trainno = train_search.group(1)
                    self.train_no.append(trainno)

                    # After user have entered >=2 answers, we will show hints.
                    for i in range(2, len(trainno) + 1):
                        substr = trainno[0:i]
                        if substr in self.train_index.keys():
                            self.train_index[substr].append(trainno)
                        else:
                            self.train_index[substr] = [trainno]
        logging.info('TrainIndex Updated')
    
    def __init__(self):
        # self.update()
        pass
