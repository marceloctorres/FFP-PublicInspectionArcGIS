# -*- coding: utf-8 -*-
import arcpy
import os
from PublicInspectionArcGIS.Utils import ToolboxLogger, Configuration
from PublicInspectionArcGIS.ArcpyDataAccess import ArcpyDataAccess

class PublicInspectionTool(object) :

    def __init__(self, configuration : Configuration, aprx : arcpy.mp.ArcGISProject) :
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
        self.BOUNDARY_FK_FIELD = configuration.getConfigKey("BOUNDARY_FK_FIELD")
        self.BOUNDARY_STATE_FIELD = configuration.getConfigKey("BOUNDARY_STATE_FIELD")
        self.BOUNDARY_DESCRIPTION_FIELD = configuration.getConfigKey("BOUNDARY_DESCRIPTION_FIELD")

        self.RIGHT_NAME = configuration.getConfigKey("RIGHT_NAME")
        self.RIGHT_ID_FIELD = configuration.getConfigKey("RIGHT_ID_FIELD")
        self.RIGHT_FK_FIELD = configuration.getConfigKey("RIGHT_FK_FIELD")

        self.PARTY_NAME = configuration.getConfigKey("PARTY_NAME")
        self.PARTY_ID_FIELD = configuration.getConfigKey("PARTY_ID_FIELD")
        self.PARTY_FK_FIELD = configuration.getConfigKey("PARTY_FK_FIELD")
        self.PARTY_FIRST_NAME_FIELD = configuration.getConfigKey("PARTY_FIRST_NAME_FIELD")
        self.PARTY_LAST_NAME_FIELD = configuration.getConfigKey("PARTY_LAST_NAME_FIELD")

        self.APPROVAL_NAME = configuration.getConfigKey("APPROVAL_NAME")
        self.APPROVAL_ID_FIELD = configuration.getConfigKey("APPROVAL_ID_FIELD")
        self.APPROVAL_FK_FIELD = configuration.getConfigKey("APPROVAL_FK_FIELD")
        self.APPROVAL_DATE_FIELD = configuration.getConfigKey("APPROVAL_DATE_FIELD")
        self.APPROVAL_IS_APPROVED_FIELD = configuration.getConfigKey("APPROVAL_IS_APPROVED_FIELD")

        self.APPROVAL_SIGNATURE_NAME =configuration.getConfigKey("APPROVAL_SIGNATURE_NAME")
        self.APPROVAL_SIGNATURE_ID_FIELD = configuration.getConfigKey("APPROVAL_SIGNATURE_ID_FIELD")
        self.APPROVAL_SIGNATURE_FK_FIELD = configuration.getConfigKey("APPROVAL_SIGNATURE_FK_FIELD")
        self.APPROVAL_SIGNATURE_ATTACH_NAME = configuration.getConfigKey("APPROVAL_SIGNATURE_ATTACH_NAME")
        self.APPROVAL_SIGNATURE_ATTACH_ATT_NAME_FIELD = configuration.getConfigKey("APPROVAL_SIGNATURE_ATTACH_ATT_NAME_FIELD")

        self.inspectionDataSource = os.path.join(self.folder, self.INSPECTION_DATASET_NAME)
        self.da = ArcpyDataAccess(self.inspectionDataSource)

    def get_maptable(self, table_name):
        map = self.aprx.listMaps(self.INSPECTION_MAP)[0]
        search_tables = [l for l in map.listTables() if l.name == table_name]
        return search_tables[0] if len(search_tables) > 0 else None

    def get_maplayer(self, layer_name):
        map = self.aprx.listMaps(self.INSPECTION_MAP)[0]
        search_layers = [l for l in map.listLayers() if l.name == layer_name]
        return search_layers[0] if len(search_layers) > 0 else None

    def get_spatialunits(self, fields="*", filter=None, geometry=False) :
        return self.da.search(self.SPATIAL_UNIT_NAME, fields, filter, geometry)

    def get_boundaries(self, fields="*", filter=None, geometry=False) :
        return self.da.search(self.BOUNDARY_NAME, fields, filter, geometry)

    def get_spatialunits_boundaries(self, fields="*", filter=None) :
        return self.da.search(self.SPATIAL_UNIT_BOUNDARY_NAME, fields, filter)

    def get_rights(self, fields="*", filter=None) :
        return self.da.search(self.RIGHT_NAME, fields, filter)

    def get_parties(self, fields="*", filter=None) :
        return self.da.search(self.PARTY_NAME, fields, filter)

    def get_approvals(self, fields="*", filter=None) :
        return self.da.search(self.APPROVAL_NAME, fields, filter)

    def get_aprprovalsignatures(self, fields="*", filter=None) :
        return self.da.search(self.APPROVAL_SIGNATURE_NAME, fields, filter)

    def insert_boundaries(self, fields, values) :
        return self.da.insert(self.BOUNDARY_NAME, fields, values)

    def insert_spatialunits_boundaries(self, fields, values) :
        return self.da.insert(self.SPATIAL_UNIT_BOUNDARY_NAME, fields, values)

    def insert_approvalsignatures(self, fields, values) :
        return self.da.insert(self.APPROVAL_SIGNATURE_NAME, fields, values)

    def insert_approvals(self, fields, values) :
        return self.da.insert(self.APPROVAL_NAME, fields, values)

    def update_approvals(self, fields, values, filter) :
        self.da.update(self.APPROVAL_NAME, fields=fields, values=values, filter=filter)

    def update_boundaries(self, fields, values, filter) :
        self.da.update(self.BOUNDARY_NAME, fields=fields, values=values, filter=filter)

    @ToolboxLogger.log_method
    def add_approvals(self, spatialunit, boundary):
        rights = self.get_rights(fields=[self.RIGHT_ID_FIELD], 
            filter="{} = '{}'".format(self.SPATIAL_UNIT_FK_FIELD, spatialunit[self.SPATIAL_UNIT_ID_FIELD]))
        for right in rights:
            parties = self.get_parties(fields=[self.PARTY_ID_FIELD],
                filter = ArcpyDataAccess.getWhereClause(self.RIGHT_FK_FIELD, right[self.RIGHT_ID_FIELD]))
            for party in parties:
                approvals = self.get_approvals(fields=[self.APPROVAL_ID_FIELD], 
                    filter = ArcpyDataAccess.getWhereClause([self.BOUNDARY_FK_FIELD, self.PARTY_FK_FIELD], [boundary[self.BOUNDARY_ID_FIELD], party[self.PARTY_ID_FIELD]]))
                if len(approvals) < 1 :
                    approval = self.add_approval(boundary, party)
                    self.add_approvalsignature(approval)
    
    @ToolboxLogger.log_method
    def add_approvalsignature(self, approval) :
        values = []
        value = tuple([approval[self.APPROVAL_ID_FIELD]])
        values.append(value)

        signatures = self.insert_approvalsignatures([self.APPROVAL_FK_FIELD], values)
        signature = signatures[0] if signatures else None
        ToolboxLogger.debug("{} {}".format(self.APPROVAL_SIGNATURE_NAME, approval[self.APPROVAL_SIGNATURE_ID_FIELD] if signature else ""))
        return signature

    @ToolboxLogger.log_method
    def add_approval(self, boundary, party):
        values = []
        value = tuple([boundary[self.BOUNDARY_ID_FIELD], party[self.PARTY_ID_FIELD]])
        values.append(value)

        approvals = self.insert_approvals([self.BOUNDARY_FK_FIELD, self.PARTY_FK_FIELD], values)
        approval = approvals[0] if approvals else None
        ToolboxLogger.debug("{} {}".format(self.APPROVAL_NAME, approval[self.APPROVAL_ID_FIELD] if boundary else ""))

        return approval

    @ToolboxLogger.log_method
    def set_approvals_by_spatialunit(self, spatialunit) :
        spatial_unit_id = spatialunit[self.SPATIAL_UNIT_ID_FIELD]
        spatial_units_boundaries = self.get_spatialunits_boundaries(filter="{} = '{}'".format(self.SPATIAL_UNIT_FK_FIELD, spatial_unit_id))
        if spatial_units_boundaries :
            boundaries_ids = [row[self.BOUNDARY_FK_FIELD] for row in spatial_units_boundaries]
            ToolboxLogger.debug("Boundary Ids: {}".format(len(boundaries_ids)))

            boundaries = self.get_boundaries(
                fields=[self.BOUNDARY_ID_FIELD], 
                filter=ArcpyDataAccess.getWhereClause(self.BOUNDARY_ID_FIELD, boundaries_ids))
            for boundary in boundaries:
                self.add_approvals(spatialunit, boundary)

    @ToolboxLogger.log_method
    def get_spatialunit_by_legal_id(self, legal_id):
        spatialunits = self.get_spatialunits(
            fields=[self.SPATIAL_UNIT_ID_FIELD],
            filter="{} = '{}'".format(self.SPATIAL_UNIT_LEGAL_ID_FIELD, legal_id))
        return spatialunits[0] if len(spatialunits) > 0 else None

    @ToolboxLogger.log_method
    def get_parties_by_spatialunit(self, spatialunit):
        spatialunit_id = spatialunit[self.SPATIAL_UNIT_ID_FIELD] if spatialunit else None
        if spatialunit_id:
            rights = self.get_rights(
                fields=[self.RIGHT_ID_FIELD],
                filter="{} = '{}'".format(self.SPATIAL_UNIT_FK_FIELD, spatialunit_id))
            right_ids = ["'{}'".format(right[self.RIGHT_ID_FIELD]) for right in rights]

            if right_ids:
                parties = self.get_parties(filter="{} IN ({})".format(self.RIGHT_FK_FIELD, ",".join(right_ids)))

                parties_props = []
                for party in parties:
                    party[self.PARTY_ID_FIELD] = party[self.PARTY_ID_FIELD].lower()
                    party_prop = {}
                    party_prop["id"] = party[self.PARTY_ID_FIELD]
                    party_prop["name"] = "{} {}".format(party[self.PARTY_FIRST_NAME_FIELD], party[self.PARTY_LAST_NAME_FIELD])
                    parties_props.append(party_prop)

                return parties_props
        return None

    @ToolboxLogger.log_method
    def get_adjacent_spatialunits(self, spatialunit):
        spatialunit_id = spatialunit[self.SPATIAL_UNIT_ID_FIELD] if spatialunit else None
        if spatialunit_id:
            spatialunits_boundaries = self.get_spatialunits_boundaries(
                fields=[self.BOUNDARY_FK_FIELD],
                filter="{} = '{}'".format(self.SPATIAL_UNIT_FK_FIELD, spatialunit_id))
            boundary_ids = ["'{}'".format(row[self.BOUNDARY_FK_FIELD]) for row in spatialunits_boundaries]

            if boundary_ids:
                spatialunits_boundaries = self.get_spatialunits_boundaries(
                    fields=[self.SPATIAL_UNIT_FK_FIELD],
                    filter="{} IN ({})".format(self.BOUNDARY_FK_FIELD, ",".join(boundary_ids)))
                spatialunit_ids = ["'{}'".format(row[self.SPATIAL_UNIT_FK_FIELD]) for row in spatialunits_boundaries]

                if spatialunit_ids:
                    spatialunits = self.get_spatialunits(
                        fields=[self.SPATIAL_UNIT_ID_FIELD, self.SPATIAL_UNIT_LEGAL_ID_FIELD, self.SPATIAL_UNIT_NAME_FIELD],
                        filter="{} IN ({})".format(self.SPATIAL_UNIT_ID_FIELD, ",".join(spatialunit_ids)))
                    return [sp for sp in spatialunits if sp[self.SPATIAL_UNIT_ID_FIELD] != spatialunit[self.SPATIAL_UNIT_ID_FIELD]]
        return None

    @ToolboxLogger.log_method
    def get_boundaries_by_spatialunit(self, spatialunit) :
        spatialunit_id = spatialunit[self.SPATIAL_UNIT_ID_FIELD] if spatialunit else None
        if spatialunit_id:
            spatialunits_boundaries = self.get_spatialunits_boundaries(
                fields=[self.BOUNDARY_FK_FIELD],
                filter="{} = '{}'".format(self.SPATIAL_UNIT_FK_FIELD, spatialunit_id))
            boundary_ids = ["'{}'".format(row[self.BOUNDARY_FK_FIELD]) for row in spatialunits_boundaries]

            if boundary_ids:
                boundaries = self.get_boundaries(
                    fields=[self.BOUNDARY_ID_FIELD, self.BOUNDARY_DESCRIPTION_FIELD],
                    filter="{} IN ({})".format(self.BOUNDARY_ID_FIELD, ",".join(boundary_ids)))
                return boundaries
        return None
       
    @ToolboxLogger.log_method
    def get_neighboring_parties(self, spatialunit) :
        neighboring_spatialunits = self.get_adjacent_spatialunits(spatialunit)
        neighboring_parties = []
        if neighboring_spatialunits :
            for neighboring_spatialunit in neighboring_spatialunits:
                neighboring_parties.extend(self.get_parties_by_spatialunit(neighboring_spatialunit))
        return neighboring_parties

    @ToolboxLogger.log_method
    def get_neighboring_approvals(self, spatialunit) :

        parties = self.get_neighboring_parties(spatialunit)
        parties_id = ["'{}'".format(party["id"]) for party in parties]

        boundaries = self.get_boundaries_by_spatialunit(spatialunit)
        boundaries_id = ["'{}'".format(boundary[self.BOUNDARY_ID_FIELD]) for boundary in boundaries]

        approvals = self.get_approvals(
            fields=[self.APPROVAL_ID_FIELD, self.APPROVAL_IS_APPROVED_FIELD, self.PARTY_FK_FIELD, self.BOUNDARY_FK_FIELD],
            filter="{} IN ({}) AND {} IN ({})".format(self.PARTY_FK_FIELD, ",".join(parties_id), self.BOUNDARY_FK_FIELD, ",".join(boundaries_id)))

        for a in approvals:
            approval_parties = [p for p in parties if p["id"] == a[self.PARTY_FK_FIELD].lower()]
            approval_boundaries = [b for b in boundaries if b[self.BOUNDARY_ID_FIELD] == a[self.BOUNDARY_FK_FIELD]]
            if approval_parties:
                a["party_name"] = approval_parties[0]["name"]
            if approval_boundaries:
                a["boundary_description"] = approval_boundaries[0][self.BOUNDARY_DESCRIPTION_FIELD]
    
        return approvals

    @ToolboxLogger.log_method
    def get_approvals_by_spatialunit(self, spatialunit) : 
        parties = self.get_parties_by_spatialunit(spatialunit)
        parties_id = ["'{}'".format(party["id"]) for party in parties]
        approvals = self.get_approvals(
            fields=[self.APPROVAL_ID_FIELD, self.APPROVAL_IS_APPROVED_FIELD, self.PARTY_FK_FIELD, self.BOUNDARY_FK_FIELD],
            filter="{} IN ({})".format(self.PARTY_FK_FIELD, ",".join(parties_id)))
        return approvals






