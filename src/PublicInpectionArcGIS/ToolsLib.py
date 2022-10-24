# -*- coding: utf-8 -*-

from PublicInpectionArcGIS.Utils import ToolboxLogger
from PublicInpectionArcGIS.Utils import ARCGIS_HANDLER, STREAM_HANDLER
from PublicInpectionArcGIS.SetupDataSources import SetupDataSourcesTool

class PublicInspectionTools :

    @staticmethod 
    def PublicInspectionTool1(param0 = None):
        ToolboxLogger.info(param0)

    @staticmethod 
    def PublicInspectionTool2(param0 = None):
        ToolboxLogger.info(param0)

    @staticmethod
    def SetupDataSource(loadDataSourcePath = None, aprx = None) :
        if loadDataSourcePath != None :
            tool = SetupDataSourcesTool(loadDataSourcePath, aprx)
            tool.execute()
