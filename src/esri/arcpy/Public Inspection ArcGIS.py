# -*- coding: utf-8 -*-
r""""""
__all__ = ['CalculateBoundariesTool', 'CalculateSpatialUnitBoundariesTool',
           'CaptureSignatureTool', 'SetupDataSourcesTool']
__alias__ = 'PublicInspectionArcGISPro'
from arcpy.geoprocessing._base import gptooldoc, gp, gp_fixargs
from arcpy.arcobjects.arcobjectconversion import convertArcObjectToPythonObject

# Tools
@gptooldoc('CalculateBoundariesTool_PublicInspectionArcGISPro', None)
def CalculateBoundariesTool():
    """CalculateBoundariesTool_PublicInspectionArcGISPro()"""
    from arcpy.geoprocessing._base import gp, gp_fixargs
    from arcpy.arcobjects.arcobjectconversion import convertArcObjectToPythonObject
    try:
        retval = convertArcObjectToPythonObject(gp.CalculateBoundariesTool_PublicInspectionArcGISPro(*gp_fixargs((), True)))
        return retval
    except Exception as e:
        raise e

@gptooldoc('CalculateSpatialUnitBoundariesTool_PublicInspectionArcGISPro', None)
def CalculateSpatialUnitBoundariesTool(legal_id=None):
    """CalculateSpatialUnitBoundariesTool_PublicInspectionArcGISPro(legal_id)

     INPUTS:
      legal_id (Cadena):
          Legal ID"""
    from arcpy.geoprocessing._base import gp, gp_fixargs
    from arcpy.arcobjects.arcobjectconversion import convertArcObjectToPythonObject
    try:
        retval = convertArcObjectToPythonObject(gp.CalculateSpatialUnitBoundariesTool_PublicInspectionArcGISPro(*gp_fixargs((legal_id,), True)))
        return retval
    except Exception as e:
        raise e

@gptooldoc('CaptureSignatureTool_PublicInspectionArcGISPro', None)
def CaptureSignatureTool(legal_id=None, party_name=None, neighbors_approvals=None):
    """CaptureSignatureTool_PublicInspectionArcGISPro(legal_id, party_name, neighbors_approvals)

     INPUTS:
      legal_id (Cadena):
          Legal ID
      party_name (Cadena):
          Party Name
      neighbors_approvals (Tabla de valores):
          Boundaries Approvals"""
    from arcpy.geoprocessing._base import gp, gp_fixargs
    from arcpy.arcobjects.arcobjectconversion import convertArcObjectToPythonObject
    try:
        retval = convertArcObjectToPythonObject(gp.CaptureSignatureTool_PublicInspectionArcGISPro(*gp_fixargs((legal_id, party_name, neighbors_approvals), True)))
        return retval
    except Exception as e:
        raise e

@gptooldoc('SetupDataSourcesTool_PublicInspectionArcGISPro', None)
def SetupDataSourcesTool(param0=None):
    """SetupDataSourcesTool_PublicInspectionArcGISPro(param0)

     INPUTS:
      param0 (Espacio de trabajo):
          Input FGDB"""
    from arcpy.geoprocessing._base import gp, gp_fixargs
    from arcpy.arcobjects.arcobjectconversion import convertArcObjectToPythonObject
    try:
        retval = convertArcObjectToPythonObject(gp.SetupDataSourcesTool_PublicInspectionArcGISPro(*gp_fixargs((param0,), True)))
        return retval
    except Exception as e:
        raise e


# End of generated toolbox code
del gptooldoc, gp, gp_fixargs, convertArcObjectToPythonObject