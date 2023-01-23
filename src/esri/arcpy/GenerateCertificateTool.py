# -*- coding: utf-8 -*-
r""""""
__all__ = ['GenerateCertificate']
__alias__ = 'GenerateCertificateTool'
from arcpy.geoprocessing._base import gptooldoc, gp, gp_fixargs
from arcpy.arcobjects.arcobjectconversion import convertArcObjectToPythonObject

# Tools
@gptooldoc('GenerateCertificate_GenerateCertificateTool', None)
def GenerateCertificate():
    """GenerateCertificate_GenerateCertificateTool()"""
    from arcpy.geoprocessing._base import gp, gp_fixargs
    from arcpy.arcobjects.arcobjectconversion import convertArcObjectToPythonObject
    try:
        retval = convertArcObjectToPythonObject(gp.GenerateCertificate_GenerateCertificateTool(*gp_fixargs((), True)))
        return retval
    except Exception as e:
        raise e


# End of generated toolbox code
del gptooldoc, gp, gp_fixargs, convertArcObjectToPythonObject