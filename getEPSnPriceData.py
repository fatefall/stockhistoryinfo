# merge with getprice
# 2017Nov19：给DB名为priceMdata
import requests, urllib
from bs4 import BeautifulSoup
import json
import numpy as np
import os, datetime
# mongoDB 接口
import pymongo

###请确保MONGOD开启
# client = pymongo.MongoClient('localhost', 27017)
client = pymongo.MongoClient("mongodb://localhost:27017/")
# print(client)

# 测试现有数据库
db = client.Stock
pricecollection = db.priceMdata
# 测试现有数据库
db = client.Stock
EPScollection = db.EPSdata

# 建立unique index
pricecollection.create_index("stockcode", name="stockcode", unique=True)

EPScollection.create_index("stockcode", name="stockcode", unique=True)
#############################

###getprice
# 输入6位数字的股票代码，
def parseHTML(html):
    res = BeautifulSoup(html, 'html.parser')
    return (res)


###取得股票价格数据
def getStockPriceData(Sn: "String,股票代码"):
    stockdatatype = '20'
    # nn:20 - 月K（不复权），21 - 月K（前复权）
    # 表示股票类型: 0 日k ，1 周k，2 月k；'stockType':'0',
    # 表示复权: 0 不复权，1前复权，2后复权 'rehabilitationType':'1',
    # url = 'http://d.10jqka.com.cn/v2/line/hs_' + Sn + '/' + stockdatatype + '/last.js'
    # url ='http://d.10jqka.com.cn/v2/realhead/hs_' + Sn + '/last.js'
    # url = 'http://stockpage.10jqka.com.cn/' + Sn + '/'

    # url = 'http://img1.money.126.net/data/hs/kline/month/times/0600519.json'
    # url = 'http://img1.money.126.net/data/hs/kline/month/times/1002508.json'
    # url = 'http://img1.money.126.net/data/hs/kline/month/times/1300011.json'

    if Sn[0] == '6':
        url = 'http://img1.money.126.net/data/hs/kline/month/times/0' + Sn + '.json'
    else:
        url = 'http://img1.money.126.net/data/hs/kline/month/times/1' + Sn + '.json'

    # 返回404的
    # url = 'http://img1.money.126.net/data/hs/kline/month/times/1390011.json'
    # print(url)
    rt = requests.get(url).text
    soup = parseHTML(rt)
    # print('soup:'+ rt)

    title = soup.select('title')
    # print(title)
    # 截取数据为字典格式
    if title == []:
        datadic = eval(rt)
    else:
        for i in title:
            print(i.text)
            if i.text == '404 Not Found':
                return (False, "404，股票代码错误！")
            else:
                return (False, "其它错误，股票代码错误！")

    # print(type(datadic))

    # for k in datadic:
    #    print("key" + k)
    #    print(datadic[k])

    stockdata = {}
    stockinfo = {}

    stockinfo['stockcode'] = datadic['symbol']
    stockinfo['start'] = datadic['times'][0]
    stockinfo['name'] = datadic['name']
    stockinfo['DISPDATE'] = str(datetime.date.today())
    print(stockinfo)

    plist = datadic['closes']
    mlist = datadic['times']
    # print(mlist)

    for i in range(len(plist)):
        stockdata[mlist[i][0:6]] = plist[i]
        # print(stockdata)

    stockinfo['data'] = stockdata

    return (True, stockinfo)


def getPrice(Sn):
    #Sn = "002508"
    # Sn = "000858"
    hasdata = False

    ParmNumOfDays = 29

    temp_d = {"stockcode": Sn}
    tempexist = pricecollection.find_one(temp_d)

    # UpdateORAdd
    if tempexist == None:
        # Add
        hasdata, data = getStockPriceData(Sn)
        # print(data)
        if hasdata:
            pricecollection.insert_one(data)
    else:
        hasdata = True
        #  Update
        try:
            disp_date = datetime.date(int(tempexist['DISPDATE'][0:4]), int(tempexist['DISPDATE'][5:7]),
                                      int(tempexist['DISPDATE'][8:10]))
            current_date = datetime.date.today()

            if (current_date - disp_date).days > ParmNumOfDays:
                hasdata, data = getStockPriceData(Sn)
                # print(data)
                if hasdata:
                    pricecollection.replace_one(tempexist, data)
        except KeyError:
            hasdata, data = getStockPriceData(Sn)
            # print(data)
            if hasdata:
                pricecollection.replace_one(tempexist, data)


    return hasdata



#Merge with getEPS.py
#2017Nov19:改DB名为EPSdata。
import requests
from bs4 import BeautifulSoup
import json
import numpy as np
import os,datetime




# 输入6位数字的股票代码，
# 返回html and JSON data

###取得EPS数据
def js_format(soup):
    # get data
    div = soup.select('#main')
    for ct in div:
        js = json.loads(ct.text)
        return js

def getEPSData(Sn):
    # url = 'http://stockpage.10jqka.com.cn/'+Sn+'/finance/'
    url = 'http://basic.10jqka.com.cn/' + Sn + '/finance.html#stockpage'
    print(url)
    headers ={
        "User-Agent":"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0"
    }
    r = requests.get(url,headers=headers)

    hasdata = False

    soup = BeautifulSoup(r.text, 'html.parser')
    # print(soup)
    stockData = js_format(soup)

    if stockData == None:
        return (False, None)
    else:
        _title = stockData["title"]  # 栏目名称
        _title[0] = ["季度", '季度']
        _simple = stockData["simple"]  # 季度

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
        epsdata['stockcode'] = Sn
        epsdata["DISPDATE"] = str(datetime.date.today())
        epsdata["epsData"] = temp
        return True, epsdata


def getEPS(Sn):
    #Sn = "002508"
    #Sn = "000858"
    ParmNumOfDays = 29
    hasdata = False

    temp_d = {"stockcode": Sn}
    tempexist = EPScollection.find_one(temp_d)
    print("getEPS")
    print(tempexist)
    # UpdateORAdd
    if tempexist == None:
        # Add
        hasdata, data = getEPSData(Sn)
        print(data)
        if hasdata:
            EPScollection.insert_one(data)
    else:
        hasdata = True
        # Update

        try:
            disp_date = datetime.date(int(tempexist['DISPDATE'][0:4]),int(tempexist['DISPDATE'][5:7]),int(tempexist['DISPDATE'][8:10]))
            current_date = datetime.date.today()

            if (current_date - disp_date).days > ParmNumOfDays:
                hasdata, data = getEPSData(Sn)
                # print(data)
                if hasdata:
                    EPScollection.replace_one(tempexist, data)
        except KeyError:
            hasdata, data = getEPSData(Sn)
            # print(data)
            if hasdata:
                EPScollection.replace_one(tempexist, data)

    return hasdata