import sys
import random

from PySide6 import QtCore, QtWidgets, QtGui # type: ignore
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QMainWindow, QSizePolicy # type: ignore
from PySide6.QtGui import QIcon, QImage, QPixmap, QPainter, QColor, QPen, QLinearGradient # type: ignore
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis # type: ignore
from PySide6.QtCore import QPointF, Qt, QTimer # type: ignore
from PySide6.QtWidgets import QGraphicsBlurEffect # type: ignore

class Title(QtWidgets.QWidget):
    def __init__(self, name):
        super().__init__()
        self.text = QtWidgets.QLabel(name,alignment=QtCore.Qt.AlignCenter)

        #Layout
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.text)

class ProcessSection(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.title = Title("CPU")
        self.processList = ProcessList()

        #Layout
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.processList)

class GraphSection(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()   


class ProcessList(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()


        self.layout = QtWidgets.QVBoxLayout(self)

        # Create a QScrollArea
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet(" border: none")

        # Create a widget to hold the process containers
        self.container_widget = QtWidgets.QWidget()
        self.container_layout = QtWidgets.QVBoxLayout(self.container_widget)
        

        # Add process containers to the container widget
        for i in range(10):
            self.processContainer = ProcessContainer("process " + str(i))
            self.container_layout.addWidget(self.processContainer,alignment=QtCore.Qt.AlignTop)

        # Set the container widget as the scroll area's widget
        self.scroll_area.setWidget(self.container_widget)

        # Add the scroll area to the main layout
        self.layout.addWidget(self.scroll_area)

def random_color():
    colors = [
    "#fffd77",
    "#ffa06e",
    "#ff4365",
    "#235789",
    "#1298a5",
    "#00d9c0",
    "#27c28c",
    "#4daa57"
]
    #r = random.randint(0, 255)
    #g = random.randint(0, 255)
    #b = random.randint(0, 255)
    #return f'#{r:02x}{g:02x}{b:02x}'
    return random.choice(colors)

class ProcessContainer(QtWidgets.QWidget):
    def __init__(self, processName):
        super().__init__()

        color = random_color()
        
        #self.setStyleSheet("background-color: #69C4E8;")
        #self.setFixedSize(256, 50)
        
        #Widget Creation
        self.container = QtWidgets.QFrame()
        self.container.setStyleSheet(f"background-color: #191919; border: 1px groove {color}")
        self.container.setFixedSize(256, 50)

        self.checkbox = QtWidgets.QCheckBox()
        self.checkbox.setFixedSize(15, 15)
        self.checkbox.setStyleSheet("QCheckBox::indicator:checked {background-color:" + str(color) +" ;}")
        #self.checkbox.setStyleSheet("border: none")
        self.text = QtWidgets.QLabel(processName)
        self.text.setStyleSheet("color: white; font-weight: bold; border: none")

#border: 1px solid {color};
        
        #folder button
        icon = QIcon("images/grey-folder-solid-24.png")
        self.folderButton = QtWidgets.QPushButton("")
        self.folderButton.setIcon(icon)
        self.folderButton.setFixedSize(32, 32)
        self.folderButton.setStyleSheet("""
            
            QPushButton:!pressed {
                background-color: #000;
                border: none;
            };
                                        
            QPushButton:pressed {
                background-color: #e0e0e0;
                border: none;
            };
            
            
        """)
    
        
        #Layout
        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.addWidget(self.container)
        self.container_layout = QtWidgets.QHBoxLayout(self.container)
        self.container_layout.addWidget(self.checkbox)
        self.container_layout.addWidget(self.text)
        self.container_layout.addWidget(self.folderButton)


class GraphWidget(QWidget):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background:transparent;")
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        margin = 20

        # Draw the glowing graph line with gradient
        gradient = QLinearGradient(0, 0, rect.width(), rect.height())
        gradient.setColorAt(0.0, random_color())
        gradient.setColorAt(1.0, random_color())
        pen = QPen(QColor(0, 0, 255, 200), 2)
        pen.setBrush(gradient)
        painter.setPen(pen)
        

        max_value = max(self.data)
        scale_x = (rect.width() - 2 * margin) / (len(self.data) - 1)
        scale_y = (rect.height() - 2 * margin) / max_value

        for i in range(len(self.data) - 1):
            x1 = margin + i * scale_x
            y1 = rect.height() - margin - self.data[i] * scale_y
            x2 = margin + (i + 1) * scale_x
            y2 = rect.height() - margin - self.data[i + 1] * scale_y
            painter.drawLine(x1, y1, x2, y2)


class GraphWidgetsContainer(QWidget):
        #processes[]
            #time[]
                #dictionary{}
    def __init__(self, processes = [[]], parent=None):
        super().__init__(parent)
        # Layout
        stacked_layout = QtWidgets.QStackedLayout(self)
        self.setLayout(stacked_layout)
        stacked_layout.setStackingMode(stacked_layout.StackAll)

        for p in processes:
            self.graph_widget = GraphWidget(p)
            stacked_layout.addWidget(self.graph_widget)
            

class ScrollingBackground(QWidget):
    def update_counter(self):
        self.counter += 1
        self.update() 

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #191919;")
        #for testing
        self.counter = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_counter)
        self.timer.start(16.67)  # 60fps 
        

    def paintEvent(self, event):

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        margin = 20
        grid_size = 60
        offset = (-self.counter * rect.width() / 1000.2)%(grid_size) #Modulus 😎

        # Draw the grid
        pen = QPen(Qt.lightGray, 1, Qt.DotLine)
        painter.setPen(pen)

        for x in range(margin, rect.width() - margin, grid_size):
            painter.drawLine(x + offset, margin, x + offset, rect.height() - margin)
        for y in range(margin, rect.height() - margin, grid_size):
            painter.drawLine(margin, y, rect.width() - margin, y)

class MainWindow(QWidget):
    #for glow effect
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Grab the pixmap of the graph widget
        pixmap = self.graph_widget.grab()
        # Display the pixmap in the label
        self.label.setPixmap(pixmap)

    def __init__(self):
        super().__init__()
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        self.setWindowTitle("Pulse X")

        self.blur_effect = QGraphicsBlurEffect()
        self.blur_effect.setBlurRadius(10)  # Adjust the blur radius
        
        self.graph_widget = GraphWidget()
        self.grid_widget = ScrollingBackground(self)

        self.label = QLabel()
        self.label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)

        self.label.setGraphicsEffect(self.blur_effect)

        # Layout
        stacked_layout = QtWidgets.QStackedLayout(self)
        self.setLayout(stacked_layout)
        stacked_layout.setStackingMode(stacked_layout.StackAll)
        stacked_layout.addWidget(self.grid_widget)
        stacked_layout.addWidget(self.graph_widget)
        stacked_layout.addWidget(self.label)

        self.setLayout(stacked_layout)


if __name__ == "__main__":

    #test data
    data_array = [
    0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0,
    10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0,
    20.0, 21.0, 22.0, 23.0, 24.0, 25.0, 26.0, 27.0, 28.0, 29.0,
    30.0, 31.0, 32.0, 33.0, 34.0, 35.0, 36.0, 37.0, 38.0, 39.0,
    40.0, 41.0, 42.0, 43.0, 44.0, 45.0, 46.0, 47.0, 48.0, 49.0,
    50.0, 51.0, 52.0, 53.0, 54.0, 55.0, 56.0, 57.0, 58.0, 59.0,
    60.0, 61.0, 62.0, 63.0, 64.0, 65.0, 66.0, 67.0, 68.0, 69.0,
    70.0, 71.0, 72.0, 73.0, 74.0, 75.0, 76.0, 77.0, 78.0, 79.0,
    80.0, 81.0, 82.0, 83.0, 84.0, 85.0, 86.0, 87.0, 88.0, 89.0,
    90.0, 91.0, 92.0, 93.0, 94.0, 95.0, 96.0, 97.0, 98.0, 99.0, 100.0
    ]

    proccess_array = []

    for i in range(10):
        random.shuffle(data_array)
        proccess_array.append(data_array[:]) #shallow copy


    app = QtWidgets.QApplication([])
    #widget = MainWindow()#(data_array)
    widget = GraphWidgetsContainer(proccess_array)
    widget.resize(1024, 600)
    widget.show()

    sys.exit(app.exec())
