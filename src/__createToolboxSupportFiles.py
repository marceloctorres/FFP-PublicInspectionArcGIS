import arcpy
import os
import shutil

PYT_PATHS = [ "Public Inspection ArcGIS.pyt", "GenerateCertificateTool.pyt"]

def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)

for PYT_PATH in PYT_PATHS:
    folder_path = os.path.dirname(os.path.realpath(__file__))
    pyt_path = os.path.normpath(os.path.join(folder_path, PYT_PATH))
    pyt_folder_path, pyt_filename_ext = os.path.split(pyt_path)
    pyt_filename, ext = os.path.splitext(pyt_filename_ext)

    source_folder_path = os.path.join(pyt_folder_path, 'esri')
    target_folder_path = os.path.join(folder_path, 'PublicInspectionArcGIS\esri')

    try:
        exist = os.path.isfile(pyt_path)
        if exist :
            print('Inicia el proceso: (\"{}\")'.format(pyt_path))
            arcpy.gp.createtoolboxsupportfiles(pyt_path)
            copytree(source_folder_path, target_folder_path)

            toolboxes_path = os.path.join(target_folder_path, 'toolboxes')
            if not os.path.exists(toolboxes_path):
                os.mkdir(toolboxes_path)
                print("Se creó '{}'".format(toolboxes_path))

            pyt_files = [x for x in os.listdir(pyt_folder_path) if x.__contains__(pyt_filename) and os.path.isfile(os.path.join(pyt_folder_path, x))]

            for f in pyt_files:
                shutil.copy(os.path.join(pyt_folder_path, f), toolboxes_path)
                print("Se copió '{}' a '{}'".format(f, toolboxes_path))

    except Exception as e:
        print("Error: '{}'".format(e))