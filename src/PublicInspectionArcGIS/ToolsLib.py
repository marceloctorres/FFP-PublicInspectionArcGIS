# -*- coding: utf-8 -*-
import os
from PublicInspectionArcGIS.Utils import ToolboxLogger, ARCGIS_HANDLER, STREAM_HANDLER, Configuration
from PublicInspectionArcGIS.SetupDataSources import SetupDataSourcesTool
from PublicInspectionArcGIS.CalculateBoundaries import CalculateBoundariesTool
from PublicInspectionArcGIS.CaptureSignature import CaptureSignaturesTool

class PublicInspectionTools :

    def getConfiguration() :
        CONFIG_PATH = "config.json"
        folder_path = os.path.dirname(os.path.realpath(__file__))
        config_path = os.path.join(folder_path, CONFIG_PATH)

        return Configuration(config_path)

    @staticmethod 
    def PublicInspectionTool1(param0=None):
        ToolboxLogger.info(param0)

    @staticmethod 
    def PublicInspectionTool2(param0=None):
        ToolboxLogger.info(param0)

    @staticmethod
    def SetupDataSource(loadDataSourcePath=None, aprx=None) :
        if loadDataSourcePath != None and aprx != None:
            configuration = PublicInspectionTools.getConfiguration()
            tool = SetupDataSourcesTool(configuration=configuration, aprx=aprx, loadDataSourcePath=loadDataSourcePath)
            tool.execute()

    @staticmethod
    def CalculateBoundaries(aprx=None) :
        if aprx != None :
            configuration = PublicInspectionTools.getConfiguration()
            tool = CalculateBoundariesTool(configuration=configuration, aprx=aprx)
            tool.execute()

    @staticmethod
    def CaptureSignatures(aprx=None, legal_id=None) :
        if aprx != None :
            configuration = PublicInspectionTools.getConfiguration()
            tool = CaptureSignaturesTool(configuration=configuration, aprx=aprx, legal_id=legal_id)
            tool.execute()
    
