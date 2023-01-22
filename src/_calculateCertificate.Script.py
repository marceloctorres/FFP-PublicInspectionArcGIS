# -*- coding: utf-8 -*-
import arcpy
import os

from PublicInspectionArcGIS.Utils import CONFIG_PATH, STREAM_HANDLER, ToolboxLogger, Configuration
from PublicInspectionArcGIS.ToolsLib import PublicInspectionTools

CONFIG_PATH = "debug.json"
INSPECTION_FGDB = "Public Inspeccion.gdb"
ToolboxLogger.initLogger(handler_type=STREAM_HANDLER)
ToolboxLogger.setDebugLevel()

folder_path = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(folder_path, CONFIG_PATH)

aprx_file="D:\\yquinonez\\Documents\\FFP-2.0\\FFP_2.0\\FFP-ArcGISPro-Project\\src\\Public Inspection\\Public Inspection.aprx"
aprx = arcpy.mp.ArcGISProject(aprx_file)

tool=PublicInspectionTools.getCalculateCertificate(aprx)
tool.legal_id="13248000000010432000"
tool.visitor_contact="Jose maria"
tool.execute()

   