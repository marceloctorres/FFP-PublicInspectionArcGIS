# -*- coding: utf-8 -*-

from PublicInspectionArcGIS.Utils import STREAM_HANDLER, ToolboxLogger
from PublicInspectionArcGIS.ToolsLib import PublicInspectionTools

ToolboxLogger.initLogger(handler_type=STREAM_HANDLER)
PublicInspectionTools.PublicInspectionTool2(
    param0="Parameter 0 Tool 2"
)