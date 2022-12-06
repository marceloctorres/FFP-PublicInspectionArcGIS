import arcpy
import shutil
import os
from PublicInspectionArcGIS.Utils import ToolboxLogger, Configuration
from PublicInspectionArcGIS.ArcpyDataAccess import ArcpyDataAccess

class SetupDataSourcesTool :
    def __init__(self, configuration, aprx, loadDataSourcePath) :
        self.TEMPORAL_ID_PATTERN = "temp_{}_id"
        self.TEMPORAL_NAME_PATTERN = "Temp {} ID"

        self.aprx = aprx
        self.loadDataSourcePath = loadDataSourcePath
        self.folder = self.aprx.homeFolder

        self.SURVEY_DATASET_NAME = configuration.getConfigKey("SURVEY_DATASET_NAME")
        self.INSPECTION_DATASET_NAME = configuration.getConfigKey("INSPECTION_DATASET_NAME")
        self.PARCEL_XML_PATH = configuration.getConfigKey("PARCEL_XML_PATH")
        self.LOAD_XML_PATH = configuration.getConfigKey("LOAD_XML_PATH")
        self.PARCEL_TYPE = configuration.getConfigKey("PARCEL_TYPE")
        self.PARCEL_RECORD_FIELD = configuration.getConfigKey("PARCEL_RECORD_FIELD")
        self.PARCEL_FABRIC_PATH = configuration.getConfigKey("PARCEL_FABRIC_PATH")
        self.PARCEL_DATASET = configuration.getConfigKey("PARCEL_DATASET")

        self.inspectionDataSource = os.path.join(self.folder, self.INSPECTION_DATASET_NAME)
        self.surveyDataSource = os.path.join(self.folder, self.SURVEY_DATASET_NAME)
        ToolboxLogger.info("Load Data Source:       {}".format(self.loadDataSourcePath))
        ToolboxLogger.info("Proyect File:           {}".format(aprx.filePath))
        ToolboxLogger.info("Survey Data Source:     {}".format(self.surveyDataSource))
        ToolboxLogger.info("Inspection Data Source: {}".format(self.inspectionDataSource))
        ToolboxLogger.info("xml workspace File:     {}".format(self.PARCEL_XML_PATH))
    
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
        result_in_count = int(result_in[0])

        if result_in_count != 0 :
            input_ds_fields = arcpy.ListFields(input_ds_path)
            output_ds_fields = arcpy.ListFields(output_ds_path)

            fix_rs_field_name = self.TEMPORAL_ID_PATTERN.format(input_ds.lower())
            nf = [x for x in output_ds_fields if x.name.lower() == fix_rs_field_name]
            if(len(nf) == 0):
                out_table = arcpy.management.AddField(output_ds_path, fix_rs_field_name, "GUID", field_alias= self.TEMPORAL_NAME_PATTERN.format(input_ds) , field_is_nullable = "NULLABLE")
                arcpy.management.AddIndex(output_ds_path, [fix_rs_field_name], "GUID_{}".format(fix_rs_field_name))
                ToolboxLogger.debug("Temp '{}' field added.".format(fix_rs_field_name))

                output_ds_fields = arcpy.ListFields(output_ds_path)

            fix_rs_field = [f for f in output_ds_fields if f.name == fix_rs_field_name][0]
            fieldMappings = arcpy.FieldMappings()

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
                        fm.outputField = output_field
                        fieldMappings.addFieldMap(fm)

            output = arcpy.management.Append(input_ds_path, output_ds_path, "NO_TEST", fieldMappings)
            result_out = arcpy.management.GetCount(output)
        else :
            result_out = []
            result_out.append('0')

        ToolboxLogger.info("Input Count: {} Output Count: {}".format(result_in[0], result_out[0]))
        ToolboxLogger.info("...'{}' Data Appended".format(input_ds))

    @ToolboxLogger.log_method
    def fixDatasetRelationships(self, dataset) :
        dataset_relationship_classes = [x for x in arcpy.Describe(dataset).children if x.datatype == "RelationshipClass" and x.cardinality != "ManyToMany"]
        relationship_classes_fixed = []

        for relationship_class in dataset_relationship_classes:
            origin_classnames = [x for x in relationship_class.originClassNames if not x.lower().__contains__("publicinspection")]
            origin_classname = origin_classnames[0] if origin_classnames else None
            if origin_classname :
                origin_classname_path = os.path.join(dataset, origin_classname)
                origin_classname_fields = arcpy.ListFields(origin_classname_path)
                fix_rs_fields = [f for f in origin_classname_fields if f.name == self.TEMPORAL_ID_PATTERN.format(origin_classname.lower())]
                fix_rs_field = fix_rs_fields[0] if fix_rs_fields else None
                if fix_rs_field :
                    ToolboxLogger.debug("Origin Classname '{}'.".format(origin_classname))
                    destination_classnames = relationship_class.destinationClassNames
                    origin_pk_name =[k[0] for k in relationship_class.originClassKeys if k[1] == "OriginPrimary"][0]
                    origin_fk_name =[k[0] for k in relationship_class.originClassKeys if k[1] == "OriginForeign"][0]
                    origin_registers = self.da.query(origin_classname, [origin_pk_name, fix_rs_field.name])
                    ToolboxLogger.debug("Origin register count = {}.".format(len(origin_registers)))
                    for destination_classname in destination_classnames:
                        ToolboxLogger.debug("Destination Classname '{}'.".format(destination_classname))

                        destination_registers = self.da.query(destination_classname)
                        relationship_classes_fixed.append(relationship_class)
                        ToolboxLogger.debug("Fixing Relationship '{}'.".format(relationship_class.name))

                        ToolboxLogger.debug("Destination register count = {}.".format(len(destination_registers)))
                        if len(destination_registers) > 0:

                            fixed_destination_records = 0 
                            destination_records = 0

                            for register in origin_registers:
                                fix_rs_value = register[fix_rs_field.name]
                                updated_registers_old = self.da.query(destination_classname, [origin_fk_name], "{} = '{}'".format(origin_fk_name, fix_rs_value))

                                self.da.update(destination_classname, [origin_fk_name], [register[origin_pk_name]], "{} = '{}'".format(origin_fk_name, fix_rs_value))
                                updated_registers = self.da.query(destination_classname, [origin_fk_name], "{} = '{}'".format(origin_fk_name, register[origin_pk_name]))

                                fixed_destination_records += len(updated_registers)
                                destination_records += len(updated_registers_old)
                            ToolboxLogger.debug("Destination fixing register count '{}'.".format(destination_records))
                            ToolboxLogger.debug("Destination fixed register count '{}'.".format(fixed_destination_records))
    
    @ToolboxLogger.log_method           
    def cleanFixRelationshipsData(self, dataset) :
        dataset_relationship_classes = [x for x in arcpy.Describe(dataset).children if x.datatype == "RelationshipClass" and x.cardinality != "ManyToMany"]

        for relationship_class in dataset_relationship_classes:
            ToolboxLogger.debug("Relationship '{}' fixed.".format(relationship_class.name))
            origin_classnames = [x for x in relationship_class.originClassNames if not x.lower().__contains__("publicinspection")]
            origin_classname = origin_classnames[0] if origin_classnames else None
            if origin_classname :
                origin_classname_path = os.path.join(dataset, origin_classname)

                origin_classname_fields = arcpy.ListFields(origin_classname_path)
                fix_rs_fields = [f for f in origin_classname_fields if f.name == self.TEMPORAL_ID_PATTERN.format(origin_classname.lower())]
                fix_rs_field = fix_rs_fields[0] if fix_rs_fields else None
                if fix_rs_field :
                    arcpy.management.DeleteField(origin_classname_path, fix_rs_field.name)
                    ToolboxLogger.debug("Temporal '{}' field deleted.".format(fix_rs_field.name))

            destination_classnames = relationship_class.destinationClassNames
            for destination_classname in destination_classnames :
                destination_classname_path = self.da.findTablePath(destination_classname)
                destination_classname_fields = arcpy.ListFields(destination_classname_path)
                fix_rs_fields = [f for f in destination_classname_fields if f.name == self.TEMPORAL_ID_PATTERN.format(destination_classname.lower())]
                fix_rs_field = fix_rs_fields[0] if fix_rs_fields else None
                if fix_rs_field :
                    null_fix_rs_fields = self.da.query(destination_classname, [fix_rs_field.name], "{} IS NULL".format(fix_rs_field.name))
                    if(len(null_fix_rs_fields) > 0) :
                        self.da.delete(destination_classname, filter = "{} IS NULL".format(fix_rs_field.name))
                    arcpy.management.DeleteField(destination_classname_path, fix_rs_field.name)
                    ToolboxLogger.debug("Temporal '{}' field deleted.".format(fix_rs_field.name))

    @ToolboxLogger.log_method
    def fixRelationships(self) :
        self.da = ArcpyDataAccess(self.inspectionDataSource)
        self.fixDatasetRelationships(self.inspectionDataSource)
        self.fixDatasetRelationships(os.path.join(self.inspectionDataSource, "Parcel"))
        self.fixDatasetRelationships(os.path.join(self.inspectionDataSource, "ReferenceObjects"))

        self.cleanFixRelationshipsData(self.inspectionDataSource)
        self.cleanFixRelationshipsData(os.path.join(self.inspectionDataSource, "Parcel"))
        self.cleanFixRelationshipsData(os.path.join(self.inspectionDataSource, "ReferenceObjects"))

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

        try :
            self.aprx.save()
        except Exception as e :
            ToolboxLogger.error(e)

    @ToolboxLogger.log_method
    def execute(self) :
        #self.createSurveyDataSource()
        #self.cleanInspectionMap()
        self.createInspectionDataSource()
        self.appendParcelData()
        self.fixRelationships()
        self.createParcelRecords()
        self.buildParcelFabric()
        self.createInspectionMap()
