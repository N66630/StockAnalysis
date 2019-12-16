# -*- coding: utf-8 -*-
"""
Created on Fri Apr 27 01:16:10 2018

@author: Administrator
"""

import threading
import os
import datetime
#import lxml.etree
from hyRoot import Common
#from Root.IO.File import hyFile

"""
寫入檔案
預計最大檔為 4MB
"""
mutex = threading.Lock()
class hyRecorder(threading.Thread):
    def  __init__( self, lock, filepath, msg):
        super(hyRecorder,  self ).__init__()
        self.lock = lock
        self.filepath = filepath
        self.msg = msg
    def run(self):
        try:
            sfilepath = self.getfilepath_invoketoolog(self.filepath)
            if mutex.acquire(1):
                if not os.path.exists(sfilepath):
                    f = open(sfilepath, 'w')
                    f.writelines('[{0}] : {1}{2}'.format("{:%Y%m%d_%H%M%S}".format(datetime.datetime.now()), self.msg, '\n'))
                    f.close()
                else:
                    f = open(sfilepath, 'a')
                    f.writelines('[{0}] : {1}{2}'.format("{:%Y%m%d_%H%M%S}".format(datetime.datetime.now()), self.msg, '\n'))
                    f.close()
                mutex.release()
        except Exception as e:
            raise Exception('Error({0}):{1}'.format(self.filepath, str(e)))
        finally:
            if mutex.acquire == True:
                mutex.release()

    def getfilepath_invoketoolog(self, filepath):
        if not os.path.exists(filepath):
            f = open(filepath,'w')
            f.close()
        if (os.path.getsize(filepath) > Common.CommVar().get_MaxLogFileSize()):
            # 'D:\APInfo\MyAP\Test\Log\MyLog', '.txt'
            splitFN = os.path.splitext(filepath)
            filename = splitFN[0].split('\\')[-1]
            #print(filename)
            if (len(filename.split('_')) == 1): # 檔名沒有序號
                #print (splitFN[0] + '_01' + splitFN[1])
                return self.getfilepath_invoketoolog(splitFN[0] + '_01' + splitFN[1])
            else:
                fileSN = filename.split('_')[-1]
                if (fileSN.isnumeric()):
                    oldSN = filename.split('_')[1]
                    return self.getfilepath_invoketoolog(filepath.replace('_' + oldSN, '_' + str("%02d" % (int(oldSN)+1))))
                else:
                    return filepath
        else:
            return filepath




class hyLog:
    """
    取得 APC 系統的 log path (底層, 包含被 getLogPath_Normal / getLogPath_Error .. 呼叫)
    """
    def getLogPath(self, apname='', funcname='', subfolder='Log', reservedays=15):
        try:
            if (funcname == ''):
                raise Exception('Missing funcname (file name)')
            if (os.path.splitext(funcname)[1][1:] == ''):
                funcname += '.txt'
            # 取得完整的路徑
            filepath = os.path.join(Common.CommVar().get_APInfoPath_Cls(), apname, subfolder,  "{:%Y%m%d}".format(datetime.date.today()) + "_" + str(reservedays), funcname)
            #print (filepath)
            return filepath
        except Exception as e:
            raise Exception('Error({0}):{1}'.format(Common.CommVar().get_APInfoPath_Cls(), str(e)))
    """
    取得 APC 系統的 normal / Error 的 log path
    1. 包含檔名. 2. 資料夾不存在時自動建立 3. 沒有副檔名時會自動設為 .txt
    """
    def getLogPath_Normal(self, apname, funcname='', subfolder='Log', reservedays=15):
        return hyLog().getLogPath(apname, funcname, subfolder, reservedays)
    def getLogPath_Error(self, apname, funcname='', subfolder='Error', reservedays=30):
        return hyLog().getLogPath(apname, funcname, subfolder, reservedays)
    def getLogPath_Sql(self, apname, funcname='', subfolder='Sql', reservedays=30):
        return hyLog().getLogPath(apname, funcname, subfolder, reservedays)

    """
    寫入 log 檔 (或 Error log)
    logtype : 1.Normal (default) 2. Error
    funcname : 個別
    path : 可以指定特定的路徑
    """
    def writeLog(self, apname, logtype='Normal', funcname='Log', text='\r\n', path=''):
        try:
            if (path==''):
                if (logtype=='Normal'):
                    path = hyLog().getLogPath_Normal(apname, funcname)
                elif (logtype=='Error'):
                    path = hyLog().getLogPath_Error(apname, funcname)
                elif (logtype=='Sql'):
                    path = hyLog().getLogPath_Sql(apname, funcname)
                else:
                    raise Exception('Invalid logtype [{0}](one of Normal / Error)'.format(logtype))
            # 資料夾不存在時建立
            dirpath = os.path.dirname(path)
            if (dirpath == ''):
                raise Exception("Invalid path : ({0})".format(path))
            if not os.path.exists(dirpath):
                os.makedirs(dirpath)
            print (text)
            hyRecorder(mutex, path, text).start()
        except Exception as e:
            raise Exception('Error({0}):{1}'.format(Common.CommVar().get_APInfoPath_Cls(), str(e)))
