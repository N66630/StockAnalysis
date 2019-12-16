from hyRoot.MSSQL import MSSQL
from hyRoot.IO.Log import hyLog
"""
python 換行四種方法
x0 = 'abc' \
   '123'
x1 = 'abc \
123
x2 = ('abc'
   '123')
x3 = '''abc
123'''
"""
class DB:
    def __init__(self, apnm, host, user, pwd, db):
        self._APName = apnm
        self.host = host
        self.user = user
        self.pwd = pwd
        self.db = db


    """先將要處理的當天的股票與代號新增出來"""
    def create_stock_id_today(self, daystr):
        try:
            #實例化類對象，連接數據對象
            ms= MSSQL(host=self.host,user=self.user,pwd=self.pwd,db=self.db)
            sql = "insert into [dbo].[W168_Stock_DailyData] (ID, Name, Date) \
                select ID, Name, '{date}' as Date from [dbo].[W168_Company] \
                where ID not in (Select ID from [dbo].[W168_Stock_DailyData] where Date='{date}')"
            sql = sql.format(date=daystr)
            ms.ExecuteNonQuery(sql)
        except Exception as e:
            hyLog().writeLog(self._APName, logtype='Sql', funcname="Sql",text=str(e) + '\r\n' + sql)
            raise


    """儲存上市公司代號"""
    def insertData_上市公司代號(self, df):
        try:
            #實例化類對象，連接數據對象
            ms= MSSQL(host=self.host,user=self.user,pwd=self.pwd,db=self.db)
            # rowdata = {'代號': 代號, '名稱': 名稱, 'ISIN_Code': ISIN_Code, '上市日': 上市日, '市場別': 市場別, '產業別': 產業別}
            for index, row in df.iterrows():
                sql = "if exists (select top 1 ID from dbo.W168_Company where ID='{id}') \
                    update dbo.W168_Company set Name='{name}', ISIN_Code='{ISIN_Code}', 上市日='{上市日}', 市場別='{市場別}', 產業別='{產業別}', UpdateTime=getdate() where ID='{id}'  \
                else \
                    insert into dbo.W168_Company (ID, Name, ISIN_Code, 上市日, 市場別, 產業別) values ('{id}', '{name}', '{ISIN_Code}', '{上市日}', '{市場別}', '{產業別}') "
                dic = dict (id=row.name,name=row["名稱"],ISIN_Code=row["ISIN_Code"],上市日=row["上市日"],市場別=row["市場別"],產業別=row["產業別"])
                sql = sql.format(**dic) #在 function call 裡面，** 用來將一個 dictionary展開成為positional 或是keyword參數，送進給該function.
                ms.ExecuteNonQuery(sql)
        except Exception as e:
            hyLog().writeLog(self._APName, logtype='Sql', funcname="Sql",text=e + '\r\n' + sql)
            raise
    """取得上市公司代號"""
    def getData_上市公司代號(self):
        try:
            #實例化類對象，連接數據對象
            ms= MSSQL(host=self.host,user=self.user,pwd=self.pwd,db=self.db)
            sql = "select ID from dbo.W168_Company"
            data = ms.ExecuteQuery(sql)
            from operator import itemgetter
            rtn = list(map(itemgetter(0), data)) # 取得 tuple array 中的第一個元素到 list
            return rtn
        except Exception as e:
            hyLog().writeLog(self._APName, logtype='Sql', funcname="Sql",text=str(e) + '\r\n' + sql)
            raise


    """儲存大盤交易資料 (daily)"""
    def insertData_大盤(self, df):
        try:
            #實例化類對象，連接數據對象
            ms= MSSQL(host=self.host,user=self.user,pwd=self.pwd,db=self.db)
            for index, row in df.iterrows():
                sql = "if exists (select top 1 ID from dbo.W168_Market_Daily where ID='TWII' and Date='{date}') \n \
                    update dbo.W168_Market_Daily set 成交張數={成交張數},  成交金額_仟億={成交金額_仟億}, 成交筆數={成交筆數}, 指數={指數}, 漲跌點數={漲跌點數} where ID='TWII' and Date='{date}' \n \
                else \n \
                    insert into dbo.W168_Market_Daily (ID, Date, 成交張數, 成交金額_仟億, 成交筆數, 指數, 漲跌點數) values ('TWII', '{date}', {成交張數},  {成交金額_仟億}, {成交筆數}, {指數}, {漲跌點數}) "
                datestr = str(int(row.name[0:3]) + 1911) + row.name[3:] # 民國轉西元
                dic = dict (date=datestr,成交張數=int(row["成交股數"])/1000,成交金額_仟億=int(row["成交金額"])/100000000,成交筆數=row["成交筆數"],指數=row["發行量加權股價指數"],漲跌點數=row["漲跌點數"])
                sql = sql.format(**dic)#在 function call 裡面，** 用來將一個 dictionary展開成為positional 或是keyword參數，送進給該function.
                ms.ExecuteNonQuery(sql)
        except Exception as e:
            hyLog().writeLog(self._APName, logtype='Sql', funcname="Sql",text=str(e) + '\r\n' + sql)
            raise


    """儲存個股的日成交資訊"""
    def insertData_個股日成交(self, df, id, daystr):
        try:
            #實例化類對象，連接數據對象
            ms= MSSQL(host=self.host,user=self.user,pwd=self.pwd,db=self.db)
            for index, row in df.iterrows():
                try:
                    #補資料時暫時的code (因為下載的個股資料是一個月的,所以一次存完, 以後逐天下載就要 mark 掉底下的 code)
                    #以上的說明要與 DB.py 的 insertData_個股日成交() 配合
                    datestr = str(int(row.name[0:3]) + 1911) + row.name[3:] # 民國轉西元
                    # if daystr != datestr:
                    #     continue
                    hyLog().writeLog(self._APName, text="\t\t\t儲存個股日成交 [({}),({})].".format( str(id), datestr))

                    sql = "if exists (select top 1 ID from dbo.[W168_Stock_DailyData] where ID='{id}' and Date='{date}') \n \
                        update dbo.[W168_Stock_DailyData] set 成交張數={成交張數},  成交金額_佰萬={成交金額_佰萬}, 開盤價={開盤價}, 最高價={最高價}, 最低價={最低價}, \n \
                            收盤價={收盤價}, 漲跌價差={漲跌價差}, 成交筆數={成交筆數} where ID='{id}' and Date='{date}' \n \
                    else \n \
                        insert into dbo.[W168_Stock_DailyData] (ID, Date, 成交張數, 成交金額_佰萬, 開盤價, 最高價, 最低價, 收盤價, 漲跌價差, 成交筆數) \n \
                            values ('{id}', '{date}', {成交張數},  {成交金額_佰萬}, {開盤價}, {最高價}, {最低價}, {收盤價}, {漲跌價差}, {成交筆數}) "
                    dic = dict (id=id,date=datestr,成交張數=int(row["成交股數"])/1000,成交金額_佰萬=int(row["成交金額"])/1000000,
                        開盤價=row["開盤價"],最高價=row["最高價"],最低價=row["最低價"],收盤價=row["收盤價"],漲跌價差=row["漲跌價差"],成交筆數=row["成交筆數"])
                    sql = sql.format(**dic)#在 function call 裡面，** 用來將一個 dictionary展開成為positional 或是keyword參數，送進給該function.
                    ms.ExecuteNonQuery(sql)
                except Exception as e:
                    hyLog().writeLog(self._APName, logtype='Sql', funcname="Sql",text=str(e) + '\r\n' + sql)
                    raise
        except Exception as e:
            hyLog().writeLog(self._APName, logtype='Sql', funcname="Sql",text=str(e) + '\r\n' + sql)
            raise


    def insertData_法人買賣超資料(self, df, date):
        try:
            #實例化類對象，連接數據對象
            ms= MSSQL(host=self.host,user=self.user,pwd=self.pwd,db=self.db)
            for index, row in df.iterrows():
                ##"證券代號","證券名稱","外陸資買賣超股數(不含外資自營商)","外資自營商買賣超股數","投信買賣超股數","自營商買賣超股數","自營商買賣超股數(自行買賣)","自營商買賣超股數(避險)","三大法人買賣超股數"
                外 = row["外陸資買賣超股數(不含外資自營商)"] + row["外資自營商買賣超股數"]
                #sql = "if exists (select top 1 ID from dbo.W168_Stock_DailyData where Date=%(date)s and ID=%(id)s) \
                #    update dbo.W168_Stock_DailyData set 外資=%(外資)s,  投信=%(投信)s, 自營商=%(自營商)s, 三大法人=%(三大法人)s where Date=%(date)s and ID=%(id)s \
                #else \
                #    insert into dbo.W168_Stock_DailyData (Date, ID, Name, 外資, 投信, 自營商, 三大法人) values (%(date)s, %(id)s, %(name)s, %(外資)s, %(投信)s, %(自營商)s, %(三大法人)s) "
                ##dic = {}.fromkeys((date,id,name,外資, 投信, 自營商, 三大法人), (date, row["證券代號"]), row["證券名稱"], 外, row["投信買賣超股數"], row["自營商買賣超股數"], row["三大法人買賣超股數"])
                #sql = "if exists (select top 1 ID from dbo.W168_Stock_DailyData where Date=:1 and ID=:2) \
                #    update dbo.W168_Stock_DailyData set 外資=:4,  投信=:5, 自營商=:6, 三大法人=:7 where Date=:1 and ID=:2 \
                #else \
                #    insert into dbo.W168_Stock_DailyData (Date, ID, Name, 外資, 投信, 自營商, 三大法人) values (:1, :2, :3, :4, :5, :6, :7) "
                ##dic = {}.fromkeys((date,id,name,外資, 投信, 自營商, 三大法人), (date, row["證券代號"]), row["證券名稱"], 外, row["投信買賣超股數"], row["自營商買賣超股數"], row["三大法人買賣超股數"])
                #dic = (date,row.name,row["證券名稱"],外,row["投信買賣超股數"],row["自營商買賣超股數"],row["三大法人買賣超股數"])
                sql = "if exists (select top 1 ID from dbo.W168_Stock_DailyData where ID={id} and Date='{date}') \n \
                    update dbo.W168_Stock_DailyData set 外資={外資},  投信={投信}, 自營商={自營商}, 三大法人={三大法人} where ID={id} and Date='{date}'  \n \
                else \n \
                    insert into dbo.W168_Stock_DailyData (ID, Name, Date, 外資, 投信, 自營商, 三大法人) \n \
                        values ('{id}', '{name}', '{date}', {外資}, {投信}, {自營商}, {三大法人}) "
                dic = dict (date=date.strftime("%Y-%m-%d"),id=row.name,name=row["證券名稱"],外資=外,投信=row["投信買賣超股數"],自營商=row["自營商買賣超股數"],三大法人=row["三大法人買賣超股數"])
                sql = sql.format(**dic)
                ms.ExecuteNonQuery(sql)
        except Exception as e:
            hyLog().writeLog(self._APName, logtype='Sql', funcname="Sql",text=str(e) + '\r\n' + sql)
            raise