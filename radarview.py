import math
import constantes as ct

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QPen, QBrush, QColor
from PyQt5.QtWidgets import QGraphicsItemGroup, QGraphicsEllipseItem

WIDTH = 800  # Initial window width (pixels)
HEIGHT = 450  # Initial window height (pixels)
TRAJECTORY_WIDTH = 350
PLANE_CIRCLE_SIZE = 1000
CONFLICT_CIRCLE_SIZE = ct.d

N_POINT_TRAJECTORY = ct.T

# Couleurs utilisées
FLIGHT_COLOR = "blue"
TRAJECTORY_COLOR = "black"
CONFLICT_CIRCLE_COLOR = QColor(0, 255, 0, 100)
CONFLICT_CIRCLE_COLOR_CONFLICT = QColor(255, 0, 0, 100)

# Création des Qbrushs
FLIGHT_BRUSH = QBrush(QColor(FLIGHT_COLOR))
CONFLICT_CIRCLE_BRUSH = QBrush(CONFLICT_CIRCLE_COLOR)
CONFLICT_CIRCLE_BRUSH_CONFLICT = QBrush(CONFLICT_CIRCLE_COLOR_CONFLICT)


# Reprise du TD pyairport:
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

    def __init__(self, flights):
        super().__init__()

        # Paramètres
        self.setWindowTitle("Resolution de conflits aeriens")
        self.resize(WIDTH, HEIGHT)
        self.currentPoint = 0
        self.flights = flights

        # Création des composants
        root_layout = QtWidgets.QVBoxLayout(self)
        self.scene = QtWidgets.QGraphicsScene()
        self.scene.addRect(0, 0, 10, 10)
        self.view = PanZoomView(self.scene)
        # self.time_entry = QtWidgets.QLineEdit()

        # Inversion de l'axe des ordonnées
        self.view.scale(1, -1)

        # Ajout des trajectoires des avions
        self.add_trajectory_items(self.flights)
        self.fit_scene_in_view()

        # Ajout de la view dans le root_layout
        root_layout.addWidget(self.view)

        # Création du slider de temps
        sld = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        sld.setMinimum(0)
        sld.setMaximum(N_POINT_TRAJECTORY - 1)
        sld.setValue(self.currentPoint)

        sliderlbl = QtWidgets.QLabel(str(self.currentPoint))
        sliderlbl.setFixedWidth(50)

        # slot
        def changeCurrentPoint(val):
            self.currentPoint = val
            sliderlbl.setText(str(val))
            self.update_trajectory_items(val)

        # Abonnement du signal au slot
        sld.valueChanged.connect(changeCurrentPoint)
        self.speed_slider = sld

        # Ajout du slider à la toolbar
        toolbar = QtWidgets.QHBoxLayout()
        toolbar.addWidget(sld)
        toolbar.addWidget(sliderlbl)
        root_layout.addLayout(toolbar)

        self.show()

    def fit_scene_in_view(self):
        self.view.fitInView(self.view.sceneRect(), QtCore.Qt.KeepAspectRatio)

    def add_trajectory_items(self, flights):

        trajectory_group = QtWidgets.QGraphicsItemGroup()
        flight_group = QtWidgets.QGraphicsItemGroup()
        self.scene.addItem(trajectory_group)
        self.scene.addItem(flight_group)

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
            item = QtWidgets.QGraphicsPathItem(path, trajectory_group)
            item.setPen(pen)
            # item.setToolTip('Trajectoire ' + 'trajectory.name')
            item2 = AircraftItem(f)
            flight_group.addToGroup(item2)

    # Paramètre t: l'instant auquel on souhaite avancer les vols
    def update_trajectory_items(self, t):
        liste_item = self.scene.items()
        for item in liste_item:
            if str(type(item)) == "<class 'radarview.AircraftItem'>":  # Pas beau ça
                item.changePos(t)


# Groupe de deux cercles permettant de visualiser l'avion (petit cercle bleu)
# ainsi que son cercle de conflit (grand cercle vert ou rouge si conflit(s))
class AircraftItem(QGraphicsItemGroup):

    def __init__(self, f):
        super().__init__(None)
        # Création du point de l'avion
        self.item_avion = QGraphicsEllipseItem()
        self.item_avion.setRect(-PLANE_CIRCLE_SIZE / 2, -PLANE_CIRCLE_SIZE / 2, PLANE_CIRCLE_SIZE,
                                PLANE_CIRCLE_SIZE)  # Les coordonnées x,y centrent le cercle
        self.item_avion.setBrush(FLIGHT_BRUSH)
        self.addToGroup(self.item_avion)
        self.flight = f
        self.trajectoire = f.completeTrajectory(N_POINT_TRAJECTORY)

        # Création du cercle de conflit pour l'avion
        self.item_conflit = QGraphicsEllipseItem()
        self.item_conflit.setRect(-CONFLICT_CIRCLE_SIZE / 2, -CONFLICT_CIRCLE_SIZE / 2, CONFLICT_CIRCLE_SIZE,
                                  CONFLICT_CIRCLE_SIZE)  # Les coords x,y centrent le cercle
        dicoConflits = self.flight.listeConflits()
        duree = 0
        self.item_conflit.setBrush(CONFLICT_CIRCLE_BRUSH)
        if len(dicoConflits) != 0:
            for i in dicoConflits:
                for j in i:
                    duree += j[1] - j[0]
        if duree != 0:
            self.item_conflit.setBrush(CONFLICT_CIRCLE_BRUSH_CONFLICT)
        self.addToGroup(self.item_conflit)
        self.setPos(self.trajectoire[0] + QPoint(0, 0))

    # Cette fonction sert à définir la position de l'avion à l'instant t
    # Elle change également la couleur du cercle de conflits d'un avion au
    # cas où il est encore impliqué dans au moins un conflit.
    # Cela nous permet de vérifier visuellement s'il persiste des conflits,
    # et dans ce cas, quels avions sont impliqués.
    def changePos(self, t):
        point = self.trajectoire[t]
        self.setPos(point)
