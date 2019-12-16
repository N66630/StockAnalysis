
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 27 01:07:36 2018

@author: Administrator
"""

#from hyRoot.IO.File import hyFile
#from hyRoot.Common import CommVar
from hyRoot.IO import File
from hyRoot import Common
import lxml.etree

class hyConfigBase:
    def getAPCMainConfigText(self, xpath, attribute=''):
        try:
            sAPCMain_ConfigPath = Common.CommVar.get_ConfigPath_APCMain()
            if (File.hyFile().CheckFileExists(sAPCMain_ConfigPath)):
                #mydoc = minidom.parse(Common.Path_APCMain)
                #items = mydoc.getElementsByTagName('configuration/SystemInfo')
                #print (len(items))

                #tree = ET.ElementTree(file=Common.Path_APCMain)
                #return tree.findtext('configuration//SystemInfo//FAB')

                doc = lxml.etree.parse(sAPCMain_ConfigPath)
                if (len(doc.xpath(xpath)) <= 0):
                    raise Exception ('Invalid xpath.')
                #print (type(doc.xpath(xpath)[0].items()))
                nodeAttriList = []
                #nodeAttriList.append(tuple(['InnerText',doc.xpath(xpath)[0].text]))
                #nodeAttriList.append(doc.xpath(xpath)[0].items()[0])
                nodeAttriList.append(doc.xpath(xpath)[0].text)
                if (len(doc.xpath(xpath)[0].attrib) > 0):
                    nodeAttriList.append(doc.xpath(xpath)[0].items())
                return nodeAttriList
                #return doc.xpath(xpath)[0].items()
            else:
                raise Exception ('File not exists. Please check the setting in the APCMain/Common.py file.')
        #except IOError:
        except Exception as e:
            print ('Error : [{0}]. (ConfigPath={1})'.format(str(e), sAPCMain_ConfigPath ))

    def getDBConnectionString(self, fab, dbrole):
        try:
            xpath = "//FAB[@Name='{0}']//{1}".format(fab, dbrole)
            sDBConnection_ConfigPath = Common.CommVar.get_ConfigPath_DBConnection()
            #print(hyFile.CheckFileExists(sDBConnection_ConfigPath))
            if (File.hyFile().CheckFileExists(sDBConnection_ConfigPath)):
                doc = lxml.etree.parse(sDBConnection_ConfigPath)

                if (len(doc.xpath(xpath)) <= 0):
                    raise Exception ('Invalid xpath. (check the fab and dbrole)')
                return doc.xpath(xpath)[0].text.split(',')
            else:
                raise Exception ('File not exists. Please check the setting in the APCMain/Common.py file')
        except Exception as e:
            print('Error : [{0}]. (ConfigPath={1}, xpath={2})'.format(str(e), sDBConnection_ConfigPath, xpath ))
