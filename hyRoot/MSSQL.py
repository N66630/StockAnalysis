#import pymssql
import pyodbc

class MSSQL:
    def __init__(self, host, user, pwd, db):
        self.host = host
        self.user = user
        self.pwd = pwd
        self.db = db

    #得到資料庫連接信息函數， 返回: conn.cursor()
    def __GetConnect(self):

        #pymssql.connect(server="xxx.xxx.xxx.xxx",user="xxx",password="xxx",database="xxx")
        #self.conn=pymssql.connect(server=self.host,user=self.user,password=self.pwd,database=self.db, port="1433")
        #self.conn = pymssql.connect(server='.',host=r'.\SQLEXPRESS',
        #               user=r'sa', password=r'123', database=r'Stock',charset='UTF-8',)
        #self.conn=pymssql.connect(server=r".\SQLEXPRESS",user=r"sa",password=r"123",database=r"Stock")
        self.conn = pyodbc.connect('DRIVER={ODBC Driver 11 for SQL Server};SERVER='+self.host+';DATABASE='+self.db+';UID='+self.user+';PWD='+self.pwd)
        #self.conn = pyodbc.connect('DRIVER={SQL Server};SERVER=.\SQLEXPRESS;DATABASE=Stock;UID=sa;PWD=123')
        cur=self.conn.cursor() #將資料庫連接信息，賦值給cur。
        if not cur:
            raise Exception ("連接資料庫失敗")
        else:
            return cur

    #執行查詢語句,返回的是一個包含tuple的list，list的元素是記錄行，tuple的元素是每行記錄的欄位
    #執行Sql語句函數，返回結果
    def ExecuteQuery(self,sql,dic={}):
        #conn=pymssql.connect(server=r".",user=r"sa",password=r"123",database=r"Stock", port="1433")
        #with self.__GetConnect() as cur: #獲得資料庫連接信息
        cur = self.__GetConnect() #獲得資料庫連接信息
        if len(dic) > 0:
            cur.execute(sql,dic) #執行Sql語句
            resList = cur.fetchall() #獲得所有的查詢結果
        else:
            cur.execute(sql) #執行Sql語句
            resList = cur.fetchall() #獲得所有的查詢結果
        #查詢完畢後必須關閉連接
        self.conn.close() #返回查詢結果
        return resList

    def ExecuteNonQuery(self,sql,dic={}):
        #with self.__GetConnect() as cur:
        cur = self.__GetConnect()
        if not dic:
            cur.execute(sql)
        else:
            cur.execute(sql,dic)
        self.conn.commit()
        self.conn.close()
