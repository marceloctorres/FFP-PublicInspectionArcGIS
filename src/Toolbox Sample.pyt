# -*- coding: utf-8 -*-

import arcpy
from PublicInspectionArcGIS.bar import Tool

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Sample Python Toolbox"
        self.alias = "SamplePythonToolbox"

        # List of tool classes associated with this toolbox
        self.tools = [SampleTool]

class SampleTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Sample Tool"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        parameters=[arcpy.Parameter(displayName='Msg', 
                                  name='msg',
                                  datatype='GPString',
                                  parameterType='Derived',
                                  direction='Output')
                                  ]
        return parameters

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

        tool = Tool()
        result = tool.hello()
        messages.AddMessage(f"{result}, welcome to the sample tool")
        parameters[0].value = result        
        return