#The First Flask Project for historic EPS inqury
from flask import Flask,url_for,render_template
from flask import request
from pyecharts import Line
from pyecharts.constants import DEFAULT_HOST
#Own Python lib
from epsInq import eps_inq, stocklistInq
from getEPSnPriceData import getPrice, getEPS

app = Flask(__name__)


@app.route('/')
def index():
    context_d = {
        'username': 'fatefall'
    }
    return render_template('index.html',**context_d)

@app.route('/list/')
def epsDefault():
    stocklist = [{
        'stockid':600000,
        'stockname':"测试用例"
        },
        {
            'stockid': 1,
            'stockname': "测试用例"
        },
        {
            'stockid': 300001,
            'stockname': "测试用例"
        }
       ]

    stocklist = stocklistInq()
    #print(stockname)
    return render_template('/stocklist.html',stocklist=stocklist)

@app.route('/eps/')
def eps():
#    print(request.method)
#    print(request.args)
    if request.method == 'GET':
#        print(request.args.to_dict())
        stockid = request.args.get('stockid')
        if len(stockid) != 6:
            return "股票代码必须为6位数字！"
        else:
            #return "股票代码是：%s" % stockid
            #print(stockid)
            # 此处应该查询并生成render页面
            stockname, attr, eps, price = eps_inq(stockid)

            if stockname == 'NOT FOUND' or stockname == 'Key Not Found in FIN Table!':
                if getPrice(stockid) & getEPS(stockid):
                    #return "可以重新查询" + stockname
                    #reTry
                    print("Retry")
                    stockname, attr, eps, price = eps_inq(stockid)
                else:
                    return "股票代码未知或没有下载数据！" + stockname


            #print(attr)
            #print(eps)

            ###echart展示,需要连接互联网得到pyecharts的Script。（以后想办法离线试试）
            title = stockname + "（股价无复权）" + "\n"

            line = Line(title, width=1600, height=800, title_text_size=40, title_pos="center", title_top='top')
            line.add('市盈率', attr, eps, mark_line=["max", "average", "min"], xy_text_size=20, label_text_size=20,
                     is_datazoom_show=True, legend_pos="center", legend_top='bottom')

            line.add('股价', attr, price, mark_line=["max", "average", "min"], xy_text_size=20, label_text_size=20,
                     is_datazoom_show=True, legend_pos="center", legend_top='bottom')

            return render_template('pyecharts.html',stockname=stockname,
                                   myechart=line.render_embed(),
                                   host=DEFAULT_HOST,
                                   script_list=line.get_js_dependencies())

    else:
        return "股票代码为空！"

@app.route('/f/')
def my_flist():
    return "如下功能："

@app.route('/example/')
def example():
    return render_template('render.html')


if __name__ == '__main__':
    app.run(debug=True)

