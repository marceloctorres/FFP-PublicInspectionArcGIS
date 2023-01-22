# -*- coding:utf-8 -*-
import arcpy
import os
from PublicInspectionArcGIS.Utils import ToolboxLogger, Configuration
from PublicInspectionArcGIS.ArcpyDataAccess import ArcpyDataAccess
from PublicInspectionArcGIS.PublicInspection import PublicInspection

from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.lib.units import inch

from reportlab.graphics.shapes import Drawing, Rect, String, Group, Line
from reportlab.graphics.widgets.markers import makeMarker
# from reportlab.lib.utils import ImageReader

class CalculateDashboard(PublicInspection):
    
    def __init__(self, configuration : Configuration, aprx : arcpy.mp.ArcGISProject,legal_id:str= None) :
        super().__init__(configuration, aprx)
        self.legal_id=legal_id
    
    
    @ToolboxLogger.log_method
    def getdata(self) :


        PDF_path=os.path.join(self.folder,"Dashboard",'Dashboard.pdf')
        doc = SimpleDocTemplate(PDF_path, pagesize=A4)
        story = []
        estilo = getSampleStyleSheet()


        # EJEMPLO 01: Dibujando alguna forma y texto
        # ==========
        d = Drawing(400, 200)

        # spatial_units = self.da.query(self.SPATIAL_UNIT_NAME, geometry=True) 
        partys = self.da.query(self.PARTY_NAME, "*")
        RightholdersRegisteredp=format(len(partys))

        d.add(String(100,220, 'Dashboard ', fontSize=38, fillColor=colors.black))
        # frame 1
        r =(Rect(-70, 80, 180, 100, fillColor=colors.lightsalmon))
        r.strokeColor = colors.lightsalmon  # otra forma de agregar propiedades
        r.strokeWidth = 3
        d.add(r)
        d.add(String(30,140, RightholdersRegisteredp, fontSize=18, fillColor=colors.black))
        d.add(String(10,120, 'Rightholders', fontSize=18, fillColor=colors.black))
        d.add(String(10,100, 'Registered', fontSize=18, fillColor=colors.black))
        
        Boundarys = self.da.query(self.BOUNDARY_NAME, "*")
        Surveye=0
        for Boundary in Boundarys:
            if Boundary[self.BOUNDARY_STATE_FIELD]=="Approved":
                Surveyeds = self.da.query(self.SPATIAL_UNIT_BOUNDARY_NAME, "*", ArcpyDataAccess.getWhereClause(self.BOUNDARY_FK_FIELD,  Boundary[self.BOUNDARY_ID_FIELD]))
                for Surveyed in Surveyeds:
                    Spatialunits = self.da.query(self.SPATIAL_UNIT_NAME, "*", ArcpyDataAccess.getWhereClause(self.SPATIAL_UNIT_ID_FIELD,  Surveyed[self.SPATIAL_UNIT_FK_FIELD]))
                    for Spatialunit in Spatialunits:
                        if Spatialunit:
                            Surveye= Surveye+1

        # frame 2
        r =(Rect(126, 80, 180, 100, fillColor=colors.violet))
        r.strokeColor = colors.violet  # otra forma de agregar propiedades
        r.strokeWidth = 3
        d.add(r)
        d.add(String(226,140, "{} ".format(Surveye), fontSize=18, fillColor=colors.black))
        d.add(String(206,120, 'Spatialunits', fontSize=18, fillColor=colors.black))
        d.add(String(206,100, 'Surveyed', fontSize=18, fillColor=colors.black))

        # frame 3
        r =(Rect(326, 80, 180, 100, fillColor=colors.aquamarine))
        r.strokeColor = colors.aquamarine  # otra forma de agregar propiedades
        r.strokeWidth = 3
        d.add(r)
        d.add(String(446,140, '0', fontSize=18, fillColor=colors.black))
        d.add(String(426,120, 'Hectares', fontSize=18, fillColor=colors.black))
        d.add(String(426,100, 'Covered', fontSize=18, fillColor=colors.black))

        story.append(d)

        #EJEMPLO 02: Gráficos Circulares
        #==========
        from reportlab.graphics.charts.piecharts import Pie
        Boundarys = self.da.query(self.BOUNDARY_NAME, "*")
        Approved=0
        In_Process=0
        No_Processed=0
        Rejected=0
        for Boundary in Boundarys:
            if Boundary[self.BOUNDARY_STATE_FIELD]=="Approved":
                Approved= Approved+1
            if Boundary[self.BOUNDARY_STATE_FIELD]=="In Process":
                In_Process=In_Process+1  
            if Boundary[self.BOUNDARY_STATE_FIELD]=="No Processed":
                No_Processed= No_Processed+1
            if Boundary[self.BOUNDARY_STATE_FIELD]=="Rejected":
                Rejected=Rejected+1  

        d = Drawing(-400, 50)
        pc = Pie()
        pc.x = 370
        pc.y = 30
        pc.width = 80
        pc.height = 80
        pc.data = [Approved,In_Process,No_Processed,Rejected]
        pc.labels = ['Approved', 'In Progress','No Progressed','Rejected']

        pc.slices.strokeWidth=0.5
        pc.slices[3].popout = 10
        pc.slices[3].strokeWidth = 2
        pc.slices[3].strokeDashArray = [2,2]
        pc.slices[3].labelRadius = 1.75
        pc.slices[3].fontColor = colors.red
        pc.sideLabels = 1  # Con 0 no se muestran líneas hacia las etiquetas
        #~ pc.slices.labelRadius = 0.65  # Para mostrar el texto dentro de las tajadas

        #Insertamos la legenda

        from reportlab.graphics.charts.legends import Legend
        legend = Legend() 
        legend.x               = 390 
        legend.y               = 20 
        legend.dx              = 8  
        legend.dy              = 8  
        legend.fontName        = 'Helvetica'  
        legend.fontSize        = 7  
        legend.boxAnchor       = 'n'  
        legend.columnMaximum   = 10  
        legend.strokeWidth     = 1  
        legend.strokeColor     = colors.black  
        legend.deltax          = 75  
        legend.deltay          = 10  
        legend.autoXPadding    = 5  
        legend.yGap            = 0  
        legend.dxTextSpace     = 5  
        legend.alignment       = 'right'  
        legend.dividerLines    = 1|2|4  
        legend.dividerOffsY    = 4.5  
        legend.subCols.rpad    = 30  

        #Insertemos nuestros propios colores
        colores  = [colors.blue, colors.red, colors.green, colors.yellow, colors.pink]
        for i, color in enumerate(colores): 
            pc.slices[i].fillColor = color
            
        legend.colorNamePairs  = [(
                                    pc.slices[i].fillColor, 
                                    (pc.labels[i][0:20], '%0.2f' % pc.data[i])
                                ) for i in range(len(pc.data))]

        d.add(pc) 
        d.add(legend)
        story.append(d) 
       
             
        #EJEMPLO 03: Gráfico de Barras
        #===========
        import pprint
        r = Rect(0, 0, 200, 100)
        pprint.pprint(r.getProperties())

        from reportlab.graphics.charts.barcharts import  HorizontalBarChart

        d = Drawing(400, 200)
         
        Male=0
        Female=0
        for party in partys:
            if party[self.PARTY_GENDER_FIELD]=="Male":
                Male= Male+1
            if party[self.PARTY_GENDER_FIELD]=="Female":
                Female=Female+1  
        data = [
                (Female,Male)
                ]
        bc =  HorizontalBarChart()
        bc.x = 140
        bc.y = 220
        bc.height = 85
        bc.width = 150
        bc.data = data
        bc.strokeColor = colors.black
        bc.valueAxis.valueMin = 0
        bc.valueAxis.valueMax = 50
        bc.valueAxis.valueStep = 5  #paso de distancia entre punto y punto
        bc.categoryAxis.labels.boxAnchor = 'ne'
        bc.categoryAxis.labels.dx = -8
        bc.categoryAxis.labels.dy = -2
        bc.categoryAxis.labels.angle = 30
        bc.categoryAxis.categoryNames = ['Male','Female']
        bc.groupSpacing = 10
        bc.barSpacing = 1
        #bc.categoryAxis.style = 'stacked'  # Una variación del gráfico
        d.add(bc)
        pprint.pprint(bc.getProperties())
        story.append(d)

        # EJEMPLO 05: Dibujando alguna forma y texto
        # ==========
        SpatialUnitSmallests = self.da.query(self.SPATIAL_UNIT_NAME, "*", ArcpyDataAccess.getWhereClause(self.SPATIAL_UNIT_ID_FIELD,  "{9E8EC63E-D162-42FE-B9FD-27DCDB987221}"))
        for SpatialUnitSmallest in SpatialUnitSmallests:
            UnitSmallest = SpatialUnitSmallest[self.SPATIAL_UNIT_SHAPE_AREA]
            UnitSmallest =UnitSmallest*100
        d = Drawing(400, 10)
        # frame 4
        r =(Rect(-70, 80, 180, 100, fillColor=colors.yellow))
        r.strokeColor = colors.yellow  # otra forma de agregar propiedades
        r.strokeWidth = 3
        d.add(r)
        d.add(String(30,140, 'Smallest', fontSize=18, fillColor=colors.black))
        d.add(String(13,120, 'Spatialunit', fontSize=18, fillColor=colors.black))
        d.add(String(-43,100, "{} ".format(UnitSmallest), fontSize=15, fillColor=colors.black))
        # frame 5
        r =(Rect(126, 80, 180, 100, fillColor=colors.aqua))
        r.strokeColor = colors.aqua  # otra forma de agregar propiedades
        r.strokeWidth = 3
        d.add(r)
        d.add(String(226,140, 'Average', fontSize=18, fillColor=colors.black))
        d.add(String(180,120, 'Spatialunit Size', fontSize=18, fillColor=colors.black))
        d.add(String(226,100, '0.8 has', fontSize=18, fillColor=colors.black))

        SpatialUnitUnitLargests = self.da.query(self.SPATIAL_UNIT_NAME, "*", ArcpyDataAccess.getWhereClause(self.SPATIAL_UNIT_ID_FIELD,  "{4FA0579E-5E66-4339-9520-02498A50BF07}"))
        for SpatialUnitUnitLargest in SpatialUnitUnitLargests:
            UnitLargest = SpatialUnitUnitLargest[self.SPATIAL_UNIT_SHAPE_AREA]
            UnitLargest =UnitLargest*100
        # frame 6
        r =(Rect(326, 80, 180, 100, fillColor=colors.coral))
        r.strokeColor = colors.coral  # otra forma de agregar propiedades
        r.strokeWidth = 3
        d.add(r)
        d.add(String(446,140, 'Largest', fontSize=18, fillColor=colors.black))
        d.add(String(424,120, 'Spatialunit', fontSize=18, fillColor=colors.black))
        d.add(String(356,100,"{}".format(UnitLargest), fontSize=15, fillColor=colors.black))

        story.append(d)

        doc.build(story)
        os.system(PDF_path)
        
    @ToolboxLogger.log_method
    def execute(self) :
        self.getdata()