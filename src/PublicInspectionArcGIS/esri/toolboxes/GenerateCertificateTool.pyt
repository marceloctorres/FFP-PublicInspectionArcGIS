
# -*- coding: utf-8 -*-

import arcpy

from PublicInspectionArcGIS.Utils import ARCGIS_HANDLER, STREAM_HANDLER, ToolboxLogger
from PublicInspectionArcGIS.ToolsLib import PublicInspectionTools

class Toolbox(object):
    
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Generate Certificate Tool"
        self.alias = "GenerateCertificateTool"
        
        # List of tool classes associated with this toolbox
        self.tools = [GenerateCertificate]

class GenerateCertificate(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Generate Certificate"
        self.description = ""
        self.alias = "GenerateCertificateTool"
        
        self.Params = {"legal_id": 0,"visitor_contact": 1}
        self.canRunInBackground = True

        ToolboxLogger.initLogger(handler_type = STREAM_HANDLER | ARCGIS_HANDLER )
        ToolboxLogger.setInfoLevel()

        aprx = arcpy.mp.ArcGISProject("CURRENT")
        self.tool = PublicInspectionTools.getCalculateCertificate(aprx=aprx)

    def getParameterInfo(self):
        """Define parameter definitions"""
        params = []

        param = arcpy.Parameter(
            displayName="Legal ID",
            name="legal_id",
            datatype="GPString",
            parameterType="Required",
            direction="Input",
        )
        params.insert(self.Params["legal_id"], param)
        
        param = arcpy.Parameter(
            displayName="visitor contact",
            name="visitor_contact",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )
        params.insert(self.Params["visitor_contact"], param)
        return params
    
    def execute(self,parameters, messages):
        """The source code of the tool."""
        legal_id = parameters[self.Params["legal_id"]].valueAsText
        visitor_contact = parameters[self.Params["visitor_contact"]].valueAsText
        
        
        self.tool.legal_id=legal_id
        self.tool.visitor_contact=visitor_contact
        self.tool.execute() 
        
        return    