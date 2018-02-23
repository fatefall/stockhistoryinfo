import requests
from bs4 import BeautifulSoup
import json
import numpy as np
import os,datetime
# mongoDB 接口
import pymongo

# client = pymongo.MongoClient('localhost', 27017)
client = pymongo.MongoClient("mongodb://localhost:27017/")

# 测试现有数据库
db = client.Stock
collection = db.GrowFINdata

# 建立unique index
#collection.create_index("Stockcode", name="Stockcode", unique=True)

# 输入6位数字的股票代码，
# 返回html and JSON data

###取得股票财务数据
def getStockData(Sn: "String,股票代码"):
    # url = 'http://stockpage.10jqka.com.cn/'+Sn+'/finance/'
    url = 'http://basic.10jqka.com.cn/' + Sn + '/finance.html#stockpage'
    print(url)
    hasdata = False
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    # print(soup)
    stockData = js_format(soup)
    # print(stockData)

    if stockData == None:
        return (False, None)
    else:
        return (True, stockData)


def epsData(Sn, rawdata: "JSON list"):
    _title = rawdata["title"]  # 栏目名称
    _title[0] = ["季度", '季度']
    _simple = rawdata["simple"]  # 季度

    # listOfParm = ["季度","基本每股收益","净利润同比增长率","营业总收入同比增长率","销售毛利率"]
    listOfParm = ["季度", "基本每股收益"]

    qtlist = _simple[0]

    eps = _simple[1]

    temp = {}
    for i in range(len(qtlist)):
        tempstr = qtlist[i].replace('-', '')[0:6]
        if eps[i] is False:
            temp[tempstr] = eps[i - 1]
        else:
            temp[tempstr] = eps[i]


    # print(temp)
    epsdata = {}
    epsdata["DISPDATE"] = str(datetime.date.today())
    epsdata["epsData"] = temp
    return epsdata


# 营业总收入同比增长率'
#    yysr_100 = _simple[6][0:ll]
# 净利润同比增长率
#    np_100 = _simple[3][0:ll]
#


def js_format(soup):
    # get data
    div = soup.select('#main')
    for ct in div:
        js = json.loads(ct.text)
        return js


def getFinData(Sn, Info: "财务数据类型"):
    hasdata, rawdata = getStockData(Sn)

    if Info == 'eps':
        return (hasdata, epsData(Sn, rawdata))
    else:
        return (hasdata, None)


###########################################
Sn = "000858"
hasdata, epsdata = getFinData(Sn,'eps')

temp_d ={"stockcode":Sn}

data =dict(temp_d, **epsdata)

if hasdata:
    tempexist = collection.find_one(temp_d)
    #print(tempexist)
    #UpdateORAdd
    if tempexist == None:
        #Add
        collection.insert_one(data)
    else:
        #Update
        collection.replace_one(tempexist,data)