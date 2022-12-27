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
        self.tools = [SetupDataSourcesTool, CalculateBoundariesTool, CaptureSignatureTool]

class SetupDataSourcesTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Setup Datasources"
        self.description = "Create FGDBs to make Public Inspection"
        self.alias = "SetupDataSourcesTool"
        
        self.canRunInBackground = True
        self.Params = {"param0": 0}
        ToolboxLogger.initLogger(handler_type = STREAM_HANDLER | ARCGIS_HANDLER )
        ToolboxLogger.setInfoLevel()

    def getParameterInfo(self):
        """Define parameter definitions"""
        params = []

        param = arcpy.Parameter(
            displayName="Input FGDB",
            name="param0",
            datatype="DEWorkspace",
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
        
        PublicInspectionTools.SetupDataSource(loadDataSourcePath=loadDataSourcePath, aprx=aprx)
        return

class CalculateBoundariesTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Calculate Boundaries"
        self.description = "Calculate Boundaries to add to Public Inspection"
        self.alias = "CalculateBoundariesTool"
        
        self.canRunInBackground = True
        ToolboxLogger.initLogger(handler_type = STREAM_HANDLER | ARCGIS_HANDLER )
        ToolboxLogger.setInfoLevel()

    def getParameterInfo(self):
        """Define parameter definitions"""
        params = []
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
        aprx = arcpy.mp.ArcGISProject("CURRENT")
        PublicInspectionTools.CalculateBoundaries(aprx=aprx)

        return

class CaptureSignatureTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Capture Signature"
        self.description = "Capture Party Signature to express agreement to Public Inspection"
        self.alias = "CaptureSignatureTool"
        
        self.Params = {"param0": 0, "param1": 1}
        self.canRunInBackground = True

        ToolboxLogger.initLogger(handler_type = STREAM_HANDLER | ARCGIS_HANDLER )
        ToolboxLogger.setInfoLevel()

        aprx = arcpy.mp.ArcGISProject("CURRENT")
        self.tool = PublicInspectionTools.getCaptureSignatureTool(aprx)
        self.parties = []

    def getParameterInfo(self):
        """Define parameter definitions"""
        params = []

        param = arcpy.Parameter(
            displayName="Legal ID",
            name="param0",
            datatype="GPString",
            parameterType="Required",
            direction="Input",
        )
        params.insert(self.Params["param0"], param)

        param = arcpy.Parameter(
            displayName="Party Name",
            name="param1",
            datatype="GPString",
            parameterType="Required",
            direction="Input",
            enabled=False
        )
        params.insert(self.Params["param1"], param)

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        if parameters[self.Params["param0"]].altered and parameters[self.Params["param0"]].valueAsText:
            legal_id = parameters[self.Params["param0"]].valueAsText
            self.spatialunit = self.tool.get_spatialunit(legal_id)
            self.parties = self.tool.get_parties(self.spatialunit)
            if self.parties:
                party_names = [party["name"] for party in self.parties]
                parameters[self.Params["param1"]].enabled = len(party_names) > 1
                parameters[self.Params["param1"]].filter.list = party_names
                parameters[self.Params["param1"]].value = party_names[0]
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        party_name = parameters[self.Params["param1"]].valueAsText
        ToolboxLogger.info("Party Name: {}".format(party_name))
        if party_name:
            self.tool.party_id = self.parties[parameters[self.Params["param1"]].filter.list.index(party_name)]["id"]
            ToolboxLogger.info("Party ID: {}".format(self.tool.party_id))
            
            self.tool.execute()

        return        