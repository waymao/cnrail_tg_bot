# query12306.py
# looks for timetable on 12306.
# Modified by waymao from lfz's version

import requests
import json
import datetime

import bot_config

header = bot_config.header
ua = {'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 11_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.0 Mobile/15E148 Safari/604.1'}

def getTrainList(queryDate,from_station,to_station,purpose_codes="ADULT") -> list:
    response  = requests.get("https://kyfw.12306.cn/kfzmpt/lcxxcx/query?"\
        "purpose_codes=%s&queryDate=%s&from_station=%s&to_station=%s"%(purpose_codes,queryDate,from_station,to_station), headers=header)
    text = response.content.decode('utf-8')
    rawData=text[text.find("{\"train")-1:text.find("],")+1]
    data={}
    try:
        data = json.loads(rawData)
    except:
        return {}
    return data

def getTimeList(train_no,train_date)-> list:
    response  = requests.get("https://kyfw.12306.cn/kfzmpt/queryTrainInfo/query?leftTicketDTO.train_no=%s&leftTicketDTO.train_date=%s&rand_code="%(train_no,train_date), headers=header)
    text = response.content.decode('utf-8')
    rawData=text[text.find("{\"arriv")-1:text.find("},\"messages")]
    data = json.loads(rawData)
    return(data)

def getTicketCheck(trainDate,station_train_code,from_station_telecode) -> str:
    response  = requests.get("https://www.12306.cn/index/otn/index12306/queryTicketCheck?trainDate=%s&station_train_code=%s&from_station_telecode=%s"%(trainDate,station_train_code,from_station_telecode),headers=header)
    text = response.content.decode('utf-8')
    data = json.loads(text)
    return(data["data"])

def station_encode(s: str) -> str:
    return '-' + '-'.join(
        '%02x' % byte
        for byte in s.encode('utf-8')
    )

def get_status(train, station, kind) -> requests.Response:
    url = 'http://dynamic.12306.cn/map_zwdcx/cx.jsp'
    url = 'https://www.12306.cn/mapping/kfxt/zwdcx/LCZWD/cx.jsp'
    params = {
        'cz': station,
        'cc': train,
        'cxlx': int(kind),
        'rq': datetime.date.today().isoformat(),
        'czEn': station_encode(station),
    }
    ua = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.3 Safari/605.1.15'}
    return requests.get(url, params, headers=header)

def print_status(response: requests.Response):
    if response.status_code == 200:
        print('|', response.text.strip())
    else:
        print('X %d error' % response.status_code)

if __name__ == '__main__':
    '''
    print(getTicketCheck("2019-06-21","G85","AOH"))
    print()
    data = getTrainList("2019-06-10","LZJ","XNO")
    for i in data:
        print(i)#['station_train_code'])
    print()
    '''

    date = "2019-07-14"
    train="G1603"
    traindata = getTimeList(train,date)
    print(traindata[0]["train_class_name"]+" "+traindata[0]['station_train_code']+"\t"+""+date+" "+traindata[-1]["arrive_day_str"])

    for i in traindata:
        print(i["station_name"].ljust(10)+" \t"+i["arrive_time"]+" \t"+i["start_time"],end="\n")
        #print_status(get_status(train,i["station_name"],1))
