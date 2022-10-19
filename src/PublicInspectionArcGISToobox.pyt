# -*- coding: utf-8 -*-

import arcpy

from PublicInpectionArcGIS.Utils import ARCGIS_HANDLER, STREAM_HANDLER
from PublicInpectionArcGIS.ToolsLib import PublicInspectionTools

class Toolbox(object):
    
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "FFP ArcGIS Public Inspection Tools"
        self.alias = "ArcGISPublicInspectionToolbox"
        
        # List of tool classes associated with this toolbox
        self.tools = [SetupDataSourcesTool]

class SetupDataSourcesTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Setup Datasources"
        self.description = "Create FGDBs to make Public Inspection"
        self.alias = "SetupDataSourcesTool"
        
        self.canRunInBackground = True
        self.Params = {"param0": 0}

    def getParameterInfo(self):
        """Define parameter definitions"""
        params = []

        param = arcpy.Parameter(
            displayName="Input FGDB",
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

        loadDataSourcePath = parameters[self.Params["param0"]].valueAsText
        aprx = arcpy.mp.ArcGISProject("CURRENT")
        
        PublicInspectionTools.PublicInspectionSetupDataSource(loadDataSourcePath=loadDataSourcePath, aprx=aprx)

        return
