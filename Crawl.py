import os
import requests
import pandas as pd
from io import StringIO
from bs4 import BeautifulSoup

"""
參數傳送:單引號/雙引號的使用
            In function *construction*      In function *call*
=======================================================================
          |  def f(*args):                 |  def f(a, b):
*args     |      for arg in args:          |      return a + b
          |          print(arg)            |  args = (1, 2)
          |  f(1, 2)                       |  f(*args)
----------|--------------------------------|---------------------------
          |  def f(a, b):                  |  def f(a, b):
**kwargs  |      return a + b              |      return a + b
          |  def g(**kwargs):              |  kwargs = dict(a=1, b=2)
          |      return f(**kwargs)        |  f(**kwargs)
          |  g(a=1, b=2)                   |
-----------------------------------------------------------------------
"""
class Crawl:

    def __init__(self, dataexportpath):
        self._DataExportPath = dataexportpath


    """ 從 http 下載檔案到 local"""
    def crawl_file_to_file(self, url, filename):
        res = requests.get(url)
        with open(os.path.join(filename), 'wb') as f:
            f.write(res.content)
    """ 從 http 讀取檔案內容到 dataframe"""
    def crawl_file_to_df(self, url):
        res = requests.get(url)
        return res.text


    """ 從檔案中讀出資料 """
    def read_file(self, filename):
        with open(os.path.join(filename),'r') as f:
            txt = f.read()
            # print (txt[:1000])
            return(txt)


    """ 下載上市公司資料 (.csv file), 不會存在 local, 而是回傳 dataframe """
    #region 這是申請中的公司 --- marked
    #def down_parse_上市公司(self, url):
    #    sFileContent = self.crawl_file_to_df(url)
    #    arFileLine =sFileContent.split('\n')
    #    arNewLine =[]
    #    for line in arFileLine:
    #        if len(line.split('",')) >= 14:
    #            arNewLine.append(line.replace('\r',''))
    #    df = pd.read_csv(StringIO("\n".join(arNewLine).replace("=","")))
    #    df = df.loc[:,["公司代號","公司簡稱","申請日期","董事長","申請時股本(仟元)"]]
    #    df = df.apply(lambda s : s.astype(str).str.replace(',','').str.strip())#數值中每千位有逗號
    #    # 將 df 證券代號變成 index (沒有設的話, 會自動加入 0,1,2,3,4 .., , 設定 index 要在篩選後)
    #    df = df.set_index("公司代號")
    #    return df;
    #endregion
    """此為 html page, 非下載 csv file"""
    def down_parse_上市公司代號(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        items = soup.select('table tr')
        allitems = []
        for row in items:
            cells = row.findAll('td')
            if len(cells) >= 7 and cells[0].text.strip() != '有價證券代號及名稱':
                tmp = cells[0].text.strip().split(("\u3000"))
                #print(tmp)
                if len(tmp) > 1 and cells[5].text.strip() == 'ESVUFR': # ESVUFR: 股票
                    代號 = tmp[0].strip()
                    名稱 = tmp[1].strip()
                    ISIN_Code = cells[1].text.strip()
                    上市日 = cells[2].text.strip()
                    市場別 = cells[3].text.strip()
                    產業別 = cells[4].text.strip()
                    rowdata = {'代號': 代號, '名稱': 名稱, 'ISIN_Code': ISIN_Code, '上市日': 上市日, '市場別': 市場別, '產業別': 產業別}
                    allitems.append(rowdata)
        df = pd.DataFrame(allitems)
        df = df.set_index('代號')
        return df


    """ 下載大盤交易資料 (.csv file), 不會存在 local, 而是回傳 dataframe """
    def down_parse_大盤(self, url):
        sFileContent = self.crawl_file_to_df(url)
        arFileLine =sFileContent.split('\n')
        arNewLine =[]
        for line in arFileLine:
            if len(line.split('",')) >= 6:
                arNewLine.append(line.replace('\r',''))
        df = pd.read_csv(StringIO("\n".join(arNewLine).replace("=","")))
        df = df.loc[:,["日期","成交股數","成交金額","成交筆數","發行量加權股價指數","漲跌點數"]]
        df = df.apply(lambda s : s.astype(str).str.replace(',','').str.strip())#數值中每千位有逗號
        # 將 df 證券代號變成 index (沒有設的話, 會自動加入 0,1,2,3,4 .., , 設定 index 要在篩選後)
        df = df.set_index("日期")
        return df

    """ 下載個股日成交 (.csv file), 不會存在 local, 而是回傳 dataframe """
    def down_parse_個股日成交(self, url):
        sFileContent = self.crawl_file_to_df(url)
        arFileLine =sFileContent.split('\n')
        arNewLine =[]
        for line in arFileLine:
            if len(line.split('",')) >= 9:
                arNewLine.append(line.replace('\r',''))
        df = pd.read_csv(StringIO("\n".join(arNewLine).replace("--","0").replace("X","0")))
        df = df.loc[:,["日期","成交股數","成交金額","開盤價","最高價","最低價","收盤價","漲跌價差","成交筆數"]]
        df = df.apply(lambda s : s.astype(str).str.replace(',','').replace('X','').str.strip())#數值中每千位有逗號
        # 將 df 證券代號變成 index (沒有設的話, 會自動加入 0,1,2,3,4 .., , 設定 index 要在篩選後)
        df = df.set_index("日期")
        return df

    """ 下載法人買賣超資料 (.csv file), 不會存在 local, 而是回傳 dataframe """
    def down_parse_法人買賣超資料(self, url):
        # 讀入從網路上下載的原始資料
        sFileContent = self.crawl_file_to_df(url)
        arFileLine =sFileContent.split('\n')
        arNewLine =[]
        for line in arFileLine:
            if len(line.split('",')) >= 19:
                arNewLine.append(line.replace('\r',''))
        df = pd.read_csv(StringIO("\n".join(arNewLine).replace("=","")))
        df = df.loc[df["證券代號"].str.len() == 4]
        df = df.loc[:,["證券代號","證券名稱","外陸資買賣超股數(不含外資自營商)","外資自營商買賣超股數","投信買賣超股數","自營商買賣超股數","自營商買賣超股數(自行買賣)","自營商買賣超股數(避險)","三大法人買賣超股數"]]
        df = df.apply(lambda s : s.str.replace(',','').str.strip()) #數值中每千位有逗號
        # 將 df 證券代號變成 index (沒有設的話, 會自動加入 0,1,2,3,4 .., , 設定 index 要在篩選後)
        df = df.set_index("證券代號")
        return df


    """ 載入與解析法人買賣超的原始資料並輸出 .csv file """
"""     def parse_法人買賣超資料(self, filename):
        # 讀入從網路上下載的原始資料
        sFileContent = self.read_file(filename)

        arFileLine =sFileContent.split('\n')
        arNewLine =[]
        for line in arFileLine:
            if len(line.split('",')) >= 19:
                arNewLine.append(line)
        df = pd.read_csv(StringIO("\n".join(arNewLine).replace("=","")))
        df = df.loc[df["證券代號"].str.len() == 6]
        df = df.loc[:,["證券代號","證券名稱","外陸資買賣超股數(不含外資自營商)","外資自營商買賣超股數","投信買賣超股數","自營商買賣超股數","自營商買賣超股數(自行買賣)","自營商買賣超股數(避險)","三大法人買賣超股數"]]
        df = df.apply(lambda s : s.str.replace(',','').str.strip()) #數值中每千位有逗號
        # 將 df 證券代號變成 index (沒有設的話, 會自動加入 0,1,2,3,4 .., , 設定 index 要在篩選後)
        df = df.set_index("證券代號")
        #df = df.apply(lambda s : pd.to_numeric(s, errors='coerce'))
        # 轉存成副檔名為 .csv
        df.to_csv(os.path.splitext(filename)[-2]+".csv", encoding="utf_8_sig")
        #df = pd.read_csv(os.path.splitext(filename)[-2]+".csv", index_col=["證券代號"])
        return df """
