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
    project_folder = debug.getConfigKey("project_folder")
    project_file = debug.getConfigKey("project_file")
    aprx_file = os.path.join(project_folder, project_file)
    aprx = arcpy.mp.ArcGISProject(aprx_file)
    tool = PublicInspectionTools.getCaptureSignature(aprx)

    if tool != None :
        #legal_id = "13248000000010430000"
        legal_id = "13248000000010445000"
        spatialunit = tool.get_spatialunit_by_legal_id(legal_id=legal_id)
        parties = tool.get_parties_by_spatialunit(spatialunit)
        neighboring_approvals = tool.get_neighboring_approvals(spatialunit, parties[0])

        for neighboring_approval in neighboring_approvals :
            neighboring_approval["is_approved"] = "Yes" if neighboring_approval["is_approved"] == "No Processed" else neighboring_approval["is_approved"]

        print(parties)
        print(neighboring_approvals)

        tool.spatialunit = spatialunit
        tool.party = parties[0]
        tool.neighboring_approvals = neighboring_approvals
        tool.execute()

        print()
        print("Signature captured")