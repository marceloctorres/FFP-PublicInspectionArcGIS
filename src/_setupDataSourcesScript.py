# -*- coding: utf-8 -*-
import arcpy
import os

from PublicInspectionArcGIS.Utils import CONFIG_PATH, STREAM_HANDLER, ToolboxLogger, Configuration
from PublicInspectionArcGIS.ToolsLib import PublicInspectionTools

CONFIG_PATH = "debug.json"
ToolboxLogger.initLogger(handler_type=STREAM_HANDLER)
ToolboxLogger.setDebugLevel()

folder_path = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(folder_path, CONFIG_PATH)

if os.path.exists(config_path) :
    debug = Configuration(config_path)
    data_folder = debug.getConfigKey("data_folder")
    fgdb_load = os.path.join(data_folder, "dummydata_load.gdb")

    project_folder = debug.getConfigKey("project_folder")
    project_file = debug.getConfigKey("project_file")
    aprx_file = os.path.join(project_folder, project_file)

    aprx = arcpy.mp.ArcGISProject(aprx_file)
    PublicInspectionTools.SetupDataSource(fgdb_load, aprx)

