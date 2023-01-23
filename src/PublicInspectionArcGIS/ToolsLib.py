# -*- coding: utf-8 -*-
import os
from PublicInspectionArcGIS.Utils import Configuration
from PublicInspectionArcGIS.SetupDataSources import SetupDataSources
from PublicInspectionArcGIS.CalculateBoundaries import CalculateBoundaries
from PublicInspectionArcGIS.CaptureSignature import CaptureSignatures
from PublicInspectionArcGIS.CalculateCertificate import CalculateCertificate
from PublicInspectionArcGIS.CalculateDashboard import CalculateDashboard

class PublicInspectionTools :

    def getConfiguration() :
        CONFIG_PATH = "config.json"
        folder_path = os.path.dirname(os.path.realpath(__file__))
        config_path = os.path.join(folder_path, CONFIG_PATH)

        return Configuration(config_path)

    @staticmethod
    def SetupDataSource(loadDataSourcePath=None, aprx=None) :
        if loadDataSourcePath != None and aprx != None:
            configuration = PublicInspectionTools.getConfiguration()
            tool = SetupDataSources(configuration=configuration, aprx=aprx, loadDataSourcePath=loadDataSourcePath)
            tool.execute()

    @staticmethod
    def getSetupDataSource(aprx=None) :
        if aprx != None :   
            configuration = PublicInspectionTools.getConfiguration()
            tool = SetupDataSources(configuration=configuration, aprx=aprx)
            return tool
        else :
            return None

    @staticmethod
    def CalculateBoundaries(aprx=None, legal_id=None) :
        if aprx != None :
            configuration = PublicInspectionTools.getConfiguration()
            tool = CalculateBoundaries(configuration=configuration, aprx=aprx)
            tool.legal_id = legal_id
            tool.execute()

    @staticmethod
    def getCalculateBoundaries(aprx=None) :
        if aprx != None :   
            configuration = PublicInspectionTools.getConfiguration()
            tool = CalculateBoundaries(configuration=configuration, aprx=aprx)
            return tool
        else :
            return None            

    @staticmethod
    def CaptureSignatures(aprx=None, legal_id=None) :
        if aprx != None :
            configuration = PublicInspectionTools.getConfiguration()
            tool = CaptureSignatures(configuration=configuration, aprx=aprx, legal_id=legal_id)
            tool.execute()
    
    @staticmethod
    def getCaptureSignature(aprx=None) :
        if aprx != None :   
            configuration = PublicInspectionTools.getConfiguration()
            tool = CaptureSignatures(configuration=configuration, aprx=aprx)
            return tool
        else :
            return None
    
    @staticmethod
    def getCalculateCertificate(aprx=None ):
        if aprx != None :   
            configuration = PublicInspectionTools.getConfiguration()
            tool = CalculateCertificate(configuration=configuration, aprx=aprx, legal_id=None)
            return tool
        else :
            return None
        
    @staticmethod
    def CalculateCertificate(aprx=None,legal_id=None) :
        if aprx != None :   
            configuration = PublicInspectionTools.getConfiguration()
            tool = CalculateCertificate(configuration=configuration, aprx=aprx, legal_id=legal_id)
            tool.execute()   

    @staticmethod
    def getCalculateDashboard(aprx=None ):
        if aprx != None :   
            configuration = PublicInspectionTools.getConfiguration()
            tool = CalculateDashboard(configuration=configuration, aprx=aprx, legal_id=None)
            return tool
        else :
            return None
        
    @staticmethod
    def CalculateDashboard(aprx=None,legal_id=None) :
        if aprx != None :   
            configuration = PublicInspectionTools.getConfiguration()
            tool = CalculateDashboard(configuration=configuration, aprx=aprx, legal_id=legal_id)
            tool.execute()   