import math
import pb

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QPen, QBrush, QColor
from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsItemGroup, QGraphicsEllipseItem

WIDTH = 800  # Initial window width (pixels)
HEIGHT = 450  # Initial window height (pixels)
TRAJECTORY_WIDTH = 100
PLANE_CIRCLE_SIZE = 500
CONFLICT_CIRCLE_SIZE = pb.d

N_POINT_TRAJECTORY = pb.T

# constant colors
FLIGHT_COLOR = "blue"
TRAJECTORY_COLOR = "black"
CONFLICT_CIRCLE_COLOR = QColor(0,255,0,100)

# creating the brushes
FLIGHT_BRUSH = QBrush(QColor(FLIGHT_COLOR))
CONFLICT_CIRCLE_BRUSH = QBrush(CONFLICT_CIRCLE_COLOR)

class PanZoomView(QtWidgets.QGraphicsView):
    """An interactive view that supports Pan and Zoom functions"""

    def __init__(self, scene):
        super().__init__(scene)
        # enable anti-aliasing
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        # enable drag and drop of the view
        self.setDragMode(self.ScrollHandDrag)

    def wheelEvent(self, event):
        """Overrides method in QGraphicsView in order to zoom it when mouse scroll occurs"""
        factor = math.pow(1.001, event.angleDelta().y())
        self.zoom_view(factor)

    @QtCore.pyqtSlot(int)
    def zoom_view(self, factor):
        """Updates the zoom factor of the view"""
        self.setTransformationAnchor(self.AnchorUnderMouse)
        super().scale(factor, factor)


class RadarView(QtWidgets.QWidget):

    def __init__(self,flights):
        super().__init__()

        # Settings
        self.setWindowTitle("Resolution de conflits aeriens")
        self.resize(WIDTH, HEIGHT)
        self.currentPoint = 0
        self.flights = flights

        # create components
        root_layout = QtWidgets.QVBoxLayout(self)
        self.scene = QtWidgets.QGraphicsScene()
        self.scene.addRect(0,0,10,10)
        self.view = PanZoomView(self.scene)
        self.time_entry = QtWidgets.QLineEdit()

        # invert y axis for the view
        self.view.scale(1, -1)

        # add the trajectory elements to the graphic scene and then fit it in the view
        self.add_trajectory_items(self.flights)
        self.fit_scene_in_view()

        # add components to the root_layout
        root_layout.addWidget(self.view)

        # add a slider to change the simulation time increment
        # slider
        sld = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        sld.setMinimum(0)
        sld.setMaximum(N_POINT_TRAJECTORY-1)
        sld.setValue(self.currentPoint)

        sliderlbl = QtWidgets.QLabel(str(self.currentPoint))
        sliderlbl.setFixedWidth(50)

        # slot
        def changeCurrentPoint(val):
            self.currentPoint = val
            sliderlbl.setText(str(val))
            self.update_trajectory_items(val)

        # connect signal to slot
        sld.valueChanged.connect(changeCurrentPoint)
        self.speed_slider = sld

        # add slider and labels to toolbar
        toolbar = QtWidgets.QHBoxLayout()
        toolbar.addWidget(sld)
        toolbar.addWidget(sliderlbl)
        root_layout.addLayout(toolbar)
        # show the window
        self.show()

    def fit_scene_in_view(self):
        self.view.fitInView(self.view.sceneRect(), QtCore.Qt.KeepAspectRatio)

    def add_trajectory_items(self, flights):

        item_group = QtWidgets.QGraphicsItemGroup()
        flight_group = QtWidgets.QGraphicsItemGroup()
        self.scene.addItem(item_group)
        self.scene.addItem(flight_group)
        #airport_group.setZValue(AIRPORT_Z_VALUE)

        # Trajectories and starting points
        pen = QPen(QtGui.QColor(TRAJECTORY_COLOR), TRAJECTORY_WIDTH)
        pen.setCapStyle(QtCore.Qt.RoundCap)
        pen.setJoinStyle(QtCore.Qt.MiterJoin)
        for f in flights:
            path = QtGui.QPainterPath()
            trajectory = f.completeTrajectory(N_POINT_TRAJECTORY)
            path.moveTo(trajectory[0].x(), trajectory[0].y())
            for xy in trajectory[1:]:
                path.lineTo(xy.x(), xy.y())
            item = QtWidgets.QGraphicsPathItem(path, item_group)
            item.setPen(pen)
            item.setToolTip('Trajectoire ' + 'trajectory.name')
            item2 = AircraftItem(trajectory)
            flight_group.addToGroup(item2)

    #A modifier attention les temps des points sont pas les mêmes dans les trajectoires
    #Parametre t: l'instant auquel on souhaite avancer les vols
    def update_trajectory_items(self,t):
        """ updates Plots views """
        liste_item = self.scene.items()
        for item in liste_item:
            if str(type(item)) == "<class 'radarview.AircraftItem'>": #Pas beau ça
                item.changePos(t)

class AircraftItem(QGraphicsItemGroup):

    def __init__(self,trajectoire):
        super().__init__(None)
        # Création du point de l'avion
        self.item_avion = QGraphicsEllipseItem()
        self.item_avion.setRect(-PLANE_CIRCLE_SIZE/2,-PLANE_CIRCLE_SIZE/2,PLANE_CIRCLE_SIZE,PLANE_CIRCLE_SIZE) #Les coords x,y centrent le cercle
        self.item_avion.setBrush(FLIGHT_BRUSH)
        self.addToGroup(self.item_avion)
        self.trajectoire = trajectoire
        #self.item_avion.setPos(trajectoire[0] + QPoint(-PLANE_CIRCLE_SIZE/2,-PLANE_CIRCLE_SIZE/2))

        #Création du cercle de conflit pour l'avion
        self.item_conflit = QGraphicsEllipseItem()
        self.item_conflit.setRect(-CONFLICT_CIRCLE_SIZE/2, -CONFLICT_CIRCLE_SIZE/2, CONFLICT_CIRCLE_SIZE, CONFLICT_CIRCLE_SIZE) #Les coords x,y centrent le cercle
        self.item_conflit.setBrush(CONFLICT_CIRCLE_BRUSH)
        self.addToGroup(self.item_conflit)
        self.trajectoire = trajectoire
        #self.item_conflit.setPos(trajectoire[0] + QPoint(-PLANE_CIRCLE_SIZE/2,-PLANE_CIRCLE_SIZE/2))
        self.setPos(trajectoire[0] + QPoint(0,0))

    def changePos(self,t):
        point = self.trajectoire[t]
        self.setPos(point)