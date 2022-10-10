# -*- coding: utf-8 -*-

from PublicInpectionArcGIS.Utils import STREAM_HANDLER, ToolboxLogger
from PublicInpectionArcGIS.ToolsLib import PublicInspectionTools

ToolboxLogger.initLogger(handler_type=STREAM_HANDLER)
PublicInspectionTools.PublicInspectionTool1(
    param0="Parameter 0 Tool 1"
)