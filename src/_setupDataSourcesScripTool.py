import arcpy
import os

from PublicInspectionArcGIS.SetupDataSourcesTool import SetupDataSourcesTool
from PublicInspectionArcGIS.ToolsLib import PublicInspectionTools
from PublicInspectionArcGIS.Utils import CONFIG_PATH, ToolboxLogger, Configuration, ARCGIS_HANDLER, STREAM_HANDLER

CONFIG_PATH = "debug.json"

if ToolboxLogger._logger is None:
    ToolboxLogger.initLogger(handler_type = STREAM_HANDLER)
    ToolboxLogger.setDebugLevel()

folder_path = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(folder_path, CONFIG_PATH)

if os.path.exists(config_path) :
    debug = Configuration(config_path)
    project_folder = debug.getConfigKey("project_folder")
    project_file = debug.getConfigKey("project_file")
    data_folder = debug.getConfigKey("data_folder")
    aprx_file = os.path.join(project_folder, project_file)
    aprx = arcpy.mp.ArcGISProject(aprx_file)

    tool = SetupDataSourcesTool()

    if tool != None :
        backend = PublicInspectionTools.getSetupDataSource(aprx=aprx)
        tool.tool = backend
        fgdb_load = os.path.join(data_folder, "dummydata_load.gdb")

        params = tool.getParameterInfo()
        params[0].value = fgdb_load 
        tool.execute(params, None)


