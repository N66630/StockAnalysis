# -*- coding: utf-8 -*-
"""
Created on Thu Apr 26 23:01:38 2018

@author: Administrator
"""

"""
Common Variable Definition
"""
import os


""" 一般類別名稱會是大寫開頭的字母 """
class CommVar:
    """
    變數與函數的底線規則
    以單底線開頭的變數或函數為 private 變數, 別的 module (*.py) 不能取用 (不該取用, 一般 import 時不會載入, 但可以強制取用)
    以雙底線開頭的變數或函數為全域靜態變, 但需要全名 (前面要加 obj.calssname__xxxxx) 取用, 且只會取到 init 時的值, 如有變更也取不到
    以單底線結尾的表示未了避免與 python keyword 衝突
    以雙底線開頭且雙底線結尾的是特殊的函數, 不要用 (ex: __main__, __init__)
    """
    _APInfoPath = r"D:\APInfo"
    _RootConfigPath = r"D:\APInfo\APC.AP\Config" # + "\\"
    _MaxLogFileSize = 4 *1024 * 1024 #MB
    __APInfoPath = r"D:\APInfo"

    """
    initial 初始化
    """
    def __init__(self):
        #pass
        if not os.path.exists(self.__APInfoPath):
            #print ('@@@ The directory is not existed of APInforPath')
            #print ('@@@ '+self.__APInfoPath)
            self.__APInfoPath = self._APInfoPath = self.__APInfoPath.replace(r"C:", r"D:")
            #print ('@@@ '+self.__APInfoPath)
            self._RootConfigPath = self._RootConfigPath.replace(r"C:", r"D:")


    """
    類的方法共有三種:
    第一種 - 一般普通
        a. 此種方式通過 def 定義, 需要至少傳遞一個參數(一般用 self, 也就是第一個參數要是 self)
        b. 要通過實例(instance) 調用此種方法
        c. 第一個參數為 self, 表示一個具體實例的本身
        呼叫方法 1: 宣告實例,再行呼叫
            c = comVar()
            c.xxxx()
        呼叫方法 2: 類別直接呼叫並代入 instance
            comVar.xxx(c)
    """
    def get_APInfoPath_Obj(self):
        return self._APInfoPath
    def set_APInfoPath_Obj(self, apinfopath):
        self._APInfoPath = apinfopath

    """
    類的方法共有三種:
    第二種 - 類方法
        a. 在 def 前面加上 @classmethod,但也需要至少傳遞一個參數(一般用 cls 表示 class)
        b. 可以通過類名直接調用或通過 instance 調用此種方法
        c. 可以通過cls訪問類變量，但不能訪問實例變量
        呼叫方法 1: 宣告實例,再行呼叫
            c = comVar()
            c.get_APInfoPath()
        呼叫方法 2: 類別直接呼叫
            comVar.get_APInfoPath()
    """
    @classmethod
    def get_APInfoPath_Cls(cls):
        return cls._APInfoPath
    @classmethod
    def get_APInfoPath_Cls_(cls):
        return cls.__APInfoPath
    @classmethod
    def set_APInfoPath_Cls(cls, apinfopath):
        cls.__APInfoPath = apinfopath
    @classmethod
    def get_RootConfigPath_Cls(cls):
        return cls._RootConfigPath
    @classmethod
    def set_RootConfigPath_Cls(cls, configpath):
        cls._RootConfigPath = configpath

    """
    類的方法共有三種:
    第三種 - 靜態的類方法
        a. 在 def 前面加上 @staticmethod, 它的特點就是參數可以為空
        b. 可以通過類名直接調用或通過 instance 調用此種方法
        c. 要取得 class 中的變數要用 class 名稱 (CommVar._MaxLogFileSize)
        呼叫方法 1: 宣告實例,再行呼叫
            c = comVar()
            c.get_MaxLogFileSize()
        呼叫方法 2: 類別直接呼叫
            CommVar.get_MaxLogFileSize()
    """
    @staticmethod
    def get_MaxLogFileSize():
        return CommVar._MaxLogFileSize
    @staticmethod
    def set_MaxLogFileSize(size):
        CommVar._MaxLogFileSize = size

    @staticmethod
    def get_ConfigPath_APCMain():
        return CommVar._RootConfigPath + '\\' + 'APCMain.Configuration'
    @staticmethod
    def get_ConfigPath_DBConnection():
        return CommVar._RootConfigPath + '\\' + 'DBConnection.Configuration'
