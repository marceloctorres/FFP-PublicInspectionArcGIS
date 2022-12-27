import arcpy
import os

from datetime import datetime
from PublicInspectionArcGIS.Utils import ToolboxLogger, Configuration
from PublicInspectionArcGIS.ArcpyDataAccess import ArcpyDataAccess
from PublicInspectionArcGIS.PublicInspectionTool import PublicInspectionTool

class CaptureSignaturesTool(PublicInspectionTool) :
    def __init__(self, configuration : Configuration, aprx : arcpy.mp.ArcGISProject) :
        super().__init__(configuration, aprx)
        self.party_id = None
        self.spatialunit = None

        self.SIGNATURE_CAPTURE_TOOL_RELATIVE_PATH = configuration.getConfigKey("SIGNATURE_CAPTURE_TOOL_RELATIVE_PATH")
        self.SIGNATURE_CAPTURE_TOOL_COMMAND = configuration.getConfigKey("SIGNATURE_CAPTURE_TOOL_COMMAND")
        self.SIGNATURES_RELATIVE_PATH = configuration.getConfigKey("SIGNATURES_RELATIVE_PATH")

        self.signatureCaptureToolPath = os.path.join(self.folder, self.SIGNATURE_CAPTURE_TOOL_RELATIVE_PATH)
        self.signaturesPath = os.path.join(self.folder, self.SIGNATURES_RELATIVE_PATH)

        self.matchtableName = "MatchTable"
        self.matchField = "MatchID"
        self.pictureField = "PicturePath"

        ToolboxLogger.info("Proyect File:           {}".format(aprx.filePath))
        ToolboxLogger.info("Inspection Data Source: {}".format(self.inspectionDataSource))
        ToolboxLogger.debug("Data Access Object:     {}".format(self.da))
    
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
    def update_approvals_isapproved(self, approvals) :
        try:
            approval_ids = ["'{}'".format(approval[self.APPROVAL_ID_FIELD]) for approval in approvals]
            self.update_approvals(
                fields=[self.APPROVAL_IS_APPROVED_FIELD, self.APPROVAL_DATE_FIELD], 
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
    def update_approvalstate(self, approvals):
        ToolboxLogger.info("Updating Approvals ...")
        self.update_approvals_isapproved(approvals)
        self.set_boundaries_states(approvals)
        ToolboxLogger.info("Approvals updated.")

    @ToolboxLogger.log_method
    def update_boundaries_states(self, boundaries):
        ToolboxLogger.info("Updating Boundaries ...")
        for boundary in boundaries:
            try :
                self.update_boundaries(
                    fields=[self.BOUNDARY_STATE_FIELD], 
                    values=[boundary[self.BOUNDARY_STATE_FIELD]], 
                    filter="{} = '{}'".format(self.BOUNDARY_ID_FIELD, boundary[self.BOUNDARY_ID_FIELD]))
            except Exception as e:
                ToolboxLogger.error("Error updating boundary: {}".format(e))

        ToolboxLogger.info("Boundaries updated.")

    @ToolboxLogger.log_method
    def set_boundaries_states(self, approvals):
        boundaries_ids = ["'{}'".format(approval[self.BOUNDARY_FK_FIELD]) for approval in approvals]
        boundaries_approvals = self.get_approvals(
            fields=[self.APPROVAL_IS_APPROVED_FIELD, self.BOUNDARY_FK_FIELD], 
            filter="{} IN ({})".format(self.BOUNDARY_FK_FIELD, ",".join(boundaries_ids)))
        boundaries = self.get_boundaries(
            fields=[self.BOUNDARY_ID_FIELD, self.BOUNDARY_STATE_FIELD],
            filter="{} IN ({})".format(self.BOUNDARY_ID_FIELD, ",".join(boundaries_ids)))

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

        self.update_boundaries_states(boundaries)

    @ToolboxLogger.log_method
    def set_party_signature_attachment(self) :
        approvalTable = self.get_maptable(self.APPROVAL_NAME)
        boundaryLayer = self.get_maplayer(self.BOUNDARY_NAME)

        if(approvalTable and boundaryLayer) :
            approvalTable.setSelectionSet([], "NEW")
            boundaryLayer.setSelectionSet([], "NEW")

        if self.party_id and self.spatialunit:
            ToolboxLogger.info("Party ID: {}".format(self.party_id.lower()))   
            command = "\"{}\" {} \"{}\\{}.png\"".format(self.signatureCaptureToolPath, self.SIGNATURE_CAPTURE_TOOL_COMMAND, self.signaturesPath, self.party_id.lower())
            output = os.popen(command)
            output.read()

            signatureFilename = "{}.png".format(self.party_id.lower())
            signatureFilePath = os.path.join(self.signaturesPath, signatureFilename)

            if os.path.exists(signatureFilePath) :
                ToolboxLogger.info("Signature File: {}".format(signatureFilename))
                self.setMatchTable()  

                approvals = self.get_approvals(
                    fields=[self.APPROVAL_ID_FIELD, self.PARTY_FK_FIELD, self.BOUNDARY_FK_FIELD],
                    filter="{} = '{}'".format(self.PARTY_FK_FIELD, self.party_id))

                if len(approvals) == 0 :
                    self.set_approvals_by_spatialunit(self.spatialunit)
                    approvals = self.get_approvals(
                        fields=[self.APPROVAL_ID_FIELD, self.PARTY_FK_FIELD, self.BOUNDARY_FK_FIELD],
                        filter="{} = '{}'".format(self.PARTY_FK_FIELD, self.party_id))

                approvals_ids = ["'{}'".format(i[self.APPROVAL_ID_FIELD]) for i in approvals]

                approval_signatures = self.get_aprprovalsignatures(
                    fields=[self.APPROVAL_SIGNATURE_ID_FIELD, self.APPROVAL_FK_FIELD],
                    filter="{} IN ({})".format(self.APPROVAL_FK_FIELD, ",".join(approvals_ids)))
                approval_signatures_ids = ["'{}'".format(i[self.APPROVAL_SIGNATURE_ID_FIELD]) for i in approval_signatures]

                self.da.delete(self.APPROVAL_SIGNATURE_ATTACH_NAME, 
                    filter= "{} = '{}' AND {} IN ({})".format(self.APPROVAL_SIGNATURE_ATTACH_ATT_NAME_FIELD, signatureFilename, self.APPROVAL_SIGNATURE_FK_FIELD, ",".join(approval_signatures_ids)))

                match_da = ArcpyDataAccess(arcpy.env.scratchGDB)
                for approval_signature in approval_signatures :
                    values = []
                    value = tuple([approval_signature[self.APPROVAL_SIGNATURE_ID_FIELD], signatureFilePath])
                    values.append(value)

                    match_da.insert(self.matchtableName, [self.matchField, self.pictureField], values)
                match_da = None

                arcpy.AddAttachments_management(self.da.findTablePath(self.APPROVAL_SIGNATURE_NAME), 
                    self.APPROVAL_SIGNATURE_ID_FIELD, 
                    self.matchTablePath, 
                    self.matchField, 
                    self.pictureField)
                
                self.update_approvalstate(approvals)
        else :
            ToolboxLogger.info("Party not found")

    @ToolboxLogger.log_method
    def execute(self) :
        self.set_party_signature_attachment()

