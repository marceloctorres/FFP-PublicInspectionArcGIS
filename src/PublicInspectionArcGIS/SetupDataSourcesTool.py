import arcpy
import os
import arcpy

from PublicInspectionArcGIS.Utils import ARCGIS_HANDLER, STREAM_HANDLER, ToolboxLogger
from PublicInspectionArcGIS.ToolsLib import PublicInspectionTools

class SetupDataSourcesTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Setup Datasources"
        self.description = "Create FGDBs to make Public Inspection"
        self.alias = "SetupDataSourcesTool"
        
        self.canRunInBackground = True
        self.Params = {"param0": 0}

        if ToolboxLogger._logger is None:
            ToolboxLogger.initLogger(handler_type = STREAM_HANDLER | ARCGIS_HANDLER )
            ToolboxLogger.setInfoLevel()

        try :         
            aprx = arcpy.mp.ArcGISProject("CURRENT")
            self.tool = PublicInspectionTools.getSetupDataSource(aprx)
        except Exception as e:  
            self.tool = None
            ToolboxLogger.debug("Error initializing CalculateBoundariesTool: {}".format(e))

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
        if self.tool is not None:
            loadDataSourcePath = parameters[self.Params["param0"]].valueAsText

            self.tool.loadDataSourcePath = loadDataSourcePath
            self.tool.execute()

        return
