import arcpy
import os
import shutil

PYT_PATHS = ["GenerateCertificateTool.pyt", "Public Inspection ArcGIS.pyt"]

for PYT_PATH in PYT_PATHS:
    folder_path = os.path.dirname(os.path.realpath(__file__))
    pyt_path = os.path.normpath(os.path.join(folder_path, PYT_PATH))
    pyt_folder_path, pyt_filename_ext = os.path.split(pyt_path)
    pyt_filename, ext = os.path.splitext(pyt_filename_ext)

    source_folder_path = os.path.join(pyt_folder_path, 'esri')
    target_folder_path = os.path.join(folder_path, 'esri')

    #try:
    existe = os.path.isfile(pyt_path)
    print("Existe: {}".format(existe))
    print('Inicia el proceso: (\"{}\")'.format(pyt_path))
    arcpy.gp.createtoolboxsupportfiles(pyt_path)

    if os.path.isdir(target_folder_path):
        print('{} ya existe'.format(target_folder_path))

        shutil.rmtree(target_folder_path)   
        print("Eliminado: '{}'".format(target_folder_path))

    shutil.move(source_folder_path, folder_path)
    print("Se movió '{}' a '{}'".format(source_folder_path, folder_path))

    toolboxes_path = os.path.join(target_folder_path, 'toolboxes')
    os.mkdir(toolboxes_path)
    print("Se creó '{}'".format(toolboxes_path))

    pyt_files = [x for x in os.listdir(pyt_folder_path) if x.__contains__(pyt_filename) and os.path.isfile(os.path.join(pyt_folder_path, x))]

    for f in pyt_files:
        shutil.copy(os.path.join(pyt_folder_path, f), toolboxes_path)
        print("Se copió '{}' a '{}'".format(f, toolboxes_path))

    #except Exception as e:
    #    print("Error: '{}'".format(e))