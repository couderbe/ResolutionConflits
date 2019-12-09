import math

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QPen

WIDTH = 800  # Initial window width (pixels)
HEIGHT = 450  # Initial window height (pixels)
TRAJECTORY_COLOR = "black"
TRAJECTORY_WIDTH = 100


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
        self.currentPoint = 0

        # create components
        root_layout = QtWidgets.QVBoxLayout(self)
        self.scene = QtWidgets.QGraphicsScene()
        self.scene.addRect(0,0,10,10)
        self.view = PanZoomView(self.scene)
        self.time_entry = QtWidgets.QLineEdit()

        # invert y axis for the view
        self.view.scale(1, -1)

        # add the airport elements to the graphic scene and then fit it in the view
        self.add_trajectory_items(trajectories)
        self.fit_scene_in_view()

        # add components to the root_layout
        root_layout.addWidget(self.view)

        # add a slider to change the simulation time increment
        # slider
        sld = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        sld.setMinimum(0)
        sld.setMaximum(5)
        sld.setValue(self.currentPoint)

        sliderlbl = QtWidgets.QLabel(str(self.currentPoint))
        sliderlbl.setFixedWidth(50)

        # slot
        def changeCurrentPoint(val):
            self.currentPoint = val
            sliderlbl.setText(str(val))

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

    def add_trajectory_items(self, trajectories):

        item_group = QtWidgets.QGraphicsItemGroup()
        self.scene.addItem(item_group)
        #airport_group.setZValue(AIRPORT_Z_VALUE)

        # Trajectories and starting points
        pen = QPen(QtGui.QColor(TRAJECTORY_COLOR), TRAJECTORY_WIDTH)
        pen.setCapStyle(QtCore.Qt.RoundCap)
        pen.setJoinStyle(QtCore.Qt.MiterJoin)
        for trajectory in trajectories:
            # Ajout du premier point
            #item_group.addEllipse(10, 10, 100, 50);
            path = QtGui.QPainterPath()
            path.moveTo(trajectory[0].x(), trajectory[0].y())
            for xy in trajectory[1:]:
                path.lineTo(xy.x(), xy.y())
            item = QtWidgets.QGraphicsPathItem(path, item_group)
            item.setPen(pen)
            item.setToolTip('Trajectoire ' + 'trajectory.name')

    ##A modifier attention les temps des points sont pas les mêmes dans les trajectoires
    #def update_aircraft_items(self):
    #    """ updates Plots views """
    #   new_flights = self.radarView.simulation.current_flights
    #  # add new aircraft items for flights who joined
    #    for f in set(new_flights) - set(self.current_flights):
    #        item = AircraftItem(self.radarView.simulation, f, self)  # create an item
    #        self.radarView.scene.addItem(item)  # add it to scene
    #        self.aircraft_items_dict[f] = item  # add it to item dict
    #    # remove aircraft items for flights who left
    #    for f in set(self.current_flights) - set(new_flights):
    #       item = self.aircraft_items_dict.pop(f)  # get item from flight in the dictionary (and remove it)
    #        self.radarView.scene.removeItem(item)   # remove it also from scene
    #    # refresh current flights list
    #    self.current_flights = new_flights
    #    # get conflicting flights
    #    conf = self.radarView.simulation.conflicts
    #    # update positions of the current aircraft items
    #    for aircraft in self.aircraft_items_dict.values():
    #        aircraft.update_position(aircraft.flight in conf)
    #    # tell everyone who is listening that there is a flight list update
    #    self.radarView.flight_list_changed_signal.emit(self.current_flights)