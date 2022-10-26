# -*- coding: utf-8 -*-
import arcpy
import os

from PublicInpectionArcGIS.Utils import CONFIG_PATH, STREAM_HANDLER, ToolboxLogger, Configuration
from PublicInpectionArcGIS.ToolsLib import PublicInspectionTools

CONFIG_PATH = "debug.json"
ToolboxLogger.initLogger(handler_type=STREAM_HANDLER)
ToolboxLogger.setDebugLevel()

folder_path = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(folder_path, CONFIG_PATH)

if os.path.exists(config_path) :
    config = Configuration(config_path)
    data_folder = config.getConfigKey("data_folder")
    project_folder = config.getConfigKey("project_folder")
    fgdb_load = os.path.join(data_folder, "Load_Data.gdb")
    aprx_file = os.path.join(project_folder, "Public Inspection.aprx")

    aprx = arcpy.mp.ArcGISProject(aprx_file)
    PublicInspectionTools.SetupDataSource(fgdb_load, aprx)

