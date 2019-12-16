# -*- coding: utf-8 -*-
"""
Created on Thu Apr 26 22:51:13 2018

@author: Administrator
"""

import os

class hyFile:
    """
    檢查檔案是否存在,可以順便刪除該檔案
    回傳: True / False
    """
    def CheckFileExists(self, filename, NeedDelete=False):
        if NeedDelete == True:
            if os.path.exists(filename):
                os.remove(filename)
        if os.path.exists(filename):
            return True
        else:
            return False