import arcpy
import os

from datetime import datetime
from PublicInspectionArcGIS.Utils import ToolboxLogger
from PublicInspectionArcGIS.ArcpyDataAccess import ArcpyDataAccess

class CaptureSignaturesTool :
    def __init__(self, configuration, aprx, legal_id) :
        self.legal_id = legal_id
        self.aprx = aprx
        self.folder = self.aprx.homeFolder

        self.INSPECTION_DATASET_NAME = configuration.getConfigKey("INSPECTION_DATASET_NAME")
        self.INSPECTION_MAP = configuration.getConfigKey("INSPECTION_MAP")

        self.SPATIAL_UNIT_NAME = configuration.getConfigKey("SPATIAL_UNIT_NAME")
        self.SPATIAL_UNIT_ID_FIELD = configuration.getConfigKey("SPATIAL_UNIT_ID_FIELD")
        self.SPATIAL_UNIT_NAME_FIELD = configuration.getConfigKey("SPATIAL_UNIT_NAME_FIELD")
        self.SPATIAL_UNIT_BOUNDARY_NAME = configuration.getConfigKey("SPATIAL_UNIT_BOUNDARY_NAME")
        self.SPATIAL_UNIT_FK_FIELD = configuration.getConfigKey("SPATIAL_UNIT_FK_FIELD")
        self.SPATIAL_UNIT_LEGAL_ID_FIELD = configuration.getConfigKey("SPATIAL_UNIT_LEGAL_ID_FIELD")
        
        self.BOUNDARY_NAME = configuration.getConfigKey("BOUNDARY_NAME")
        self.BOUNDARY_ID_FIELD = configuration.getConfigKey("BOUNDARY_ID_FIELD")
        self.BOUNDARY_DESCRIPTION_FIELD = configuration.getConfigKey("BOUNDARY_DESCRIPTION_FIELD")
        self.BOUNDARY_FK_FIELD = configuration.getConfigKey("BOUNDARY_FK_FIELD")

        self.RIGHT_NAME = configuration.getConfigKey("RIGHT_NAME")
        self.RIGHT_ID_FIELD = configuration.getConfigKey("RIGHT_ID_FIELD")
        self.RIGHT_FK_FIELD = configuration.getConfigKey("RIGHT_FK_FIELD")        

        self.PARTY_NAME = configuration.getConfigKey("PARTY_NAME")
        self.PARTY_ID_FIELD = configuration.getConfigKey("PARTY_ID_FIELD")
        self.PARTY_FK_FIELD = configuration.getConfigKey("PARTY_FK_FIELD")

        self.BOUNDARY_FK_FIELD = configuration.getConfigKey("BOUNDARY_FK_FIELD")
        self.BOUNDARY_NAME = configuration.getConfigKey("BOUNDARY_NAME")
        self.BOUNDARY_ID_FIELD = configuration.getConfigKey("BOUNDARY_ID_FIELD")
        self.BOUNDARY_STATE_FIELD = configuration.getConfigKey("BOUNDARY_STATE_FIELD")

        self.APPROVAL_NAME = configuration.getConfigKey("APPROVAL_NAME")
        self.APPROVAL_ID_FIELD = configuration.getConfigKey("APPROVAL_ID_FIELD")
        self.APPROVAL_FK_FIELD = configuration.getConfigKey("APPROVAL_FK_FIELD")
        self.APPROVAL_DATE_FIELD = configuration.getConfigKey("APPROVAL_DATE_FIELD")
        self.APPROVAL_IS_APPROVED_FIELD = configuration.getConfigKey("APPROVAL_IS_APPROVED_FIELD")

        self.APPROVAL_SIGNATURE_NAME =configuration.getConfigKey("APPROVAL_SIGNATURE_NAME")
        self.APPROVAL_SIGNATURE_ID_FIELD = configuration.getConfigKey("APPROVAL_SIGNATURE_ID_FIELD")
        self.SIGNATURE_CAPTURE_TOOL_RELATIVE_PATH = configuration.getConfigKey("SIGNATURE_CAPTURE_TOOL_RELATIVE_PATH")
        self.SIGNATURE_CAPTURE_TOOL_COMMAND = configuration.getConfigKey("SIGNATURE_CAPTURE_TOOL_COMMAND")
        self.SIGNATURES_RELATIVE_PATH = configuration.getConfigKey("SIGNATURES_RELATIVE_PATH")
        self.APPROVAL_SIGNATURE_FK_FIELD = configuration.getConfigKey("APPROVAL_SIGNATURE_FK_FIELD")
        self.APPROVAL_SIGNATURE_ATTACH_NAME = configuration.getConfigKey("APPROVAL_SIGNATURE_ATTACH_NAME")
        self.APPROVAL_SIGNATURE_ATTACH_ATT_NAME_FIELD = configuration.getConfigKey("APPROVAL_SIGNATURE_ATTACH_ATT_NAME_FIELD")

        self.inspectionDataSource = os.path.join(self.folder, self.INSPECTION_DATASET_NAME)
        self.da = ArcpyDataAccess(self.inspectionDataSource)

        self.signatureCaptureToolPath = os.path.join(self.folder, self.SIGNATURE_CAPTURE_TOOL_RELATIVE_PATH)
        self.signaturesPath = os.path.join(self.folder, self.SIGNATURES_RELATIVE_PATH)

        self.matchtableName = "MatchTable"
        self.matchField = "MatchID"
        self.pictureField = "PicturePath"

        ToolboxLogger.info("Proyect File:           {}".format(aprx.filePath))
        ToolboxLogger.info("Inspection Data Source: {}".format(self.inspectionDataSource))
    
    @ToolboxLogger.log_method
    def setMatchTable(self) :
        workspace = arcpy.env.workspace
        arcpy.env.workspace = arcpy.env.scratchGDB
        exist_machtable = arcpy.Exists(self.matchtableName)
        arcpy.env.workspace = workspace

        self.matchTablePath = os.path.join(arcpy.env.scratchGDB, self.matchtableName)
        if not exist_machtable :
            arcpy.management.CreateTable(arcpy.env.scratchGDB, self.matchtableName)
            ToolboxLogger.info("Match Table: '{}' created.".format(self.matchTablePath))

        fields = arcpy.ListFields(self.matchTablePath)
        field_names = [f.name for f in fields if f.name == self.matchField or f.name == self.pictureField]

        if len(field_names) == 0 :
            arcpy.management.AddField(self.matchTablePath, self.matchField, "TEXT")
            arcpy.management.AddField(self.matchTablePath, self.pictureField, "TEXT")

        arcpy.management.TruncateTable(self.matchTablePath)
        ToolboxLogger.info("Match Table truncated.")

    @ToolboxLogger.log_method
    def updateApprovalsIsApprovedCursor(self, approvals) :
        try:
            approval_ids = ["'{}'".format(approval[self.APPROVAL_ID_FIELD]) for approval in approvals]
            self.da.update(self.APPROVAL_NAME, fields=[self.APPROVAL_IS_APPROVED_FIELD, self.APPROVAL_DATE_FIELD], 
                values=["Yes", datetime.today()],
                filter="{} IN ({})".format(self.APPROVAL_ID_FIELD, ",".join(approval_ids)))
        except Exception as e:
            ToolboxLogger.error("Error updating approvals: {}".format(e))

    @ToolboxLogger.log_method
    def updateApprovalsIsApprovedTools(self, approvals) :
        try:
            approval_ids = ["'{}'".format(approval[self.APPROVAL_ID_FIELD]) for approval in approvals]
            arcpy.management.MakeTableView(self.da.findTablePath(self.APPROVAL_NAME), "in_memory\out_view", "{} IN ({})".format(self.APPROVAL_ID_FIELD, ",".join(approval_ids)))
            arcpy.management.CalculateField("in_memory\out_view", self.APPROVAL_IS_APPROVED_FIELD, "'Yes'")
            arcpy.management.CalculateField("in_memory\out_view", self.APPROVAL_DATE_FIELD, "datetime.datetime.now()", "PYTHON3")
        except Exception as e:
            ToolboxLogger.error("Error updating approvals: {}".format(e))

    @ToolboxLogger.log_method
    def updateApprovalState(self, approvals):
        ToolboxLogger.info("Updating Approvals ...")
        self.updateApprovalsIsApprovedCursor(approvals)
        self.updateBoundaryState(approvals)
        ToolboxLogger.info("Approvals updated.")

    @ToolboxLogger.log_method
    def updateBoundaryStateCursor(self, boundaries):
        ToolboxLogger.info("Updating Boundaries ...")
        for boundary in boundaries:
            try :
                self.da.update(self.BOUNDARY_NAME, fields=[self.BOUNDARY_STATE_FIELD], values=[boundary[self.BOUNDARY_STATE_FIELD]], filter="{} = '{}'".format(self.BOUNDARY_ID_FIELD, boundary[self.BOUNDARY_ID_FIELD]))
            except Exception as e:
                ToolboxLogger.error("Error updating boundary: {}".format(e))

        ToolboxLogger.info("Boundaries updated.")

    @ToolboxLogger.log_method
    def updateBoundaryState(self, approvals):
        boundaries_ids = ["'{}'".format(approval[self.BOUNDARY_FK_FIELD]) for approval in approvals]
        boundaries_approvals = self.da.query(self.APPROVAL_NAME, [self.APPROVAL_IS_APPROVED_FIELD, self.BOUNDARY_FK_FIELD], "{} IN ({})".format(self.BOUNDARY_FK_FIELD, ",".join(boundaries_ids)))
        boundaries = self.da.query(self.BOUNDARY_NAME, [self.BOUNDARY_ID_FIELD, self.BOUNDARY_STATE_FIELD], "{} IN ({})".format(self.BOUNDARY_ID_FIELD, ",".join(boundaries_ids)))

        for boundary in boundaries:
            boundary_approvals = [approval for approval in boundaries_approvals if approval[self.BOUNDARY_FK_FIELD] == boundary[self.BOUNDARY_ID_FIELD]]
            if all([approval[self.APPROVAL_IS_APPROVED_FIELD] == "No Processed" for approval in boundary_approvals]) :
                boundary[self.BOUNDARY_STATE_FIELD] = "No Processed"
            elif all([approval[self.APPROVAL_IS_APPROVED_FIELD] == "Yes" for approval in boundary_approvals]) :
                boundary[self.BOUNDARY_STATE_FIELD] = "Approved"
            elif any([approval[self.APPROVAL_IS_APPROVED_FIELD] == "No" for approval in boundary_approvals]):
                boundary[self.BOUNDARY_STATE_FIELD] = "Rejected"
            else:   
                boundary[self.BOUNDARY_STATE_FIELD] = "In Process"

        self.updateBoundaryStateCursor(boundaries)

    def __getMapTable(self, table_name):
        map = self.aprx.listMaps(self.INSPECTION_MAP)[0]
        search_tables = [l for l in map.listTables() if l.name == table_name]
        return search_tables[0] if len(search_tables) > 0 else None

    def __getMapLayer(self, layer_name):
        map = self.aprx.listMaps(self.INSPECTION_MAP)[0]
        search_layers = [l for l in map.listLayers() if l.name == layer_name]
        return search_layers[0] if len(search_layers) > 0 else None

    @ToolboxLogger.log_method
    def setPartySignatureAttachment(self) :
        approvalTable = self.__getMapTable(self.APPROVAL_NAME)
        boundaryLayer = self.__getMapLayer(self.BOUNDARY_NAME)

        if(approvalTable and boundaryLayer) :
            approvalTable.setSelectionSet([], "NEW")
            boundaryLayer.setSelectionSet([], "NEW")

        spatialUnits = self.da.query(self.SPATIAL_UNIT_NAME, [self.SPATIAL_UNIT_ID_FIELD, self.SPATIAL_UNIT_LEGAL_ID_FIELD], "{} = '{}'".format(self.SPATIAL_UNIT_LEGAL_ID_FIELD, self.legal_id))
        spatialUnit_id = spatialUnits[0][self.SPATIAL_UNIT_ID_FIELD] if len(spatialUnits) > 0 else None

        if spatialUnit_id:
            self.setMatchTable()

            rights = self.da.query(self.RIGHT_NAME, [self.RIGHT_ID_FIELD], "{} = '{}'".format(self.SPATIAL_UNIT_FK_FIELD, spatialUnit_id))
            right_id = rights[0][self.RIGHT_ID_FIELD] if len(rights) > 0 else None

            if right_id:
                parties = self.da.query(self.PARTY_NAME, [self.PARTY_ID_FIELD], "{} = '{}'".format(self.RIGHT_FK_FIELD, right_id))
                party_id = parties[0][self.PARTY_ID_FIELD] if len(parties) > 0 else None

                if party_id:
                    self.guid = party_id
                    ToolboxLogger.info("Party ID: {}".format(self.guid))     

                    command = "\"{}\" {} \"{}\\{}.png\"".format(self.signatureCaptureToolPath, self.SIGNATURE_CAPTURE_TOOL_COMMAND, self.signaturesPath, self.guid.lower())
                    output = os.popen(command)
                    output.read()

                    signatureFilename = "{}.png".format(self.guid.lower())
                    signatureFilePath = os.path.join(self.signaturesPath, signatureFilename)

                    if os.path.exists(signatureFilePath) :
                        ToolboxLogger.info("Signature File: {}".format(signatureFilePath))

                        approvals = self.da.query(self.APPROVAL_NAME, [self.APPROVAL_ID_FIELD, self.PARTY_FK_FIELD, self.BOUNDARY_FK_FIELD], "{} = '{}'".format(self.PARTY_FK_FIELD, self.guid))
                        approvals_ids = ["'{}'".format(i[self.APPROVAL_ID_FIELD]) for i in approvals]

                        approval_signatures = self.da.query(self.APPROVAL_SIGNATURE_NAME, [self.APPROVAL_SIGNATURE_ID_FIELD, self.APPROVAL_FK_FIELD], "{} IN ({})".format(self.APPROVAL_FK_FIELD, ",".join(approvals_ids)))
                        approval_signatures_ids = ["'{}'".format(i[self.APPROVAL_SIGNATURE_ID_FIELD]) for i in approval_signatures]

                        self.da.delete(self.APPROVAL_SIGNATURE_ATTACH_NAME, 
                            filter= "{} = '{}' AND {} IN ({})".format(self.APPROVAL_SIGNATURE_ATTACH_ATT_NAME_FIELD, signatureFilename, self.APPROVAL_SIGNATURE_FK_FIELD, ",".join(approval_signatures_ids)))

                        match_da = ArcpyDataAccess(arcpy.env.scratchGDB)
                        for approval_signature in approval_signatures :
                            values = []
                            value = tuple([approval_signature[self.APPROVAL_SIGNATURE_ID_FIELD], signatureFilePath])
                            values.append(value)

                            match_da.add(self.matchtableName, [self.matchField, self.pictureField], values)
                        match_da = None

                        arcpy.AddAttachments_management(self.da.findTablePath(self.APPROVAL_SIGNATURE_NAME), 
                            self.APPROVAL_SIGNATURE_ID_FIELD, 
                            self.matchTablePath, 
                            self.matchField, 
                            self.pictureField)
                        
                        self.updateApprovalState(approvals)
                else :
                    ToolboxLogger.error("Party not found")
            else :
                ToolboxLogger.error("Right not found")
        else :
            ToolboxLogger.error("Spatial Unit not found")

    @ToolboxLogger.log_method
    def execute(self) :
        self.setPartySignatureAttachment()
