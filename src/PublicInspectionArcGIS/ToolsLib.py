# -*- coding: utf-8 -*-

from PublicInspectionArcGIS.Utils import ToolboxLogger, ARCGIS_HANDLER, STREAM_HANDLER
from PublicInspectionArcGIS.SetupDataSources import SetupDataSourcesTool
from PublicInspectionArcGIS.CalculateBoundaries import CalculateBoundariesTool

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

    @staticmethod
    def CalculateBoundaries(inspectionDataSourcePath) :
        tool = CalculateBoundariesTool(inspectionDataSourcePath)
        tool.execute()
