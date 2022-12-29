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

# if os.path.exists(config_path) :
#     config = Configuration(config_path)
#     inspectionDataSource = os.path.join(config.getConfigKey('project_folder'), INSPECTION_FGDB)
inspectionDataSource="D:\\yquinonez\\Documents\\FFP-2.0\\Public Inspeccion\\Public Inspeccion.gdb"    
PublicInspectionTools.CalculateCertificate(inspectionDataSource)
   