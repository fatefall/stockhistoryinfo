import pymongo

# client = pymongo.MongoClient('localhost', 27017)
client = pymongo.MongoClient("mongodb://localhost:27017/")
# print(client)

# 测试现有数据库
db = client.Stock
fin_collection = db.EPSdata
price_collection = db.priceMdata

# 查询股票列表
def stocklistInq():
    try:
        # temp_M_price = price_collection.find()["data"]
        CS_price = price_collection.find()
    except TypeError:
        return 'NOT FOUND'

    stocklist = []

    for v in CS_price:
        stock = {}

        try:
            stock['stockid'] = v['stockcode']
            stock['stockname'] = v['name']
            stocklist.append(stock)

        except KeyError:
            print("有问题的数据" + str(v))

    # print(stocklist)
    return stocklist


# 查询单个
def eps_inq(Sn):
    temp_d = {"stockcode": Sn}
    print(temp_d)
    try:
        temp_Q_eps = fin_collection.find_one(temp_d)["epsData"]
        print(temp_Q_eps)
        temp_M_price = price_collection.find_one(temp_d)["data"]
        print(temp_M_price)
    except TypeError:
        return 'NOT FOUND', None, None, None
    except KeyError:
        return 'Key Not Found in FIN Table!', None, None, None

    stockname = price_collection.find_one(temp_d)["name"] + "(" + price_collection.find_one(temp_d)["stockcode"] + ")"


### need to enhance to monthly instead of Quarterly
    hist_q_eps = []
    hist_q = []
    hist_price = []
    Qlist = ['03', '06', '09', '12']
    Q1list = ['12','01','02']
    Q2list = ['03','04','05']
    Q3list = ['06','07','08']
    Q4list = ['09','10','11']
    lastQeps = 0
    tl = 0
    i = 0
    for mm in temp_M_price:
        #如果月份是3/6/9/12，则用当季度的EPS计算市盈率。这样会提前反应变化，因为季报一般都会晚出一个月左右。
        if mm[4:6] in Q1list:
            temp_mm = mm[0:4] + '12'
        elif mm[4:6] in Q2list:
            temp_mm = mm[0:4] + '03'
        elif mm[4:6] in Q3list:
            temp_mm = mm[0:4] + '06'
        elif mm[4:6] in Q4list:
            temp_mm = mm[0:4] + '09'

        #print(temp_mm)

        #计算每月月末的市盈率
        i = i + 1
        try:
            if float(temp_M_price[mm]) > 0 and float(temp_Q_eps[temp_mm]) > 0:
                tp = round(float(temp_M_price[mm]) / (float(temp_Q_eps[temp_mm]) * 4), 2)
                lastQeps = float(temp_Q_eps[temp_mm])
                # print(float(temp_Q_eps[temp_mm]),tp)
            else:
                tp = 0
                # print("<=0")
                # print(float(temp_Q_eps[temp_mm]),tp)

            hist_q_eps.append(tp)

        except KeyError:
            print("当月没值" + mm)
            # print(i)
            # print(len(hist_q_eps))
            if i == len(hist_q_eps) + 1:
                if float(temp_M_price[mm]) > 0 and lastQeps > 0:
                    tp = round(float(temp_M_price[mm]) / (lastQeps * 4), 2)
                else:
                    tp = 0
                hist_q_eps.append(tp)
            else:
                hist_q_eps.append(0)

        except TypeError:
            print("TypeError" + mm)
            tl = i
            hist_q_eps.append(0)

        hist_q.append(mm)
        hist_price.append(temp_M_price[mm])


    #print(hist_q)
    #print(hist_q_eps)
    # print(collection.count())
    print("-----")

    return stockname, hist_q, hist_q_eps, hist_price
