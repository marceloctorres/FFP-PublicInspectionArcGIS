# -*- coding: utf-8 -*-

from PublicInpectionArcGIS.Utils import STREAM_HANDLER, ToolboxLogger
from PublicInpectionArcGIS.ToolsLib import PublicInspectionTools

ToolboxLogger.initLogger(handler_type=STREAM_HANDLER)
PublicInspectionTools.PublicInspectionSetupDataSource("D:\\mtorres\\OneDrive - Esri NOSA\\Documentos\\ArcGIS\\Projects\\Modelo FFP\\DummyData.gdb")
