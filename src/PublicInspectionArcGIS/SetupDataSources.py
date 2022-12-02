import arcpy
import shutil
import os
from PublicInspectionArcGIS.Utils import ToolboxLogger
from PublicInspectionArcGIS.ArcpyDataAccess import ArcpyDataAccess

class SetupDataSourcesTool :
    SURVEY_DATASET_NAME = "survey.gdb"
    INSPECTION_DATASET_NAME = "inspection.gdb"
    PARCEL_XML_PATH = "XmlWorkspaceDocuments\\FFP-ParcelFabric.v2.xml"
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
        ToolboxLogger.info("Proyect File:           {}".format(aprx.filePath))
        ToolboxLogger.info("Load Data Source:       {}".format(self.loadDataSourcePath))
        ToolboxLogger.info("Survey Data Source:     {}".format(self.surveyDataSource))
        ToolboxLogger.info("Inspection Data Source: {}".format(self.inspectionDataSource))
    
    @ToolboxLogger.log_method
    def createSurveyDataSource(self):
        file_folder_path = os.path.dirname(os.path.realpath(__file__))
        xml_path = os.path.join(file_folder_path, self.LOAD_XML_PATH)
        arcpy.management.ExportXMLWorkspaceDocument(self.loadDataSourcePath, xml_path)
        ToolboxLogger.info("Load data Exported")

        if(os.path.exists(self.surveyDataSource)) :
            arcpy.Delete_management(self.surveyDataSource)

        arcpy.management.CreateFileGDB(self.folder, self.SURVEY_DATASET_NAME, "CURRENT")
        ToolboxLogger.info("Survey Dataset Created")
        arcpy.management.ImportXMLWorkspaceDocument(self.surveyDataSource, xml_path)
        ToolboxLogger.info("Survey Data Imported")

        arcpy.management.Delete(xml_path)        

    @ToolboxLogger.log_method
    def copySurveyDataSource(self) :
        if(os.path.exists(self.surveyDataSource)) :
            arcpy.Delete_management(self.surveyDataSource)

        shutil.copytree(self.loadDataSourcePath, self.surveyDataSource)
        ToolboxLogger.info("Survey Dataset Created")

    @ToolboxLogger.log_method
    def cleanInspectionMap(self) :
        map = self.aprx.listMaps("Inspection")[0]

        layers = [l for l in map.listLayers() if not l.isBasemapLayer]
        for layer in layers :
            map.removeLayer(layer)
        
        tables = map.listTables()
        for table in tables :
            map.removeTable(table)   
        ToolboxLogger.info("Inspection Map Cleaned")     

    @ToolboxLogger.log_method
    def createInspectionDataSource(self) :
        if(os.path.exists(self.inspectionDataSource)) :
            arcpy.Delete_management(self.inspectionDataSource)

        arcpy.management.CreateFileGDB(self.folder, self.INSPECTION_DATASET_NAME, "CURRENT")
        ToolboxLogger.info("Inspection Dataset Created")

        file_folder_path = os.path.dirname(os.path.realpath(__file__))
        xml_path = os.path.join(file_folder_path, self.PARCEL_XML_PATH)

        arcpy.management.ImportXMLWorkspaceDocument(self.inspectionDataSource, xml_path, "SCHEMA_ONLY")
        ToolboxLogger.info("Inspection Parcel Fabric Schema Imported")
    
    @ToolboxLogger.log_method
    def appendDataset(self, input_ds):
        ToolboxLogger.info("Appending '{}' Data...".format(input_ds))
        input_ds_path = os.path.join(self.loadDataSourcePath, input_ds)
        output_ds_path = os.path.join(self.inspectionDataSource, input_ds)

        ToolboxLogger.debug("Input:  {}".format(input_ds_path))
        ToolboxLogger.debug("Output: {}".format(output_ds_path))

        result_in = arcpy.management.GetCount(input_ds_path)

        if result_in != 0 :
            input_ds_fields = arcpy.ListFields(input_ds_path)
            output_ds_fields = arcpy.ListFields(output_ds_path)

            fix_rs_field_name = "{}_id".format(input_ds.lower())
            nf = [x for x in output_ds_fields if x.name.lower() == fix_rs_field_name]
            if(len(nf) == 0):
                ToolboxLogger.debug("Nooo! Existe el campo {}".format(fix_rs_field_name))
                out_table = arcpy.management.AddField(output_ds_path, fix_rs_field_name, "GUID", field_alias= "{} ID".format(input_ds) , field_is_nullable = "NULLABLE")
                arcpy.management.AddIndex(output_ds_path, [fix_rs_field_name], "GUID_{}".format(fix_rs_field_name))

                ToolboxLogger.debug("Nueva tabla: {}".format(out_table))
                output_ds_fields = arcpy.ListFields(output_ds_path)
            else:
                print("Existe el campo {}".format(fix_rs_field_name))

            field_names = [f.name for f in output_ds_fields]
            fix_rs_field = [f for f in output_ds_fields if f.name == fix_rs_field_name][0]
            ToolboxLogger.debug("Campos de salida {}".format(field_names))

            fieldMappings = arcpy.FieldMappings()
            fieldMappings.addTable(output_ds_path)

            for out_field in output_ds_fields:
                if out_field.type != "OID" and out_field.type != "Geometry":
                    if out_field.name == fix_rs_field_name :
                        gid_input_fields = [f for f in input_ds_fields if f.type.lower() == "globalid"]
                        input_field = gid_input_fields[0] if input_ds_fields else None
                        output_field = fix_rs_field
                    else :
                        input_fields = [f for f in input_ds_fields if f.name.lower() == out_field.name.lower()]
                        input_field = input_fields[0] if input_fields else None
                        output_field = out_field
                        
                    if input_field :
                        fm = arcpy.FieldMap()
                        fm.addInputField(input_ds_path, input_field.name)

                        ToolboxLogger.info("Input Field: {} Output Field: {}".format(input_field.name, output_field.name))
                        fm.outputField = output_field
                        fieldMappings.addFieldMap(fm)

            output = arcpy.management.Append(input_ds_path, output_ds_path, "NO_TEST", fieldMappings)
            result_out = arcpy.management.GetCount(output)
        else :
            result_out = 0

        ToolboxLogger.info("Input Count: {} Output Count: {}".format(result_in[0], result_out[0]))
        ToolboxLogger.info("...'{}' Data Appended".format(input_ds))

    def fixDatasetRelationships(self, dataset) :
        da = ArcpyDataAccess(self.inspectionDataSource)
        dataset_relationship_classes = [x for x in arcpy.Describe(dataset).children if x.datatype == "RelationshipClass"]
        for relationship_class in dataset_relationship_classes:

            origin_classnames = [x for x in relationship_class.originClassNames if not x.lower().__contains__("publicinspection")]
            origin_classname = origin_classnames[0] if origin_classnames else None
            if origin_classname :
                origin_classname_path = os.path.join(dataset, origin_classname)
                ToolboxLogger.debug("rsc = {} ---> ocs = {}".format(relationship_class.name, origin_classname))

                origin_classname_fields = arcpy.ListFields(origin_classname_path)
                fix_rs_fields = [f for f in origin_classname_fields if f.name == "{}_id".format(origin_classname.lower())]
                fix_rs_field = fix_rs_fields[0] if fix_rs_fields else None
                if fix_rs_field :
                    origin_registers = da.query(origin_classname, "*")
                    destination_class_names = relationship_class.destinationClassNames
                    origin_pk_name =[k[0] for k in relationship_class.originClassKeys if k[1] == "OriginPrimary"][0]
                    origin_fk_name =[k[0] for k in relationship_class.originClassKeys if k[1] == "OriginForeign"][0]
                    ToolboxLogger.debug("origin_pk_name = {}".format(origin_pk_name))
                    ToolboxLogger.debug("origin_fk_name = {}".format(origin_fk_name))

                    ToolboxLogger.debug("destination_class_names = {}".format(destination_class_names))
                    for register in origin_registers:
                        fix_rs_value = register[fix_rs_field.name]
                        for destination_classname in destination_class_names:
                            ToolboxLogger.debug("fix_rs_value = {}".format(fix_rs_value))
                            ToolboxLogger.debug("destination_classname = {}".format(destination_classname))
                            da.update(destination_classname, [origin_fk_name], [register[origin_pk_name]], "{} = '{}'".format(origin_fk_name, fix_rs_value))
                if fix_rs_field :
                    arcpy.management.DeleteField(origin_classname_path, fix_rs_field.name)

    def fixRelationships(self) :
        self.fixDatasetRelationships(self.inspectionDataSource)
        self.fixDatasetRelationships(os.path.join(self.inspectionDataSource, "Parcel"))
        self.fixDatasetRelationships(os.path.join(self.inspectionDataSource, "ReferenceObjects"))

    @ToolboxLogger.log_method
    def appendParcelData(self) :
        arcpy.env.workspace = self.loadDataSourcePath
        #arcpy.env.preserveGlobalIds = True

        featureClasses = arcpy.ListFeatureClasses()
        for input_fc in featureClasses:
            self.appendDataset(input_fc)

        tables = arcpy.ListTables()
        for input_tb in tables:
            self.appendDataset(input_tb)

    @ToolboxLogger.log_method
    def createParcelRecords(self) : 
        in_parcel_features = os.path.join(self.inspectionDataSource, self.PARCEL_TYPE)
        arcpy.parcel.CreateParcelRecords(in_parcel_features, self.PARCEL_RECORD_FIELD, "","FIELD") 
        ToolboxLogger.info("Parcel Records Created")

    @ToolboxLogger.log_method
    def buildParcelFabric(self):
        in_parcel_fabric_path = os.path.join(self.inspectionDataSource, self.PARCEL_FABRIC_PATH)
        arcpy.parcel.BuildParcelFabric(in_parcel_fabric_path, "MAXOF")
        ToolboxLogger.info("Parcel Fabric Built")
    
    @ToolboxLogger.log_method
    def createInspectionMap(self) :
        map = self.aprx.listMaps("Inspection")[0]

        in_parcel_fabric_path = os.path.join(self.inspectionDataSource, self.PARCEL_FABRIC_PATH)
        map.addDataFromPath(in_parcel_fabric_path)

        in_parcel_dataset = os.path.join(self.inspectionDataSource, self.PARCEL_DATASET)
        map.addDataFromPath(in_parcel_dataset)

        layers =  [l for l in map.listLayers() if not l.isBasemapLayer]
        for layer in layers :
            layer_file_path = os.path.join(self.folder, "{}.lyrx".format(layer.longName))
            exist = os.path.exists(layer_file_path)
            layer.visible = exist

            if exist :
                ToolboxLogger.info("Apply Symbology From Layer: {}.lyrx".format(layer.longName))
                arcpy.management.ApplySymbologyFromLayer(layer, layer_file_path, None, "DEFAULT")

                layer.updateConnectionProperties(layer.connectionProperties, layer.connectionProperties)
        
        if self.aprx.activeMap != map:
            map.openView()

        self.aprx.save()

    @ToolboxLogger.log_method
    def execute(self) :
        self.createSurveyDataSource()
        self.cleanInspectionMap()
        self.createInspectionDataSource()
        self.appendParcelData()
        self.fixRelationships()
        self.createParcelRecords()
        self.buildParcelFabric()
        self.createInspectionMap()
