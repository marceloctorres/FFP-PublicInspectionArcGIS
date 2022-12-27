import arcpy
import shutil
import os

from PublicInspectionArcGIS.Utils import ToolboxLogger, Configuration
from PublicInspectionArcGIS.ArcpyDataAccess import ArcpyDataAccess
from PublicInspectionArcGIS.PublicInspectionTool import PublicInspectionTool

class CalculateBoundariesTool(PublicInspectionTool):
    def __init__(self, configuration : Configuration, aprx : arcpy.mp.ArcGISProject) :
        super().__init__(configuration, aprx)
        self.GEOMETRY_FIELD = configuration.getConfigKey("GEOMETRY_FIELD")

        ToolboxLogger.info("Proyect File:           {}".format(aprx.filePath))
        ToolboxLogger.info("Inspection Data Source: {}".format(self.inspectionDataSource))
        ToolboxLogger.debug("Data Access Object:     {}".format(self.da))
    
    @ToolboxLogger.log_method
    def set_boundaries(self) :
        spatial_units = self.get_spatialunits(geometry=True)
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
                        boundary = self.add_boundary(intersect, "{} - {}".format(su0[self.SPATIAL_UNIT_NAME_FIELD], su1[self.SPATIAL_UNIT_NAME_FIELD]))
                        self.add_spatialunit_boundary(su0, boundary)
                        self.add_spatialunit_boundary(su1, boundary)

                        self.add_approvals(su0, boundary)
                        self.add_approvals(su1, boundary)
                    else :
                        ToolboxLogger.debug("NULL Geometry!")

            spatial_unit_id = su0[self.SPATIAL_UNIT_ID_FIELD]
            spatial_units_boundaries = self.get_spatialunits_boundaries(filter="{} = '{}'".format(self.SPATIAL_UNIT_FK_FIELD, spatial_unit_id))

            if spatial_units_boundaries :
                boundaries_ids = [row[self.BOUNDARY_FK_FIELD] for row in spatial_units_boundaries]
                ToolboxLogger.debug("Boundary Ids: {}".format(len(boundaries_ids)))

                related_boundaries = self.get_boundaries(fields=[self.BOUNDARY_ID_FIELD, self.GEOMETRY_FIELD], 
                    filter=ArcpyDataAccess.getWhereClause(self.BOUNDARY_ID_FIELD, boundaries_ids))
                
                not_null_related_boundaries = [g[self.GEOMETRY_FIELD] for g in related_boundaries if g[self.GEOMETRY_FIELD]]
                ToolboxLogger.debug("Boundary Geometries Length: {}".format(len(not_null_related_boundaries)))

                boundary_union = not_null_related_boundaries.pop(0)
                for boundary in not_null_related_boundaries :
                    boundary_union = boundary_union.union(boundary)
            
                geometry0_boundary = geometry.boundary()
                intersect = geometry0_boundary.difference(boundary_union)
                if intersect.length > 0 :
                    boundary = self.add_boundary(intersect, "{}".format(su0[self.SPATIAL_UNIT_NAME_FIELD]))
                    self.add_spatialunit_boundary(su0, boundary)
                    self.add_approvals(su0, boundary)
    
    @ToolboxLogger.log_method
    def add_boundary(self, geometry, description):
        values = []
        value = tuple([geometry, description])
        values.append(value)

        boundaries = self.insert_boundaries([self.GEOMETRY_FIELD, self.BOUNDARY_DESCRIPTION_FIELD], values)
        boundary = boundaries[0] if boundaries else None
        ToolboxLogger.debug("{} {}".format(self.BOUNDARY_NAME, boundary[self.BOUNDARY_ID_FIELD] if boundary else ""))

        return boundary

    @ToolboxLogger.log_method
    def add_spatialunit_boundary(self, spatial_unit, boundary):
        values = []
        value = tuple([spatial_unit["GlobalID"], boundary[self.BOUNDARY_ID_FIELD]])
        values.append(value)
        
        spatialunits_boundaries = self.insert_spatialunits_boundaries([self.SPATIAL_UNIT_FK_FIELD, self.BOUNDARY_FK_FIELD], values)
        spatialUnit_boundary = spatialunits_boundaries[0] if spatialunits_boundaries else None    
        return spatialUnit_boundary


    @ToolboxLogger.log_method
    def set_approvals(self) :
        spatialunits = self.get_spatialunits()
        for spatialunit in spatialunits:
            self.set_approvals_by_spatialunit(spatialunit)

    @ToolboxLogger.log_method
    def execute(self) :
        self.set_boundaries()
        self.set_approvals()
