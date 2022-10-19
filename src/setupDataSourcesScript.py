# -*- coding: utf-8 -*-
import arcpy
from PublicInpectionArcGIS.Utils import STREAM_HANDLER, ToolboxLogger
from PublicInpectionArcGIS.ToolsLib import PublicInspectionTools

ToolboxLogger.initLogger(handler_type=STREAM_HANDLER)
fgdb_load = "D:\\FFP\\Load_Data.gdb"
aprx_file = "D:\\mtorres\\OneDrive - Esri NOSA\\Documentos\\ArcGIS\Projects\\Public Inspection\\Public Inspection.aprx"
aprx = arcpy.mp.ArcGISProject(aprx_file)
PublicInspectionTools.PublicInspectionSetupDataSource(fgdb_load, aprx)
