import os
import configparser
import sys
import datetime
import requests
#from hyRoot.Network.Crawl import Crawl
from Crawl import Crawl
from hyRoot.IO import Log
import pandas as pd
from io import StringIO
#import pymssql
from DB import DB
from distutils.util import strtobool
import time

_APName = ""
if __name__ == '__main__':
    # 取得 ini file path (目前file同路徑下)
    #region 取得定義
    currentPath = os.path.dirname(os.path.realpath(__file__))
    cnfPath = os.path.join(currentPath, 'Config.ini').replace("\\","/")
    #print ('我的 ini 檔名稱 : ' + cnfPath)
    #創建管理對象
    _cf = configparser.ConfigParser()
    #讀取 ini 檔
    _cf.read(cnfPath, encoding='utf-8')
    #取得所有的 session
    sessions = _cf.sections()
    print(sessions) # return list (['BasicInfo', 'ProcessConfig', 'DataConfig', 'StockAnalysis'])
    #取得某 session 下的 items
    #session_0_items = _cf.items(sessions[0])
    #session_1_items = _cf.items(sessions[1])
    #print (session_0_items)
    #print dict(session_1_items)['process_no_unitid']
    _APName = _cf["StockAnalysis"]["Name"].replace("\"","").replace("\'","")
    sDownloadFilePath = _cf["StockAnalysis"]["DataExortPath"]
    sDB_Host = _cf["StockAnalysis"]["DB_Host"]
    sDB_User = _cf["StockAnalysis"]["DB_User"]
    sDB_Pwd = _cf["StockAnalysis"]["DB_Pwd"]
    sDB_Name = _cf["StockAnalysis"]["DB_Name"]
    #endregion

    log =Log.hyLog() #第一種函數宣告, 要用 instance (或是呼叫函數時第一個引數帶入物件)

    start_date = datetime.date(2019,11,1)#.strftime("%Y%m%d")
    end_date = datetime.date.today() #.strftime("%Y%m%d")
    day = datetime.timedelta(days=1) #獲取昨天的日期
    log.writeLog(apname=_APName, text="要處理的時間 ({} ~ {})".format(start_date.strftime("%Y%m%d"), end_date.strftime("%Y%m%d")))

    # initial crawl object
    craw = Crawl(sDownloadFilePath)
    db = DB(_APName, sDB_Host, sDB_User, sDB_Pwd, sDB_Name)
    sleep_sec = 5
    lastprocmonth = 0
    while start_date <= end_date:
        try:
            # 星期六,日不處理
            if start_date.weekday() == 5 or start_date.weekday() == 6:
                start_date = start_date + day
                continue
            #暫時的 code
            procemonthdata = False
            if start_date.month != lastprocmonth:
                procemonthdata = True
                lastprocmonth = start_date.month

            daystr = start_date.strftime("%Y%m%d")
            log.writeLog(_APName,text="\tProcess Start : (Date={})".format(daystr))

            #region 0.將所有的股票代號先匯到 W168_Stock_DailyData table
            db.create_stock_id_today(daystr)

            #region 1.取得與儲存上市公司代號 (要在 Config.ini file 中設定要取才會取, 不會每天做)
            if (strtobool(_cf["StockAnalysis"]["Download上市公司代號"])):
                url_上市公司代號 = _cf["StockAnalysis"]["Url_上市公司代號"]
                # 取得與儲存上市公司代號
                try:
                    log.writeLog(_APName, text="\t\t下載與解析上市公司代號 (此為 html page).".format(""))
                    df = craw.down_parse_上市公司代號(url_上市公司代號)
                    time.sleep(sleep_sec)#避免被證交所限制存取
                    log.writeLog(_APName, text="\t\t儲存上市公司資料.".format(""))
                    db.insertData_上市公司代號(df)
                except Exception as e:
                    log.writeLog(_APName, text="[Error]~解析/儲存上市公司資料 : {}".format(str(e)))
            #endregion

            #region 2.取得與儲存大盤交易資料
            try:
                url_大盤 = _cf["StockAnalysis"]["Url_大盤"].format(daystr)
                log.writeLog(_APName, text="\t\t下載與解析大盤交易資料 ({}).".format(str(start_date)))
                df = craw.down_parse_大盤(url_大盤)
                time.sleep(sleep_sec)#避免被證交所限制存取
                log.writeLog(_APName, text="\t\t儲存大盤交易資料 ({}).".format(str(start_date)))
                db.insertData_大盤(df)
            except Exception as e:
                log.writeLog(_APName, text="[Error]~解析/儲存大盤交易資料 ({}) : {}".format( str(start_date), str(e)))
            #endregion

            #region 3.取得與儲存個股日成交
            #region 3.1 先從資料庫中取出全部的個股代號
            lst = db.getData_上市公司代號()
            #endregion
            for id in lst:
                #補資料時暫時的code (因為下載的個股資料是一個月的,所以一次存完, 以後逐天下載就要 mark 掉底下的 code)
                #以上的說明要與 DB.py 的 insertData_個股日成交() 配合
                if (procemonthdata != True or (start_date.month == 6 and id < '1454')):
                    continue
                try:
                    url_個股日成交 = _cf["StockAnalysis"]["Url_個股日成交"].format(daystr, id)
                    log.writeLog(_APName, text="\t\t\t下載與解析個股日成交 [({}),({})].".format( str(id), str(start_date)))
                    df = craw.down_parse_個股日成交(url_個股日成交)
                    time.sleep(sleep_sec)#避免被證交所限制存取
                    log.writeLog(_APName, text="\t\t\t儲存個股日成交 [({}),({})].".format( str(id), str(start_date)))
                    db.insertData_個股日成交(df,id,start_date.strftime("%Y/%m/%d"))
                except Exception as e:
                    log.writeLog(_APName, text="[Error]~解析/儲存個股日成交 [({}),({})] : {}".format( str(id), str(start_date), str(e)))
            #endregion

            #region 4.取得與儲存法人買賣超
            try:
                url_法人買賣超 = _cf["StockAnalysis"]["Url_法人買賣超"].format(daystr)#.replace('\"','') # 用變數帶入時會自動在前後加上單引而引發  No connection adapters were found for 的錯誤
                log.writeLog(_APName, text="\t\t下載與解析法人買賣超 ({}).".format(str(start_date)))
                df = craw.down_parse_法人買賣超資料(url_法人買賣超)
                time.sleep(sleep_sec) #避免被證交所限制存取
                log.writeLog(_APName, text="\t\t儲存法人買賣超 ({}).".format(str(start_date)))
                db.insertData_法人買賣超資料(df, start_date)
            except Exception as e:
                log.writeLog(_APName, text="[Error]~解析/儲存法人買賣超 ({}) : {}".format( str(start_date), str(e)))
            #endregion

            """
            #法人買賣超 url
            url_法人買賣超 = _cf["StockAnalysis"]["Url_法人買賣超"].format(daystr)#.replace('\"','') # 用變數帶入時會自動在前後加上單引而引發  No connection adapters were found for 的錯誤
            export_filename_法人買賣超 = os.path.join(sDownloadFilePath,'{}_法人買賣超.txt'.format(daystr)).replace('\\', '/').replace('\"','') # 用變數帶入時會自動在前後加上單引而引發  No connection adapters were found for 的錯誤
            log.writeLog(_APName, text="\t\t取得法人買賣超路徑為 url={}".format(url_法人買賣超))

            # 下載法人買賣超的原始資料 (未處理)
            # (帶入的 url / filepath 不可是字串 -> ini file 中要去除前後引號)
            try:
                if not os.path.exists(export_filename_法人買賣超):
                    log.writeLog(_APName, text="\t\t下載法人買賣超資料 (先存成 .txt). filename={}".format(export_filename_法人買賣超))
                    craw.crawl_file_to_file(url_法人買賣超, export_filename_法人買賣超)
            except Exception as e:
                log.writeLog(_APName, text="[Error]~下載法人買賣超資料 : {}".format(str(e)))

            # 載入與解析法人買賣超的原始資料並輸出 .csv file
            try:
                if os.path.exists(export_filename_法人買賣超):
                    log.writeLog(_APName, text="\t\t解析法人買賣超資料 (有用的資料轉為 .csv).".format(""))
                    df = craw.parse_法人買賣超資料(export_filename_法人買賣超)
                    log.writeLog(_APName, text="\t\t儲存法人買賣超資料.".format(""))
                    db.insertData_法人買賣超資料(df, start_date)
            except Exception as e:
                log.writeLog(_APName, text="[Error]~解析/儲存法人買賣超資料 : {}".format(str(e)))
            """
        except Exception as e:
            log.writeLog(_APName, logtype='Error', funcname="Error",text="[Error](__main__) : {}".format(str(e)))

        start_date = start_date + day



