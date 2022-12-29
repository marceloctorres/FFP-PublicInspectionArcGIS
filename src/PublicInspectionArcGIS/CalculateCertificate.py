
import arcpy
# import os
from arcpy import da
from PublicInspectionArcGIS.Utils import ToolboxLogger
from PublicInspectionArcGIS.ArcpyDataAccess import ArcpyDataAccess

from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

class CalculateCertificateTool:
    
    
    PARCEL_TYPE = "SpatialUnit"
    SPATIAL_UNIT_NAME = PARCEL_TYPE
    SPATIAL_UNIT_ID_FIELD = "GlobalID"
    SPATIAL_UNIT_NAME_FIELD = "spatialunit_name"
    SPATIAL_UNIT_LEGAL_ID= "legal_id"
    SPATIAL_UNIT_BOUNDARY_NAME = "SpatialUnit_Boundary"
    SPATIAL_UNIT_FK_FIELD ="spatialunit_id"
    
    BOUNDARY_NAME = "SpatialUnit_Boundary"
    BOUNDARY_ID_FIELD = "GlobalID"
    BOUNDARY_FK_FIELD = "boundary_id"
    
    APPROVAL_NAME = "Approval"
    APPROVAL_ID_FIELD = "GlobalID"
    APPROVAL_FK_FIELD = "party_id"
    
    RIGTH_NAME = "Right"
    RIGHT_ID_FIELD = "GlobalID"
    RIGHT_FK_FIELD = "right_id"

    PARTY_NAME = "Party"
    PARTY_ID_FIELD = "GlobalID"
    PARTY_FIRST_NAME="first_name"
    PARTY_LAST_NAME="last_name"
    PARTY_ID_NUMBER="id_number"
    PARTY_FK_FIELD = "party_id"
    
    APROVAL_NAME = "Party"
    APROVAL_ID_FIELD = "GlobalID"
    APROVAL_FIRST_NAME="first_name"
    APROVAL_LAST_NAME="last_name"
    APROVAL_ID_NUMBER="id_number"
    APROVAL_FK_FIELD = "party_id"

    
    def __init__(self, inspectionDataPath) :
        self.inspectionDataSources = inspectionDataPath
        ToolboxLogger.info("Inspection Data Source: {}".format(self.inspectionDataSources))
        self.da = ArcpyDataAccess(self.inspectionDataSources)
    
    
    @ToolboxLogger.log_method
    def getdata(self) :
        
        spatialUnit="{DD93CEAC-95DE-40E9-88DE-1B3E2B7C23A2}"
        # spatialUnit="{572A335E-F335-409D-B80B-703E27308CB1}"
        
        right = self.da.query(self.RIGTH_NAME, [self.RIGHT_ID_FIELD], ArcpyDataAccess.getWhereClause(self.SPATIAL_UNIT_FK_FIELD, spatialUnit))
        for rights in right:
            partie = self.da.query(self.PARTY_NAME, "*", ArcpyDataAccess.getWhereClause(self.RIGHT_FK_FIELD, rights[self.RIGHT_ID_FIELD]))
        for parties in partie:
            First_Name = parties[self.PARTY_FIRST_NAME]
            Last_Name = parties[self.PARTY_LAST_NAME]
            id_number = parties[self.PARTY_ID_NUMBER]
            Spatial = self.da.query(self.PARCEL_TYPE, "*", ArcpyDataAccess.getWhereClause(self.SPATIAL_UNIT_ID_FIELD, spatialUnit))
            for SpatialU in Spatial:
                spatialunit_name=SpatialU[self.SPATIAL_UNIT_NAME_FIELD]
                CadastralCertificate = SpatialU[self.SPATIAL_UNIT_LEGAL_ID]
             
    
            Namepdf= CadastralCertificate
            Name= First_Name 
            last = Last_Name 
            Document= id_number
            NameSpacial=spatialunit_name
            Location=""
            CadastralCertificates=CadastralCertificate
            RegistrationPage="123"
            contac = " Marlon Cadena "

            c = canvas.Canvas(Namepdf+".pdf")
            c.rect(10, 10, 575, 820)
            c.drawImage("logo.png", 20, 750,width=100, height=70)
            c.drawImage("logo1.png", 390, 775,width=190, height=45)
            c.setFont("Times-Roman", 18)
            c.drawString(220, 750,"Acta de Colindancia")
            c.setFont("Times-Roman", 11)
            c.rect(20, 655, 555, 80)
            c.drawString(40, 720,"Nobre del Interesado: "+ Name +" " +last)
            c.drawString(40, 700,"Documento: "+Document)
            c.drawString(40, 680,"Firma: ")
            c.drawString(340, 720,"Nombre del Predio: "+NameSpacial)
            c.drawString(340, 700,"Ubicación: "+Location)
            c.drawString(340, 680,"Cedula Catastral: "+CadastralCertificates)
            c.drawString(340, 660,"Folio de Matricula: "+RegistrationPage)
            c.drawImage("Firma.png", 80, 660,width=190, height=40)
            c.rect(20, 370, 555, 275)
            c.drawImage("Mapa.png", 22, 373,width=550, height=270)
            c.rect(20, 80, 555,275)
            c.setFont("Times-Roman", 10)
            c.drawString(22, 340,"Los abajo firmantes, como colindantes del predio objeto de levantamiento topográfico realizado en la fecha referida,manifiestan que han ")
            c.drawString(22, 320,"asistido y aprobado el procedimiento realizado por el topógrafo, y estan de acuerdo con los linderos señalados durante este procedimiento")
            
            bundaries = self.da.query(self.BOUNDARY_NAME, [self.BOUNDARY_FK_FIELD], ArcpyDataAccess.getWhereClause(self.SPATIAL_UNIT_FK_FIELD, spatialUnit))
            sa=0
            for bundarie in bundaries: 
                print( bundarie[self.BOUNDARY_FK_FIELD])
                aprovals = self.da.query(self.APPROVAL_NAME,"*", ArcpyDataAccess.getWhereClause(self.BOUNDARY_FK_FIELD, bundarie[self.BOUNDARY_FK_FIELD]))
                sa=sa+1 
                for aproval in aprovals:
                    print( aproval[self.PARTY_ID_FIELD])
                    print( aproval[self.APPROVAL_FK_FIELD])
                    partiesa = self.da.query(self.PARTY_NAME,"*", ArcpyDataAccess.getWhereClause(self.PARTY_ID_FIELD, aproval[self.APPROVAL_FK_FIELD]))
                
                    for partiesas in partiesa:
                        if partiesas[self.PARTY_FIRST_NAME]==Name:
                            print("no")
                        else:    
                            
                            if sa==1:
                                
                                c.setFont("Times-Roman", 10)
                                c.drawString(30, 280,"Nobre del Interesado: "+ partiesas[self.PARTY_FIRST_NAME] + partiesas[self.PARTY_LAST_NAME])
                                c.drawString(260, 280,"Documento: "+partiesas[self.PARTY_ID_NUMBER])
                                c.drawString(30, 260,"Nombre del Predio: "+NameSpacial)
                                c.drawString(360, 260,"Firma: ")
                                c.drawImage("Firma.png", 390, 240,width=180, height=40)
                                  
                              
                            if sa==2:
                                c.setFont("Times-Roman", 10)
                                c.drawString(30, 235,"Nobre del Interesado: "+ partiesas[self.PARTY_FIRST_NAME] + partiesas[self.PARTY_LAST_NAME])
                                c.drawString(260, 235,"Documento: "+partiesas[self.PARTY_ID_NUMBER])
                                c.drawString(30, 215,"Nombre del Predio: "+NameSpacial)
                                c.drawString(360, 215,"Firma: ")
                                c.drawImage("Firma.png", 390, 195,width=180, height=40)
                                  
                            if sa==3:
                                c.setFont("Times-Roman", 10)
                                c.drawString(30, 190,"Nobre del Interesado: "+ partiesas[self.PARTY_FIRST_NAME] + partiesas[self.PARTY_LAST_NAME])
                                c.drawString(260, 190,"Documento: "+partiesas[self.PARTY_ID_NUMBER])
                                c.drawString(30, 170,"Nombre del Predio: "+NameSpacial)
                                c.drawString(360, 170,"Firma: ")
                                c.drawImage("Firma.png", 390, 150,width=180, height=40)
                            if sa==4:
                                c.setFont("Times-Roman", 10)
                                c.drawString(30, 145,"Nobre del Interesado: "+ partiesas[self.PARTY_FIRST_NAME] + partiesas[self.PARTY_LAST_NAME])
                                c.drawString(260, 145,"Documento: "+partiesas[self.PARTY_ID_NUMBER])
                                c.drawString(30, 125,"Nombre del Predio: "+NameSpacial)
                                c.drawString(360, 125,"Firma: ")
                                c.drawImage("Firma.png", 390, 105,width=180, height=40)
                            
            c.rect(20, 20, 555, 60)
            c.rect(20, 20, 278, 60)
            c.drawString(30, 68,"Firma del Porfesional : Kadaster")
            c.drawString(30, 30,"Fecha: ")
            c.drawString(302, 68,"Observaciones:")
            c.drawString(302, 50,"El contacto de la visita fue: "+contac)
            c.save()
    
    
    @ToolboxLogger.log_method
    def execute(self) :
        self.getdata()