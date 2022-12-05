import arcpy
import shutil
import os
from PublicInspectionArcGIS.Utils import ToolboxLogger
from PublicInspectionArcGIS.ArcpyDataAccess import ArcpyDataAccess

class CalculateBoundariesTool:
    def __init__(self, configuration, aprx) :
        self.aprx = aprx
        self.folder = self.aprx.homeFolder
        self.INSPECTION_DATASET_NAME = configuration.getConfigKey("INSPECTION_DATASET_NAME")
        self.GEOMETRY_FIELD = configuration.getConfigKey("GEOMETRY_FIELD")

        self.SPATIAL_UNIT_NAME = configuration.getConfigKey("SPATIAL_UNIT_NAME")
        self.SPATIAL_UNIT_ID_FIELD = configuration.getConfigKey("SPATIAL_UNIT_ID_FIELD")
        self.SPATIAL_UNIT_NAME_FIELD = configuration.getConfigKey("SPATIAL_UNIT_NAME_FIELD")
        self.SPATIAL_UNIT_BOUNDARY_NAME = configuration.getConfigKey("SPATIAL_UNIT_BOUNDARY_NAME")
        self.SPATIAL_UNIT_FK_FIELD = configuration.getConfigKey("SPATIAL_UNIT_FK_FIELD")
        
        self.BOUNDARY_NAME = configuration.getConfigKey("BOUNDARY_NAME")
        self.BOUNDARY_ID_FIELD = configuration.getConfigKey("BOUNDARY_ID_FIELD")
        self.BOUNDARY_DESCRIPTION_FIELD = configuration.getConfigKey("BOUNDARY_DESCRIPTION_FIELD")
        self.BOUNDARY_FK_FIELD = configuration.getConfigKey("BOUNDARY_FK_FIELD")

        self.RIGTH_NAME = configuration.getConfigKey("RIGTH_NAME")
        self.RIGHT_ID_FIELD = configuration.getConfigKey("RIGHT_ID_FIELD")
        self.RIGHT_FK_FIELD = configuration.getConfigKey("RIGHT_FK_FIELD")

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

        ToolboxLogger.info("Proyect File:           {}".format(aprx.filePath))
        ToolboxLogger.info("Inspection Data Source: {}".format(self.inspectionDataSource))

    
    @ToolboxLogger.log_method
    def getBoundaries(self) :
        spatial_units = self.da.query(self.SPATIAL_UNIT_NAME, geometry=True)
        ToolboxLogger.info("SpatialUnits count {}".format(len(spatial_units)))

        while(len(spatial_units) > 0) :
            su0 = spatial_units.pop(0)
            ToolboxLogger.debug("Spatial Unit 0: {}".format(su0[self.SPATIAL_UNIT_ID_FIELD]))
            geometry = su0[self.GEOMETRY_FIELD]

            ToolboxLogger.info("Spatial count: {}".format(len(spatial_units))) 
            for su1 in spatial_units:
                geometry1 = su1[self.GEOMETRY_FIELD]
                equals = geometry.equals(geometry1)
                disjoint = geometry.disjoint(geometry1)
                if not equals and not disjoint:
                    ToolboxLogger.debug("Spatial Unit 1: {}".format(su1[self.SPATIAL_UNIT_ID_FIELD]))
                    intersect = geometry.intersect(geometry1, 2)
                    ToolboxLogger.debug("Boundary Length: {}".format(intersect.length))

                    if intersect.length > 0:
                        boundary = self.addBoundary(intersect, "{} - {}".format(su0[self.SPATIAL_UNIT_NAME_FIELD], su1[self.SPATIAL_UNIT_NAME_FIELD]))
                        self.addSpatialUnitBoundary(su0, boundary)
                        self.addSpatialUnitBoundary(su1, boundary)

                        self.addApprovals(su0, boundary)
                        self.addApprovals(su1, boundary)
                    else :
                        ToolboxLogger.debug("NULL Geometry!")

            spatial_unit_id = su0[self.SPATIAL_UNIT_ID_FIELD]
            spatial_units_boundaries = self.da.query(self.SPATIAL_UNIT_BOUNDARY_NAME, "*", "{} = '{}'".format(self.SPATIAL_UNIT_FK_FIELD, spatial_unit_id))

            if spatial_units_boundaries :
                boundaries_ids = [row[self.BOUNDARY_FK_FIELD] for row in spatial_units_boundaries]
                ToolboxLogger.debug("Boundary Ids: {}".format(len(boundaries_ids)))

                related_boundaries = self.da.query(self.BOUNDARY_NAME, [self.BOUNDARY_ID_FIELD, self.GEOMETRY_FIELD], 
                    ArcpyDataAccess.getWhereClause(self.BOUNDARY_ID_FIELD, boundaries_ids))
                not_null_related_boundaries = [g[self.GEOMETRY_FIELD] for g in related_boundaries if g[self.GEOMETRY_FIELD]]
                ToolboxLogger.debug("Boundary Geometries Length: {}".format(len(not_null_related_boundaries)))

                boundary_union = not_null_related_boundaries.pop(0)
                for boundary in not_null_related_boundaries :
                    boundary_union = boundary_union.union(boundary)
            
                geometry0_boundary = geometry.boundary()
                intersect = geometry0_boundary.difference(boundary_union)
                if intersect.length > 0 :
                    boundary = self.addBoundary(intersect, "{}".format(su0[self.SPATIAL_UNIT_NAME_FIELD]))
                    self.addSpatialUnitBoundary(su0, boundary)
                    self.addApprovals(su0, boundary)
    
    @ToolboxLogger.log_method
    def addBoundary(self, geometry, description):
        values = []
        value = tuple([geometry, description])
        values.append(value)

        boundaries = self.da.add(self.BOUNDARY_NAME, [self.GEOMETRY_FIELD, self.BOUNDARY_DESCRIPTION_FIELD], values)
        boundary = boundaries[0] if boundaries else None
        ToolboxLogger.debug("{} {}".format(self.BOUNDARY_NAME, boundary[self.BOUNDARY_ID_FIELD] if boundary else ""))

        return boundary

    @ToolboxLogger.log_method
    def addSpatialUnitBoundary(self, spatial_unit, boundary):
        values = []
        value = tuple([spatial_unit["GlobalID"], boundary[self.BOUNDARY_ID_FIELD]])
        values.append(value)
        
        spatialunits_boundaries = self.da.add(self.SPATIAL_UNIT_BOUNDARY_NAME, [self.SPATIAL_UNIT_FK_FIELD, self.BOUNDARY_FK_FIELD], values)
        spatialUnit_boundary = spatialunits_boundaries[0] if spatialunits_boundaries else None    
        return spatialUnit_boundary

    @ToolboxLogger.log_method
    def addApprovals(self, spatialUnit, boundary):
        rights = self.da.query(self.RIGTH_NAME, [self.RIGHT_ID_FIELD], ArcpyDataAccess.getWhereClause(self.SPATIAL_UNIT_FK_FIELD, spatialUnit[self.SPATIAL_UNIT_ID_FIELD]))
        for right in rights:
            parties = self.da.query(self.PARTY_NAME, [self.PARTY_ID_FIELD], ArcpyDataAccess.getWhereClause(self.RIGHT_FK_FIELD, right[self.RIGHT_ID_FIELD]))
            for party in parties:
                approvals = self.da.query(self.APPROVAL_NAME, [self.APPROVAL_ID_FIELD], 
                    ArcpyDataAccess.getWhereClause([self.BOUNDARY_FK_FIELD, self.PARTY_FK_FIELD], [boundary[self.BOUNDARY_ID_FIELD], party[self.PARTY_ID_FIELD]]))
                if len(approvals) < 1 :
                    approval = self.addApproval(boundary, party)
                    self.addApprovalSignature(approval)
    
    @ToolboxLogger.log_method
    def addApprovalSignature(self, approval) :
        values = []
        value = tuple([approval[self.APPROVAL_ID_FIELD]])
        values.append(value)

        signatures = self.da.add(self.APPROVAL_SIGNATURE_NAME, [self.APPROVAL_FK_FIELD], values)
        signature = signatures[0] if signatures else None
        ToolboxLogger.debug("{} {}".format(self.APPROVAL_SIGNATURE_NAME, approval[self.APPROVAL_SIGNATURE_ID_FIELD] if signature else ""))
        return signature

    @ToolboxLogger.log_method
    def addApproval(self, boundary, party):
        values = []
        value = tuple([boundary[self.BOUNDARY_ID_FIELD], party[self.PARTY_ID_FIELD]])
        values.append(value)

        approvals = self.da.add(self.APPROVAL_NAME, [self.BOUNDARY_FK_FIELD, self.PARTY_FK_FIELD], values)
        approval = approvals[0] if approvals else None
        ToolboxLogger.debug("{} {}".format(self.APPROVAL_NAME, approval[self.APPROVAL_ID_FIELD] if boundary else ""))

        return approval

    @ToolboxLogger.log_method
    def getApprovals(self) :
        spatialunits = self.da.query(self.SPATIAL_UNIT_NAME)
        for spatialunit in spatialunits:
            spatial_unit_id = spatialunit[self.SPATIAL_UNIT_ID_FIELD]
            spatial_units_boundaries = self.da.query(self.SPATIAL_UNIT_BOUNDARY_NAME, "*", "{} = '{}'".format(self.SPATIAL_UNIT_FK_FIELD, spatial_unit_id))

            if spatial_units_boundaries :
                boundaries_ids = [row[self.BOUNDARY_FK_FIELD] for row in spatial_units_boundaries]
                ToolboxLogger.debug("Boundary Ids: {}".format(len(boundaries_ids)))

                boundaries = self.da.query(self.BOUNDARY_NAME, [self.BOUNDARY_ID_FIELD], ArcpyDataAccess.getWhereClause(self.BOUNDARY_ID_FIELD, boundaries_ids))
                for boundary in boundaries:
                    self.addApprovals(spatialunit, boundary)

    @ToolboxLogger.log_method
    def execute(self) :
        self.getBoundaries()
        self.getApprovals()
