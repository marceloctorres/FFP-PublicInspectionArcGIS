# -*- coding: utf-8 -*-

import arcpy  

from PublicInspectionArcGIS.Utils import ARCGIS_HANDLER, STREAM_HANDLER, ToolboxLogger
from PublicInspectionArcGIS.ToolsLib import PublicInspectionTools 

class Toolbox(object):
    
    def __init__(self):     
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "FFP ArcGIS Public Inspection Tools"
        self.alias = "ArcGISPublicInspectionToolbox"
        
        # List of tool classes associated with this toolbox
        self.tools = [GenerateCertificate]
        
class GenerateCertificate(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "GenerateCertificate"
        self.description = ""
        self.alias = "GenerateCertificate"
        
        self.canRunInBackground = True
        self.Params = {"param0": 0}
        ToolboxLogger.initLogger(handler_type = STREAM_HANDLER | ARCGIS_HANDLER )
        ToolboxLogger.setInfoLevel()

    def getParameterInfo(self):
        """Define parameter definitions"""
        params = []

        param = arcpy.Parameter(
            displayName="Name spatial unit",
            name="param0",
            datatype="DEWorkspace",
            # datatype="GPString",
            parameterType="Required",
            direction="Input",
        ) 
        params.insert(self.Params["param0"], param)

        return params
      
    def execute(self, parameters, messages):
        """The source code of the tool."""

        inspectionDataPath = parameters[self.Params["param0"]].valueAsText
        # aprx = arcpy.mp.ArcGISProject("CURRENT")
        
        PublicInspectionTools.CalculateCertificate(inspectionDataPath=inspectionDataPath)
        
        return 