import arcpy
import shutil
import os
from PublicInpectionArcGIS.Utils import ToolboxLogger

class SetupDataSourcesTool :
    SURVEY_DATASET_NAME = "survey.gdb"
    INSPECTION_DATASET_NAME = "inspection.gdb"
    PARCEL_XML_PATH = "XmlWorkspaceDocuments\\FFP-ParcelFabric.xml"
    LOAD_XML_PATH = "XmlWorkspaceDocuments\\load.xml"
    PARCEL_TYPE = "SpatialUnit"
    PARCEL_RECORD_FIELD = "legal_id"
    PARCEL_FABRIC_PATH = "Parcel\PublicInspection"
    PARCEL_DATASET = "Parcel"
    
    def __init__(self, loadDataSourcePath, aprx) :
        self.aprx = aprx
        self.loadDataSourcePath = loadDataSourcePath
        self.folder = self.aprx.homeFolder
        self.inspectionDataSource = os.path.join(self.folder, self.INSPECTION_DATASET_NAME)
        self.surveyDataSource = os.path.join(self.folder, self.SURVEY_DATASET_NAME)
    
    @ToolboxLogger.log_method
    def createSurveyDataSource(self):
        file_folder_path = os.path.dirname(os.path.realpath(__file__))
        xml_path = os.path.join(file_folder_path, self.LOAD_XML_PATH)
        arcpy.management.ExportXMLWorkspaceDocument(self.loadDataSourcePath, xml_path)
        ToolboxLogger.info("Load data Exported")

        if(os.path.exists(self.surveyDataSource)) :
            arcpy.Delete_management(self.surveyDataSource)

        arcpy.management.CreateFileGDB(self.folder, self.SURVEY_DATASET_NAME)
        ToolboxLogger.info("Survey Dataset Created")
        arcpy.management.ImportXMLWorkspaceDocument(self.surveyDataSource, xml_path)
        ToolboxLogger.info("Survey data Imported")

        arcpy.management.Delete(xml_path)        

    @ToolboxLogger.log_method
    def copySurveyDataSource(self) :
        if(os.path.exists(self.surveyDataSource)) :
            arcpy.Delete_management(self.surveyDataSource)

        shutil.copytree(self.loadDataSourcePath, self.surveyDataSource)
        ToolboxLogger.info("Survey Dataset Created")

    @ToolboxLogger.log_method
    def createInspectionDataSource(self) :
        if(os.path.exists(self.inspectionDataSource)) :
            arcpy.Delete_management(self.inspectionDataSource)

        arcpy.management.CreateFileGDB(self.folder, self.INSPECTION_DATASET_NAME)
        ToolboxLogger.info("Inspection Dataset Created")

        file_folder_path = os.path.dirname(os.path.realpath(__file__))
        xml_path = os.path.join(file_folder_path, self.PARCEL_XML_PATH)

        arcpy.management.ImportXMLWorkspaceDocument(self.inspectionDataSource, xml_path, "SCHEMA_ONLY")
        ToolboxLogger.info("Inspection Parcel Fabric schema imported")
    
    @ToolboxLogger.log_method
    def appendDataset(self, input_ds, output_ds):

        ##arcpy.management.AddIndex(in_table, fields, {index_name}, {unique}, {ascending})
        in_fields = arcpy.ListFields(input_ds)
        out_fields = arcpy.ListFields(output_ds)

        fieldMappings = arcpy.FieldMappings()
        fieldMappings.addTable(output_ds)

        ToolboxLogger.info("Appending {} data...".format(input_ds))

        fm = arcpy.FieldMap()
        for in_field in in_fields:
            if in_field.type != "OID" and in_field.type != "Geometry":
                if in_field.type.lower() == "globalid" :
                    ToolboxLogger.info("{}-->{}".format(in_field.name, in_field.type))
                    arcpy.management.AddIndex(output_ds, [in_field.name], "GUID")

                fm = arcpy.FieldMap()
                fm.addInputField(input_ds, in_field.name)

                out_field = [f for f in out_fields if f.name.lower() == in_field.name.lower()]
                fm.outputField = out_field[0]
                ##ToolboxLogger.info("{}-->{}".format(in_field.name, out_field[0].name))

                fieldMappings.addFieldMap(fm)
                    
        arcpy.management.Append(input_ds, output_ds, "NO_TEST", fieldMappings)
        ToolboxLogger.info("{} data appended".format(input_ds))

    @ToolboxLogger.log_method
    def appendParcelData(self) :
        arcpy.env.workspace = self.loadDataSourcePath
        #arcpy.env.preserveGlobalIds = True

        featureClasses = arcpy.ListFeatureClasses()
        for input_fc in featureClasses:
            output_fc = os.path.join(self.inspectionDataSource, input_fc)

            self.appendDataset(input_fc, output_fc)

        tables = arcpy.ListTables()
        for input_tb in tables:
            output_tb  = os.path.join(self.inspectionDataSource, input_tb)

            self.appendDataset(input_tb, output_tb)

    @ToolboxLogger.log_method
    def createParcelRecords(self) : 
        in_parcel_features = os.path.join(self.inspectionDataSource, self.PARCEL_TYPE)
        arcpy.parcel.CreateParcelRecords(in_parcel_features, self.PARCEL_RECORD_FIELD) 
        ToolboxLogger.info("Parcel Records Created")

    @ToolboxLogger.log_method
    def buildParcelFabric(self):
        in_parcel_fabric = os.path.join(self.inspectionDataSource, self.PARCEL_FABRIC_PATH)
        arcpy.parcel.BuildParcelFabric(in_parcel_fabric, "MAXOF")
        ToolboxLogger.info("Parcel Fabric Built")
    
    @ToolboxLogger.log_method
    def createInspectionMap(self) :
        map = self.aprx.listMaps("Inspection")[0]
        layers = map.listLayers()
        for layer in layers :
            map.removeLayer(layer)
        
        tables = map.listTables()
        for table in tables :
            map.removeTable(table)

        in_parcel_fabric = os.path.join(self.inspectionDataSource, self.PARCEL_FABRIC_PATH)
        map.addDataFromPath(in_parcel_fabric)

        in_parcel_dataset = os.path.join(self.inspectionDataSource, self.PARCEL_DATASET)
        map.addDataFromPath(in_parcel_dataset)

        layers = map.listLayers()

        map.openView()
        self.aprx.save()

    @ToolboxLogger.log_method
    def execute(self) :
        self.createSurveyDataSource()
        self.createInspectionDataSource()
        self.appendParcelData()
        self.createParcelRecords()
        self.buildParcelFabric()
        self.createInspectionMap()