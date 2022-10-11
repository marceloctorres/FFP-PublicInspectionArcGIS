# -*- coding: utf-8 -*-

import arcpy

from PublicInpectionArcGIS.Utils import ARCGIS_HANDLER, STREAM_HANDLER
from PublicInpectionArcGIS.ToolsLib import PublicInspectionTools

class Toolbox(object):
    
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "FFP Public Inspection ArcGIS Tools"
        self.alias = "PublicInspectionArcGISToolbox"
        
        # List of tool classes associated with this toolbox
        self.tools = [PublicInspectionArcGISTool1,
                      PublicInspectionArcGISTool2]

class PublicInspectionArcGISTool1(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "FFP Public Inspection Tool 1"
        self.description = "FFP Public Inspection Tool 1"
        self.alias = "PublicInspectionArcGISTool1"
        
        self.canRunInBackground = True
        self.Params = {"param0": 0}

    def getParameterInfo(self):
        """Define parameter definitions"""
        params = []

        param = arcpy.Parameter(
            displayName="Parameter 0",
            name="param0",
            datatype="GPString",
            parameterType="Required",
            direction="Input",
        )
        params.insert(self.Params["param0"], param)

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        param0 = parameters[self.Params["param0"]].valueAsText
        PublicInspectionTools.PublicInspectionTool1(param0=param0)

        return

class PublicInspectionArcGISTool2(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "FFP Public Inspection Tool 2"
        self.description = "FFP Public Inspection Tool 2"
        self.alias = "PublicInspectionArcGISTool1"
        
        self.canRunInBackground = True
        self.Params = {"param0": 0}

    def getParameterInfo(self):
        """Define parameter definitions"""
        params = []

        param = arcpy.Parameter(
            displayName="Parameter 0",
            name="param0",
            datatype="GPString",
            parameterType="Required",
            direction="Input",
        )
        params.insert(self.Params["param0"], param)

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        param0 = parameters[self.Params["param0"]].valueAsText
        PublicInspectionTools.PublicInspectionTool2(param0=param0)

        PublicInspectionTools.PublicInspectionTool1(
    param0="Parameter 0 Tool 1"
)

        return

