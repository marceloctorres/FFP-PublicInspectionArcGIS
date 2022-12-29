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
        
        self.Params = {"legal_id": 0, "party_name": 1, "neighbors_approvals" : 2}
        self.canRunInBackground = True

        ToolboxLogger.initLogger(handler_type = STREAM_HANDLER | ARCGIS_HANDLER )
        ToolboxLogger.setInfoLevel()

        aprx = arcpy.mp.ArcGISProject("CURRENT")
        self.tool = PublicInspectionTools.getCaptureSignatureTool(aprx)

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
            displayName="Party Name",
            name="party_name",
            datatype="GPString",
            parameterType="Required",
            direction="Input",
            enabled=False
        )
        params.insert(self.Params["party_name"], param)

        param = arcpy.Parameter(
            displayName="Boundaries Approvals",
            name="neighbors_approvals",
            datatype="DETable",
            parameterType="Required",
            direction="Input",
            enabled=False
        )
        param.columns = [['GPString', 'Party Name'], ['GPString', 'Approval State']]
        param.filters[1].type = 'ValueList'
        param.filters[1].list = ['Yes', 'No']
        
        params.insert(self.Params["neighbors_approvals"], param)

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        if not parameters[self.Params["legal_id"]].altered :
            parameters[self.Params["party_name"]].enabled = False
            parameters[self.Params["party_name"]].filter.list = []
            parameters[self.Params["party_name"]].value = None

        if not parameters[self.Params["party_name"]].altered :
            parameters[self.Params["neighbors_approvals"]].enabled = False
            parameters[self.Params["neighbors_approvals"]].values = []

        if parameters[self.Params["legal_id"]].altered \
                and parameters[self.Params["legal_id"]].valueAsText \
                and not parameters[self.Params["legal_id"]].hasBeenValidated:

            legal_id = parameters[self.Params["legal_id"]].valueAsText
            spatialunit = self.tool.get_spatialunit_by_legal_id(legal_id)
            parties = self.tool.get_parties_by_spatialunit(spatialunit)

            if parties:
                party_names = [party["name"] for party in parties]
                parameters[self.Params["party_name"]].enabled = len(party_names) > 1
                parameters[self.Params["party_name"]].filter.list = party_names
                parameters[self.Params["party_name"]].value = party_names[0] if len(party_names) == 1 else None

            parameters[self.Params["neighbors_approvals"]].enabled = False
            parameters[self.Params["neighbors_approvals"]].values = []

        if parameters[self.Params["party_name"]].altered \
                and parameters[self.Params["party_name"]].valueAsText \
                and not parameters[self.Params["party_name"]].hasBeenValidated:

            legal_id = parameters[self.Params["legal_id"]].valueAsText
            party_name = parameters[self.Params["party_name"]].valueAsText

            spatialunit = self.tool.get_spatialunit_by_legal_id(legal_id)
            parties = self.tool.get_parties_by_spatialunit(spatialunit)
            party = [party for party in parties if party["name"] == party_name][0]
            neighboring_approvals = self.tool.get_neighboring_approvals(spatialunit, party)

            if neighboring_approvals:
                value_table = []
                for approval in neighboring_approvals:
                    value_table.append([approval["neighbors"], "Yes" if approval["is_approved"] == "No Processed" else approval["is_approved"]])

                parameters[self.Params["neighbors_approvals"]].enabled = len(value_table) > 0
                parameters[self.Params["neighbors_approvals"]].values = value_table
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        legal_id = parameters[self.Params["legal_id"]].valueAsText
        party_name = parameters[self.Params["party_name"]].valueAsText
        value_table = parameters[self.Params["neighbors_approvals"]].values

        ToolboxLogger.info("Value Table: {}".format(value_table))

        self.tool.spatialunit = self.tool.get_spatialunit_by_legal_id(legal_id)
        parties = self.tool.get_parties_by_spatialunit(self.tool.spatialunit)
        self.tool.party = [party for party in parties if party["name"] == party_name][0] if len(parties) > 0 else None

        ToolboxLogger.info("Spatial Unit: {}".format(self.tool.spatialunit))
        ToolboxLogger.info("Party: {}".format(self.tool.party))

        if self.tool.spatialunit and self.tool.party:
            self.tool.neighboring_approvals = self.tool.get_neighboring_approvals(self.tool.spatialunit, self.tool.party)
            for value in value_table:
                for approval in self.tool.neighboring_approvals:
                    if approval["neighbors"] == value[0]:
                        approval["is_approved"] = value[1]
            self.tool.execute()

        return        