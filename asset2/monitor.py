import sys
import logging

from utils import ll2px

from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

REFRESH_RATE = 1 # fps
SIZE = 800

class Screen(QMainWindow):
    """
    Screen draws the airport states onto the screen using PyQt5.
    """

    def __init__(self, airport, clock):

        super().__init__()

        # Sets the window title
        self.setWindowTitle(airport.code)

        # Sets the window size
        self.setGeometry(0, 0, SIZE, SIZE)
        self.setFixedSize(SIZE, SIZE)

        # Draws the background image
        self.draw_background(airport.surface.image_filepath)

        # Saves the current airport state
        self.airport = airport

        # Saves the clock in simulation
        self.clock = clock

        # Shows
        self.show()

    def draw_background(self, image_filepath):

        # Sets the image object
        pixmap = QPixmap(image_filepath, "1")
        scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatio)

        # Draw
        palette = QPalette()
        palette.setBrush(10, QBrush(scaled_pixmap))
        self.setPalette(palette)

    def paintEvent(self, event):
        self.draw_gates()
        self.draw_spots()
        self.draw_runways()
        self.draw_taxiways()
        self.draw_pushback_ways()
        self.draw_aircrafts()

        self.draw_time()

    def draw_gates(self):
        for gate in self.airport.surface.gates:
            self.draw_node(gate, Qt.darkGreen)

    def draw_spots(self):
        for spot in self.airport.surface.spots:
            self.draw_node(spot, Qt.red)

    def draw_aircrafts(self):
        for aircraft in self.airport.aircrafts:
            self.draw_node(aircraft.location, Qt.black)

    def draw_node(self, node, color):

        painter = QPainter()
        painter.begin(self)
        painter.setPen(color)
        px_pos = ll2px(node.geo_pos, self.airport.surface.corners, SIZE)
        point = QPoint(px_pos[0], px_pos[1])
        painter.drawEllipse(point, 3, 3)
        painter.end()

    def draw_runways(self):
        for runway in self.airport.surface.runways:
            self.draw_link(runway, Qt.blue)

    def draw_taxiways(self):
        for taxiway in self.airport.surface.taxiways:
            self.draw_link(taxiway, Qt.gray)

    def draw_pushback_ways(self):
        for taxiway in self.airport.surface.pushback_ways:
            self.draw_link(taxiway, Qt.green)

    def draw_link(self, link, color):

        # Setups painter
        painter = QPainter()
        painter.begin(self)
        painter.setPen(color)

        # Draws all nodes of the link
        corners = self.airport.surface.corners
        previous_node = None
        for node in link.nodes:
            if previous_node:
                prev_geo_pos = ll2px(previous_node.geo_pos, corners, SIZE)
                curr_geo_pos = ll2px(node.geo_pos, corners, SIZE)
                painter.drawLine(prev_geo_pos[0], prev_geo_pos[1],
                                 curr_geo_pos[0], curr_geo_pos[1])
            previous_node = node

        # Closes the painter
        painter.end()

    def draw_time(self):
        self.setWindowTitle(str(self.clock.now))

    def tick(self):
        self.repaint()


class Monitor:
    """
    Monitor works as an observer which pull states from the simulation and
    draw them on the screen. Two types of states are used. Static states
    contain states that won't change during the whole simulation process; 
    runtime states indicates the states the changes within simulation.
    """

    def __init__(self, simulation):

        # Setups the logger
        self.logger = logging.getLogger(__name__)

        self.app = QApplication(sys.argv)
        self.simulation = simulation
        self.screen = Screen(self.simulation.airport, self.simulation.clock)

    def start(self):
        self.app.exec_()

    def tick(self):
        self.screen.tick()
