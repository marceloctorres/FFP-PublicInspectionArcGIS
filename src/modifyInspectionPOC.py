import arcpy
import os

from PublicInspectionArcGIS.Utils import CONFIG_PATH, STREAM_HANDLER, ToolboxLogger, Configuration

workspace = "D:\mtorres\OneDrive - Esri NOSA\Documentos\ArcGIS\Projects\Modelo FFP\FFP Inspeccion Publica.gdb"
dataset = os.path.join(workspace, "Parcel")

arcpy.env.workspace = workspace 

ToolboxLogger.initLogger(handler_type=STREAM_HANDLER)
ToolboxLogger.setDebugLevel()

def populate_catalog_list(workspace):
    catalog_list = [] 

    for d in arcpy.Describe(workspace).children :
        if d.datatype == "FeatureDataset" :
            catalog_sub_list = populate_catalog_list(d.catalogPath)
            catalog_list += catalog_sub_list
        else :
            catalog_item = {}
            catalog_item["name"] = d.name 
            catalog_item["path"] = d.catalogPath
            catalog_list.append(catalog_item)
    return catalog_list

def find(catalog_list, name) :
    items = [x for x in catalog_list if x["name"] == name]
    item = items[0] if items else None
    return item

def execute(workspace):
    catalog_list = populate_catalog_list(workspace)
    path = find(catalog_list, "SpatialUnit")
    print(path)

    rscs = [x for x in arcpy.Describe(workspace).children if x.datatype == "RelationshipClass" and not x.isAttachmentRelationship]
    ToolboxLogger.debug("rscs = {}".format(len(rscs)))
    for rsc in rscs:
        ToolboxLogger.debug("--------------------------------------------------------------------------------------------------------------------------")
        ToolboxLogger.debug(rsc.name)
        ToolboxLogger.debug(rsc.catalogpath)
        ToolboxLogger.debug ("Backward Path Label: {}".format(rsc.backwardPathLabel))
        ToolboxLogger.debug ("Cardinality: {}".format(rsc.cardinality))
        ToolboxLogger.debug ("Class key: {}".format(rsc.classKey))
        ToolboxLogger.debug ("Destination Class Keys: {}".format(rsc.destinationClassKeys))
        ToolboxLogger.debug ("Destination Class Names: {}".format(rsc.destinationClassNames))
        ToolboxLogger.debug ("Forward Path Label: {}".format(rsc.forwardPathLabel)) 
        ToolboxLogger.debug ("isAttachmentRelationship: {}".format(rsc.isAttachmentRelationship)) 
        ToolboxLogger.debug ("Is Attributed: {}".format(rsc.isAttributed))
        ToolboxLogger.debug ("Is Composite: {}".format(rsc.isComposite)) 
        ToolboxLogger.debug ("Is Reflexive: {}".format(rsc.isReflexive))
        ToolboxLogger.debug ("Key Type: {}".format(rsc.keyType))
        ToolboxLogger.debug ("Notification Direction: {}".format(rsc.notification))
        ToolboxLogger.debug ("Origin Class Keys: {}".format(rsc.originClassKeys))
        ToolboxLogger.debug ("Origin Class Names: {}".format(rsc.originClassNames))
        ToolboxLogger.debug ("relationshipRules: {}".format(rsc.relationshipRules))
        ToolboxLogger.debug ("splitPolicy: {}".format(rsc.splitPolicy))

        ocs = [x for x in rsc.originClassNames if not x.lower().__contains__("publicinspection")]
        ToolboxLogger.debug("ocs = {}".format(len(ocs)))

        if(len(ocs)) > 0:
            oks = []
            for oc in ocs:
                fs = arcpy.ListFields(oc)
                nf = [x for x in fs if x.name.lower() == "{}_id".format(oc.lower())]
                if(len(nf) == 0):
                    print("Nooo! Existe el campo {}_id".format(oc.lower()))
                    arcpy.management.AddField(oc, "{}_id".format(oc.lower()), "GUID", field_alias= "{} ID".format(oc) , field_is_nullable = "NULLABLE")
                else:
                    print("Existe el campo {}_id".format(oc.lower()))
                oks.append("{}_id".format(oc.lower()))

                print("Siguiente...")


            origin_table = ocs[0]
            destination_table = rsc.destinationClassNames[0]
            out_relationship_class = os.path.join(workspace, "{}_1".format(rsc.name))
            cardinality = "ONE_TO_ONE" if rsc.cardinality == "OneToOne" else "ONE_TO_MANY" if rsc.cardinality == "OneToMany" else "MANY_TO_MANY"
            message_direction = "FORWARD" if rsc.notification == "Forward" else "BACKWARD" if rsc.notification == "Backward" else "BOTH" if rsc.notification == "Backward" else "NONE"
            relationship_type = "COMPOSITE" if rsc.isComposite else "SIMPLE"
            attributed = "ATTRIBUTED" if rsc.isAttributed else "NONE"
            foreing_key = [x[0] for x in rsc.originClassKeys if x[1] == "OriginForeign"]
            forward_label = rsc.forwardPathLabel
            backward_label = rsc.backwardPathLabel
            origin_primary_key = oks[0]
            origin_foreign_key = foreing_key[0]

            ToolboxLogger.debug("origin_table = {}".format(origin_table))
            ToolboxLogger.debug("destination_table = {}".format(destination_table))
            ToolboxLogger.debug("out_relationship_class = {}".format(out_relationship_class))
            ToolboxLogger.debug("relationship_type = {}".format("{}".format(relationship_type)))
            ToolboxLogger.debug("forward_label = {}".format("{}".format(forward_label)))
            ToolboxLogger.debug("backward_label = {}".format("{}".format(backward_label)))
            ToolboxLogger.debug("message_direction = {}".format("{}".format(message_direction)))
            ToolboxLogger.debug("cardinality = {}".format(cardinality))
            ToolboxLogger.debug("attributed = {}".format(attributed))
            ToolboxLogger.debug("origin_primary_key = {}".format("{}".format(origin_primary_key)))
            ToolboxLogger.debug("origin_foreign_key = {}".format(origin_foreign_key))

            arcpy.management.CreateRelationshipClass(origin_table = origin_table, 
                destination_table = destination_table,
                out_relationship_class = out_relationship_class, 
                relationship_type = relationship_type, 
                forward_label = destination_table, 
                backward_label = origin_table, 
                message_direction = message_direction, 
                cardinality = cardinality,
                attributed = attributed, 
                origin_primary_key = origin_primary_key, 
                origin_foreign_key = origin_foreign_key)

execute(workspace)
execute(dataset)

    

