import sys

from utils import ll2px

from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

REFRESH_RATE = 1 # fps
SIZE = 640

class Screen(QWidget):


    def __init__(self, airport, gates):

        super().__init__()

        # Sets the window title
        self.setWindowTitle(airport.name)

        # Sets the window size
        self.setGeometry(0, 0, SIZE, SIZE)

        # Draws the background image
        self.draw_background(airport.image_filepath)

        # Saves gates and draw them later
        self.gates = gates

        # Shows
        self.show()

    def draw_background(self, image_filepath):

        # Sets the image object
        print(image_filepath)
        pixmap = QPixmap(image_filepath, "1")
        scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatio)

        # Draw
        palette = QPalette()
        palette.setBrush(10, QBrush(scaled_pixmap))
        self.setPalette(palette)

    def paintEvent(self, event):

        # Draw all gates
        painter = QPainter()
        painter.begin(self)
        painter.setPen(Qt.blue)
        for gate in self.gates:
            point = QPoint(gate[0], gate[1])
            painter.drawEllipse(point, 3, 3)
        painter.end()

class Monitor:
    """ Monitor works as an observer which pull states from the simulation and
    draw them on the screen. Two types of states are used. Static states
    contain states that won't change during the whole simulation process; 
    runtime states indicates the states the changes within simulation.
    """

    def __init__(self, simulation):

        static_state = simulation.get_static_state()
        surface = static_state["surface"]

        # Initializes the screen
        self.simulation = simulation
        self.app = QApplication(sys.argv)

        # Parse gates
        gates = []
        for gate in surface.gates:
            px_pos = ll2px(gate.geo_pos, surface.airport.corners, SIZE)
            print(px_pos)
            gates.append(px_pos)

        # Starts screen and holds
        self.screen = Screen(surface.airport, gates)
        self.app.exec_()

    def close(self):
        self.screen.close()
