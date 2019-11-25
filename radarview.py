import math

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QPen

WIDTH = 800  # Initial window width (pixels)
HEIGHT = 450  # Initial window height (pixels)
TRAJECTORY_COLOR = "grey"
TRAJECTORY_WIDTH = 15


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

    def __init__(self,trajectories):
        super().__init__()

        # Settings
        self.setWindowTitle("Resolution de conflits aeriens")
        self.resize(WIDTH, HEIGHT)

        # create components
        root_layout = QtWidgets.QVBoxLayout(self)
        self.scene = QtWidgets.QGraphicsScene()
        self.view = PanZoomView(self.scene)
        self.time_entry = QtWidgets.QLineEdit()

        # invert y axis for the view
        self.view.scale(1, -1)

        # add the airport elements to the graphic scene and then fit it in the view
        self.add_trajectory_items(trajectories)
        self.fit_scene_in_view()

        # add components to the root_layout
        root_layout.addWidget(self.view)

        # show the window
        self.show()

    def fit_scene_in_view(self):
        self.view.fitInView(self.view.sceneRect(), QtCore.Qt.KeepAspectRatio)

    def add_trajectory_items(self, trajectories):

        item_group = QtWidgets.QGraphicsItemGroup()
        self.scene.addItem(item_group)
        #airport_group.setZValue(AIRPORT_Z_VALUE)

        # Taxiways
        pen = QPen(QtGui.QColor(TRAJECTORY_COLOR), TRAJECTORY_WIDTH)
        pen.setCapStyle(QtCore.Qt.RoundCap)
        pen.setJoinStyle(QtCore.Qt.MiterJoin)
        for trajectory in trajectories:
            path = QtGui.QPainterPath()
            path.moveTo(trajectory[0].x(), trajectory[0].y())
            for xy in trajectory[1:]:
                path.lineTo(xy.x(), xy.y())
            item = QtWidgets.QGraphicsPathItem(path, item_group)
            item.setPen(pen)
            item.setToolTip('Trajectoire ' + 'trajectory.name')

