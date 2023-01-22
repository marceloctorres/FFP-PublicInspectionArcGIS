import arcpy
import os

from PublicInspectionArcGIS.CaptureSignatureTool import CaptureSignatureTool
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
    aprx_file = os.path.join(project_folder, project_file)
    aprx = arcpy.mp.ArcGISProject(aprx_file)

    tool = CaptureSignatureTool()

    if tool != None :
        backend = PublicInspectionTools.getCaptureSignature(aprx=aprx)
        tool.tool = backend

        #legal_id = "13248000000010430000"
        legal_id = "13248000000010445000"
        spatialunit = backend.get_spatialunit_by_legal_id(legal_id=legal_id)
        parties = backend.get_parties_by_spatialunit(spatialunit)

        neighboring_approvals = backend.get_neighboring_approvals(spatialunit, parties[0])

        for neighboring_approval in neighboring_approvals :
            neighboring_approval["is_approved"] = "Yes" if neighboring_approval["is_approved"] == "No Processed" else neighboring_approval["is_approved"]

        print(parties)
        print(neighboring_approvals)

        if parties and neighboring_approvals:
            party_names = [party["name"] for party in parties]

            value_table = []
            for approval in neighboring_approvals:
                value_table.append([approval["neighbors"], "Yes" if approval["is_approved"] == "No Processed" else approval["is_approved"]])

            params = tool.getParameterInfo()
            params[0].value = legal_id
            params[1].value = party_names[0]
            params[2].values = value_table

            tool.execute(params, None)


