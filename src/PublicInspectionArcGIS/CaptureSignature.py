import arcpy
import os
import csv

from PublicInspectionArcGIS.Utils import ToolboxLogger
from PublicInspectionArcGIS.ArcpyDataAccess import ArcpyDataAccess

class CaptureSignaturesTool :

    def __init__(self, configuration, aprx) :
        self.aprx = aprx
        self.folder = self.aprx.homeFolder

        self.INSPECTION_DATASET_NAME = configuration.getConfigKey("INSPECTION_DATASET_NAME")
        self.INSPECTION_MAP = configuration.getConfigKey("INSPECTION_MAP")

        self.PARTY_NAME = configuration.getConfigKey("PARTY_NAME")
        self.PARTY_ID_FIELD = configuration.getConfigKey("PARTY_ID_FIELD")
        self.PARTY_FK_FIELD = configuration.getConfigKey("PARTY_FK_FIELD")

        self.APPROVAL_NAME = configuration.getConfigKey("APPROVAL_NAME")
        self.APPROVAL_ID_FIELD = configuration.getConfigKey("APPROVAL_ID_FIELD")
        self.APPROVAL_FK_FIELD = configuration.getConfigKey("APPROVAL_FK_FIELD")

        self.APPROVAL_SIGNATURE_NAME =configuration.getConfigKey("APPROVAL_SIGNATURE_NAME")
        self.APPROVAL_SIGNATURE_ID_FIELD = configuration.getConfigKey("APPROVAL_SIGNATURE_ID_FIELD")

        self.inspectionDataSource = os.path.join(self.folder, self.INSPECTION_DATASET_NAME)
        self.da = ArcpyDataAccess(self.inspectionDataSource)

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
        ToolboxLogger.info("Match Table: '{}' truncated.".format(self.matchTablePath))
    
    @ToolboxLogger.log_method
    def getSelectedParties(self) :

        map = self.aprx.listMaps(self.INSPECTION_MAP)[0]
        search_tables = [l for l in map.listTables() if l.name == self.PARTY_NAME]
        partyTable = search_tables[0] if len(search_tables) > 0 else None
        selectedRows = partyTable.getSelectionSet()

        if len(selectedRows) == 1 :
            ToolboxLogger.info("One party selected.")
            self.setMatchTable()

            row_id = selectedRows.pop()
            parties = self.da.query(self.PARTY_NAME, ["OBJECTID", self.PARTY_ID_FIELD], "OBJECTID = {}".format(row_id))

            self.guid = parties[0][self.PARTY_ID_FIELD]
            ToolboxLogger.info("Party ID: {}".format(self.guid))     

            command = "D:\\FFP\\FFP-SignatureCapture\\FFP.SignatureCapture.exe -fp \"{}\\{}.png\"".format(self.folder, self.guid.lower())
            output = os.popen(command)
            output.read()

            signatureFilePath = os.path.join(self.folder, "{}.png".format(self.guid.lower()))
            if os.path.exists(signatureFilePath) :
                ToolboxLogger.info("Signature File: {}".format(signatureFilePath))

                approvals = self.da.query(self.APPROVAL_NAME, [self.APPROVAL_ID_FIELD, self.PARTY_FK_FIELD], "{} = '{}'".format(self.PARTY_FK_FIELD, self.guid))
                approvals_ids = ["'{}'".format(i[self.APPROVAL_ID_FIELD]) for i in approvals]
                approval_signatures = self.da.query(self.APPROVAL_SIGNATURE_NAME, [self.APPROVAL_SIGNATURE_ID_FIELD, self.APPROVAL_FK_FIELD], "{} IN ({})".format(self.APPROVAL_FK_FIELD, ",".join(approvals_ids)))

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

        elif len(selectedRows) > 1 :
            ToolboxLogger.error("More than one party selected.")
        else :  
            ToolboxLogger.error("No party selected.")

    @ToolboxLogger.log_method
    def execute(self) :
        self.getSelectedParties()
