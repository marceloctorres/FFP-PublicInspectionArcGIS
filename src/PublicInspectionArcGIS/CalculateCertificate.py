
import arcpy
import os
from arcpy import da
from PublicInspectionArcGIS.Utils import ToolboxLogger, Configuration
from PublicInspectionArcGIS.ArcpyDataAccess import ArcpyDataAccess
from PublicInspectionArcGIS.PublicInspection import PublicInspection
from datetime import date
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

class CalculateCertificate(PublicInspection):
    
    def __init__(self, configuration : Configuration, aprx : arcpy.mp.ArcGISProject,legal_id:str= None,visitor_contact:str= None) :
        super().__init__(configuration, aprx)
        self.legal_id=legal_id
        self.visitor_contact=visitor_contact
    
    
    @ToolboxLogger.log_method
    def getdata(self) :
       
        image_path=os.path.join(self.folder,"img")
        image_path_firm=os.path.join(self.folder,"Signatures")
        SpatialUni = self.da.query(self.SPATIAL_UNIT_NAME, "*", ArcpyDataAccess.getWhereClause(self.SPATIAL_UNIT_LEGAL_ID_FIELD,  self.legal_id))
        for SpatialUnis in SpatialUni:
            right = self.da.query(self.RIGHT_NAME, [self.RIGHT_ID_FIELD], ArcpyDataAccess.getWhereClause(self.SPATIAL_UNIT_FK_FIELD, SpatialUnis[self.SPATIAL_UNIT_ID_FIELD]))
        for rights in right:
            partie = self.da.query(self.PARTY_NAME, "*", ArcpyDataAccess.getWhereClause(self.RIGHT_FK_FIELD, rights[self.RIGHT_ID_FIELD]))
        for parties in partie:
            id_firm=  parties[self.PARTY_ID_FIELD]
            First_Name = parties[self.PARTY_FIRST_NAME_FIELD]
            Last_Name = parties[self.PARTY_LAST_NAME_FIELD]
            id_number = parties[self.PARTY_ID_NUMBER_FIELD]
            Spatial = self.da.query(self.SPATIAL_UNIT_NAME, "*", ArcpyDataAccess.getWhereClause(self.SPATIAL_UNIT_LEGAL_ID_FIELD,  self.legal_id))
            for SpatialU in Spatial:
                spatialunit_name=SpatialU[self.SPATIAL_UNIT_NAME_FIELD]
                CadastralCertificate = SpatialU[self.SPATIAL_UNIT_LEGAL_ID_FIELD]
             
    
            Namepdf="{}.pdf".format(CadastralCertificate)
            Firmpdf="{}.png".format(id_firm) 
            Name= First_Name 
            last = Last_Name 
            Document= id_number
            NameSpacial=spatialunit_name  
            Location=""    
            CadastralCertificates=CadastralCertificate
            RegistrationPage="" 
  
            PDF_path=os.path.join(self.folder,"certificate",Namepdf)
            c = canvas.Canvas(PDF_path)
            c.rect(10, 10, 575, 820)
            c.drawImage(image_path+"/logo.png", 20, 750,width=200, height=70)
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
            c.drawImage(image_path_firm+"\\"+Firmpdf, 80, 660,width=190, height=40)
            c.rect(20, 370, 555, 275)
            c.drawImage(image_path+"/Mapa.png", 22, 373,width=550, height=270)
            c.rect(20, 80, 555,275)
            c.setFont("Times-Roman", 10)
            c.drawString(22, 340,"Los abajo firmantes, como colindantes del predio objeto de levantamiento topográfico realizado en la fecha referida,manifiestan que han ")
            c.drawString(22, 320,"asistido y aprobado el procedimiento realizado por el topógrafo, y estan de acuerdo con los linderos señalados durante este procedimiento")
            SpatialUni = self.da.query(self.SPATIAL_UNIT_NAME, "*", ArcpyDataAccess.getWhereClause(self.SPATIAL_UNIT_LEGAL_ID_FIELD,  self.legal_id))
            for SpatialUnis in SpatialUni:
                boundaries=self.get_boundaries_by_spatialunit(SpatialUnis)
                # bundaries = self.da.query(self.BOUNDARY_NAME, [self.BOUNDARY_FK_FIELD], ArcpyDataAccess.getWhereClause(self.SPATIAL_UNIT_FK_FIELD, SpatialUnis[self.SPATIAL_UNIT_ID_FIELD]))
                sa=0
            for boundary in boundaries: 
                aprovals = self.da.query(self.APPROVAL_NAME,"*", ArcpyDataAccess.getWhereClause(self.BOUNDARY_FK_FIELD, boundary[self.BOUNDARY_ID_FIELD]))
                sa=sa+1 
                for aproval in aprovals:
                    print( aproval[self.PARTY_ID_FIELD])
                    print( aproval[self.PARTY_FK_FIELD])
                    partiesa = self.da.query(self.PARTY_NAME,"*", ArcpyDataAccess.getWhereClause(self.PARTY_ID_FIELD, aproval[self.PARTY_FK_FIELD]))
                
                    for partiesas in partiesa:
                        if partiesas[self.PARTY_FIRST_NAME_FIELD]==Name:
                            print("")
                        else:    
                            
                            if sa==1:
                                
                                rights = self.da.query(self.RIGHT_NAME,"*", ArcpyDataAccess.getWhereClause(self.RIGHT_ID_FIELD, partiesas[self.RIGHT_FK_FIELD]))
                                for right in rights:
                                    spatialUnits = self.da.query(self.SPATIAL_UNIT_NAME,"*", ArcpyDataAccess.getWhereClause(self.SPATIAL_UNIT_ID_FIELD, right[self.SPATIAL_UNIT_FK_FIELD]))
                                for spatialUnit in spatialUnits:
                                    c.setFont("Times-Roman", 
                                              10)
                                    c.drawString(30, 280,"Nombre del Interesado: {} {}".format(partiesas[self.PARTY_FIRST_NAME_FIELD] , partiesas[self.PARTY_LAST_NAME_FIELD]))
                                    c.drawString(260, 280,"Documento: {}".format(partiesas[self.PARTY_ID_NUMBER_FIELD]))
                                    c.drawString(30, 260,"Nombre del Predio: {} ".format(spatialUnit[self.SPATIAL_UNIT_NAME_FIELD]))
                                    c.drawString(360, 260,"Firma: ")
                                    c.drawImage(image_path_firm+"\\{}.png".format(partiesas[self.PARTY_ID_FIELD]), 390, 255,width=180, height=40)
                                    
                              
                            if sa==2:
                                rights = self.da.query(self.RIGHT_NAME,"*", ArcpyDataAccess.getWhereClause(self.RIGHT_ID_FIELD, partiesas[self.RIGHT_FK_FIELD]))
                                for right in rights:
                                    spatialUnits = self.da.query(self.SPATIAL_UNIT_NAME,"*", ArcpyDataAccess.getWhereClause(self.SPATIAL_UNIT_ID_FIELD, right[self.SPATIAL_UNIT_FK_FIELD]))
                                for spatialUnit in spatialUnits:
                                    c.setFont("Times-Roman", 10)
                                    c.drawString(30, 235,"Nombre del Interesado: {} {}".format(partiesas[self.PARTY_FIRST_NAME_FIELD] , partiesas[self.PARTY_LAST_NAME_FIELD]))
                                    c.drawString(260, 235,"Documento: {}".format(partiesas[self.PARTY_ID_NUMBER_FIELD]))
                                    c.drawString(30, 215,"Nombre del Predio: {} ".format(spatialUnit[self.SPATIAL_UNIT_NAME_FIELD]))
                                    c.drawString(360, 215,"Firma: ")
                                    c.drawImage(image_path_firm+"\\{}.png".format(partiesas[self.PARTY_ID_FIELD]), 390, 210,width=180, height=40)
                                  
                            if sa==3:
                                rights = self.da.query(self.RIGHT_NAME,"*", ArcpyDataAccess.getWhereClause(self.RIGHT_ID_FIELD, partiesas[self.RIGHT_FK_FIELD]))
                                for right in rights:
                                    spatialUnits = self.da.query(self.SPATIAL_UNIT_NAME,"*", ArcpyDataAccess.getWhereClause(self.SPATIAL_UNIT_ID_FIELD, right[self.SPATIAL_UNIT_FK_FIELD]))
                                for spatialUnit in spatialUnits:
                                    c.setFont("Times-Roman", 10)
                                    c.drawString(30, 190,"Nombre del Interesado: {} {}".format(partiesas[self.PARTY_FIRST_NAME_FIELD] , partiesas[self.PARTY_LAST_NAME_FIELD]))
                                    c.drawString(260, 190,"Documento: {}".format(partiesas[self.PARTY_ID_NUMBER_FIELD]))
                                    c.drawString(30, 170,"Nombre del Predio:{} ".format(spatialUnit[self.SPATIAL_UNIT_NAME_FIELD]))
                                    c.drawString(360, 170,"Firma: ")
                                    c.drawImage(image_path_firm+"\\{}.png".format(partiesas[self.PARTY_ID_FIELD]), 390, 165,width=180, height=40)
                            if sa==4:
                                rights = self.da.query(self.RIGHT_NAME,"*", ArcpyDataAccess.getWhereClause(self.RIGHT_ID_FIELD, partiesas[self.RIGHT_FK_FIELD]))
                                for right in rights:
                                    spatialUnits = self.da.query(self.SPATIAL_UNIT_NAME,"*", ArcpyDataAccess.getWhereClause(self.SPATIAL_UNIT_ID_FIELD, right[self.SPATIAL_UNIT_FK_FIELD]))
                                for spatialUnit in spatialUnits:
                                    c.setFont("Times-Roman", 10)
                                    c.drawString(30, 145,"Nombre del Interesado: {} {}".format(partiesas[self.PARTY_FIRST_NAME_FIELD] , partiesas[self.PARTY_LAST_NAME_FIELD]))
                                    c.drawString(260, 145,"Documento: {}".format(partiesas[self.PARTY_ID_NUMBER_FIELD]))
                                    c.drawString(30, 125,"Nombre del Predio: {} ".format(spatialUnit[self.SPATIAL_UNIT_NAME_FIELD]))
                                    c.drawString(360, 130,"Firma: ")
                                    c.drawImage(image_path_firm+"\\{}.png".format(partiesas[self.PARTY_ID_FIELD]), 390, 125,width=180, height=40)
            today = date.today()               
            c.rect(20, 20, 555, 60)
            c.rect(20, 20, 278, 60)
            c.drawString(30, 68,"Firma del Porfesional : ")
            c.drawString(30, 30,"Fecha:  {}".format(today.day)+ "/{}".format(today.month)+"/{} ".format(today.year))
            c.drawString(302, 68,"Observaciones:")
            c.drawString(302, 30,"El contacto de la visita fue: "+ self.visitor_contact)
            c.save()
    
    
    @ToolboxLogger.log_method
    def execute(self) :
        self.getdata()