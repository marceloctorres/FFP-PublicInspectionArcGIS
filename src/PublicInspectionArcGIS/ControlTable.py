import arcpy
import os
from arcpy import da
from PublicInspectionArcGIS.Utils import ToolboxLogger
from PublicInspectionArcGIS.ArcpyDataAccess import ArcpyDataAccess

from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.lib.units import inch

from reportlab.graphics.shapes import Drawing, Rect, String, Group, Line
from reportlab.graphics.widgets.markers import makeMarker



# estilo=getSampleStyleSheet()
# estilo.add(ParagraphStyle(name = "ejemplo",  alignment=TA_CENTER, fontSize=20,
#            fontName="Helvetica-BoldOblique"))


class tableroGeneral:
    PARCEL_TYPE = "SpatialUnit"
    SPATIAL_UNIT_NAME = PARCEL_TYPE
    SPATIAL_UNIT_ID_FIELD = "GlobalID"
    SPATIAL_UNIT_NAME_FIELD = "spatialunit_name"
    SPATIAL_UNIT_LEGAL_ID= "legal_id"
    SPATIAL_UNIT_BOUNDARY_NAME = "SpatialUnit_Boundary"
    SPATIAL_UNIT_FK_FIELD ="spatialunit_id"
    
    def __init__(self, inspectionDataPath) :
        self.inspectionDataSources = inspectionDataPath
        ToolboxLogger.info("Inspection Data Source: {}".format(self.inspectionDataSources))
        self.da = ArcpyDataAccess(self.inspectionDataSources)
    
    
    @ToolboxLogger.log_method
    def getdata(self) :
        story = []
        spatial_units = self.da.query(self.SPATIAL_UNIT_NAME, geometry=True) 
        p=format(len(spatial_units))
        
        c = canvas.Canvas("ControlTable.pdf", pagesize=A4)
        # c= SimpleDocTemplate('ControlTable1.pdf', pagesize=A4)
        c.setFillColorRGB(	40, 180, 99 )
        c.rect(18, 670, 180, 80,fill=True)
        c.drawImage("logot1.png", 25, 685,width=50, height=40)
        c.setFont("Times-Roman", 19)
        c.setFillColorRGB(0.7, 0, 0.7)
        c.drawString(155, 720,p)
        c.drawString(95, 700,"Rightholders")
        c.drawString(95, 680,"Registered")
        
        c.setFillColorRGB(0.6, 0, 0.8)
        c.rect(208, 670, 180, 80,fill=True)
        c.drawImage("logot2.png", 215, 685,width=50, height=40)
        c.setFont("Times-Roman", 19)
        c.setFillColorRGB(1, 0, 0)
        c.drawString(340, 720,"a")
        c.drawString(292, 700,"Spatialunits")
        c.drawString(292, 680,"Surveyed")
        
        c.setFillColorRGB(1.1, 0, 1.8)
        c.rect(400, 670, 180, 80,fill=True )
        c.drawImage("logot3.png", 410, 685,width=50, height=40)
        c.setFont("Times-Roman", 19)
        c.setFillColorRGB(1, 0, 0)
        c.drawString(532, 720,"a")
        c.drawString(492, 700,"Hectares")
        c.drawString(492, 680,"Covered")




        c.rect(18, 545, 180, 110)
       
        c.setFillColorRGB(1, 0, 0)
        c.rect(18, 450, 180, 80,fill=True)
        c.drawImage("logot4.png", 25, 470,width=50, height=40)
        c.setFont("Times-Roman", 19)
        c.setFillColorRGB(0.7, 0, 0.7)
        c.drawString(100, 500,"Smallest")
        c.drawString(95, 480,"Spatialunit")
        c.drawString(120, 460,"13151")

        c.setFillColorRGB(1, 0, 0)
        c.rect(208, 450, 180, 80,fill=True)
        c.drawImage("logot5.png", 215, 470,width=50, height=40)
        c.setFont("Times-Roman", 17)
        c.setFillColorRGB(0.7, 0, 0.7)
        c.drawString(325, 500,"Average")
        c.drawString(275, 480,"Spatialunit Size")
        c.drawString(330, 460,"0.8 has")
        
        
        c.setFillColorRGB(1, 0, 0)
        c.rect(400, 450, 180, 80,fill=True)
        c.drawImage("logot5.png", 215, 470,width=50, height=40)
        c.setFont("Times-Roman", 17)
        c.setFillColorRGB(0.7, 0, 0.7)
        c.drawString(325, 500,"Average")
        c.drawString(275, 480,"Spatialunit Size")
        c.drawString(330, 460,"0.8 has")
        # c.save()
        
        
        
        
        #EJEMPLO 08: Gráficos Circulares
        #==========
        from reportlab.graphics.charts.piecharts import Pie

        d = Drawing(300, 200)
        pc = Pie()
        pc.x = 65
        pc.y = 15
        pc.width = 120
        pc.height = 120
        pc.data = [50,20,10,19,1]
        pc.labels = ['Pending','In Progress','Approved','In Revision','titled']

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
        legend.x               = 370 
        legend.y               = 0 
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
        c=story.append(d)
        os.system('ControlTable.pdf')
        c.save()
    @ToolboxLogger.log_method
    def execute(self) :
        self.getdata()