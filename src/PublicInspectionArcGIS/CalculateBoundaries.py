import arcpy
import os

from PublicInspectionArcGIS.Utils import ToolboxLogger, Configuration
from PublicInspectionArcGIS.ArcpyDataAccess import ArcpyDataAccess
from PublicInspectionArcGIS.PublicInspection import PublicInspection

class CalculateBoundaries(PublicInspection):
    def __init__(self, configuration : Configuration, aprx : arcpy.mp.ArcGISProject) :
        super().__init__(configuration, aprx)
        self.GEOMETRY_FIELD = configuration.getConfigKey("GEOMETRY_FIELD")
        self.legal_id = None

        ToolboxLogger.info("Proyect File:           {}".format(aprx.filePath))
        ToolboxLogger.info("Inspection Data Source: {}".format(self.inspectionDataSource))
        ToolboxLogger.debug("Data Access Object:     {}".format(self.da))
    
    @ToolboxLogger.log_method
    def update_point_type(self, points, boundary) :
        self.fail_boundaries = []
        boundary_geometry = boundary[self.GEOMETRY_FIELD]
        boundary_first_point = boundary_geometry.firstPoint
        boundary_last_point = boundary_geometry.lastPoint
        print("Points count: {}".format(len(points)))
        count = 0
        for point in points :
            point_geometry = point[self.GEOMETRY_FIELD]
            point_buffer = point_geometry.buffer(5 / 111135)
            
            intersect_first_point = point_buffer.intersect(boundary_first_point, 1)
            intersect_last_point = point_buffer.intersect(boundary_last_point, 1)
            if (intersect_first_point.firstPoint or intersect_first_point.lastPoint or intersect_last_point.firstPoint or intersect_last_point.lastPoint):
                ToolboxLogger.debug("Point '{}' is an Anchor".format(point[self.POINTS_ID_FIELD]))
                count += 1
                if point[self.POINTS_TYPE_FIELD] == "Vertex" :
                    self.update_points(fields=[self.POINTS_TYPE_FIELD], values=["Anchor"], filter="{} = '{}'".format(self.POINTS_ID_FIELD, point[self.POINTS_ID_FIELD]))
                    point[self.POINTS_TYPE_FIELD] = "Anchor"
                    ToolboxLogger.debug("Point '{}' updated".format(point[self.POINTS_ID_FIELD]))
                if count == 2:
                    ToolboxLogger.debug("Break search")
                    break

    @ToolboxLogger.log_method
    def set_spatialunit_boundaries(self, su0, spatial_units, points) :
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
                        spatialunits_boundaries = self.get_spatialunits_boundaries(
                            filter="{0} = '{1}' or {0} = '{2}'".format(
                                self.SPATIAL_UNIT_FK_FIELD, su0[self.SPATIAL_UNIT_ID_FIELD], su1[self.SPATIAL_UNIT_ID_FIELD])
                            )
                        boundaries_ids = [boundary[self.BOUNDARY_FK_FIELD] for boundary in spatialunits_boundaries]
                        spatialunits_boundaries_meet_criteria = [boundary for boundary in spatialunits_boundaries if boundaries_ids.count(boundary[self.BOUNDARY_FK_FIELD]) == 2]

                        if len(spatialunits_boundaries_meet_criteria) == 2 \
                                and spatialunits_boundaries_meet_criteria[0][self.BOUNDARY_FK_FIELD] == spatialunits_boundaries_meet_criteria[1][self.BOUNDARY_FK_FIELD] :
                            ToolboxLogger.debug("Boundary by Spatial Unit: {}".format(spatialunits_boundaries_meet_criteria))
                            boundary = self.get_boundaries(filter="{} = '{}'".format(self.BOUNDARY_ID_FIELD, spatialunits_boundaries_meet_criteria[0][self.BOUNDARY_FK_FIELD]))[0]
                            boundary[self.GEOMETRY_FIELD] = intersect
                            self.update_boundaries(fields=[self.GEOMETRY_FIELD], values=[intersect], filter="{} = '{}'".format(self.BOUNDARY_ID_FIELD, boundary[self.BOUNDARY_ID_FIELD]))
                            ToolboxLogger.debug("Boundary '{}' updated".format(boundary[self.BOUNDARY_ID_FIELD]))
                        else :
                            boundary = self.add_boundary(intersect, "{} - {}".format(su0[self.SPATIAL_UNIT_NAME_FIELD], su1[self.SPATIAL_UNIT_NAME_FIELD]))
                            self.add_spatialunit_boundary(su0, boundary)
                            self.add_spatialunit_boundary(su1, boundary)

                            self.add_approvals(su0, boundary)
                            self.add_approvals(su1, boundary)
                        self.update_point_type(points, boundary)
                    else :
                        ToolboxLogger.debug("NULL Geometry!")

            spatial_unit_id = su0[self.SPATIAL_UNIT_ID_FIELD]
            spatial_units_boundaries = self.get_spatialunits_boundaries(
                filter="{} = '{}'".format(self.SPATIAL_UNIT_FK_FIELD, spatial_unit_id))

            if spatial_units_boundaries :
                spatialunits_boundaries_id = [row[self.BOUNDARY_FK_FIELD] for row in spatial_units_boundaries]
                ToolboxLogger.debug("Boundary Ids: {}".format(len(spatialunits_boundaries_id)))

                spatialunits_boundaries = self.get_spatialunits_boundaries(
                    filter=ArcpyDataAccess.getWhereClause(self.BOUNDARY_FK_FIELD, spatialunits_boundaries_id))
                boundaries_ids = [boundary[self.BOUNDARY_FK_FIELD] for boundary in spatialunits_boundaries]

                boundaries_ids_meet_criteria = [id for id in boundaries_ids if boundaries_ids.count(id) == 2]
                spatialunits_boundaries_meet_criteria = [boundary for boundary in spatialunits_boundaries if boundary[self.BOUNDARY_FK_FIELD] in boundaries_ids_meet_criteria]

                related_boundaries_ids = [boundary[self.BOUNDARY_FK_FIELD] for boundary in spatialunits_boundaries_meet_criteria]
                related_boundaries = self.get_boundaries(filter=ArcpyDataAccess.getWhereClause(self.BOUNDARY_ID_FIELD, related_boundaries_ids), geometry=True)

                not_null_related_boundaries = [g[self.GEOMETRY_FIELD] for g in related_boundaries if g[self.GEOMETRY_FIELD]]
                ToolboxLogger.debug("Boundary Geometries Length: {}".format(len(not_null_related_boundaries)))

                boundary_union = not_null_related_boundaries.pop(0)
                for boundary in not_null_related_boundaries :
                    boundary_union = boundary_union.union(boundary)
            
                geometry0_boundary = geometry.boundary()
                intersect = geometry0_boundary.difference(boundary_union)
                if intersect.length > 0 :
                    boundaries_ids_meet_criteria = [id for id in boundaries_ids if boundaries_ids.count(id) == 1]
                    spatialunits_boundaries_meet_criteria = [boundary for boundary in spatialunits_boundaries if boundary[self.BOUNDARY_FK_FIELD] in boundaries_ids_meet_criteria]
                    if len(spatialunits_boundaries_meet_criteria) == 1:
                        ToolboxLogger.debug("Boundary by Spatial Unit: {}".format(spatialunits_boundaries_meet_criteria))
                        boundaries = self.get_boundaries(
                            filter="{} = '{}'".format(self.BOUNDARY_ID_FIELD, spatialunits_boundaries_meet_criteria[0][self.BOUNDARY_FK_FIELD]),
                            geometry=True)
                        boundary = boundaries[0]
                        print(boundary[self.GEOMETRY_FIELD])
                        boundary[self.GEOMETRY_FIELD] = intersect

                        self.update_boundaries(fields=[self.GEOMETRY_FIELD], values=[intersect], filter="{} = '{}'".format(self.BOUNDARY_ID_FIELD, boundary[self.BOUNDARY_ID_FIELD]))
                        ToolboxLogger.debug("Boundary '{}' updated".format(boundary[self.BOUNDARY_ID_FIELD]))
                    else :
                        boundary = self.add_boundary(intersect, "{}".format(su0[self.SPATIAL_UNIT_NAME_FIELD]))
                        self.add_spatialunit_boundary(su0, boundary)
                        self.add_approvals(su0, boundary)
                    self.update_point_type(points, boundary)
   
    @ToolboxLogger.log_method
    def set_boundaries(self) :
        points = self.get_points(geometry=True)
        if self.legal_id is None :
            self.update_points(fields=[self.POINTS_TYPE_FIELD], values=["Vertex"])

            spatial_units = self.get_spatialunits(geometry=True)
            ToolboxLogger.info("SpatialUnits count {}".format(len(spatial_units)))
            ToolboxLogger.info("Points count {}".format(len(points)))

            while(len(spatial_units) > 0) :
                su0 = spatial_units.pop(0)
                self.set_spatialunit_boundaries(su0, spatial_units, points)
        else :
            layer = arcpy.management.MakeFeatureLayer(
                in_features=os.path.join(self.inspectionDataSource, self.SPATIAL_UNIT_NAME),
                out_layer="{}_layer".format(self.SPATIAL_UNIT_NAME),
                where_clause="{} = '{}'".format(self.SPATIAL_UNIT_LEGAL_ID_FIELD, self.legal_id),
                workspace="in_memory")
            
            selected_units = arcpy.management.SelectLayerByLocation(
                in_layer=os.path.join(self.inspectionDataSource, self.SPATIAL_UNIT_NAME),
                overlap_type="WITHIN_A_DISTANCE", 
                select_features=layer[0],
                search_distance="5 Meters",
                selection_type="NEW_SELECTION")

            FIDSet = arcpy.Describe(selected_units[0]).FIDset
            records = [int(FID) for FID in FIDSet.split(";")] if FIDSet else []
            spatial_units = self.get_spatialunits(
                filter="{} IN ({})".format("OBJECTID", ",".join([str(record) for record in records])),
                geometry=True)

            su0 = [x for x in spatial_units if x[self.SPATIAL_UNIT_LEGAL_ID_FIELD] == self.legal_id][0]
            spatial_units = [x for x in spatial_units if x[self.SPATIAL_UNIT_LEGAL_ID_FIELD] != self.legal_id]

            self.set_spatialunit_boundaries(su0, spatial_units, points)
   
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
        #self.set_approvals()
