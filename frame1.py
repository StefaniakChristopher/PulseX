import sys
import asyncio
import random

from PySide6 import QtCore, QtWidgets, QtGui # type: ignore
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QMainWindow, QSizePolicy, QGraphicsBlurEffect # type: ignore
from PySide6.QtGui import QIcon, QFont, QPixmap, QPainter, QColor, QPen, QLinearGradient # type: ignore
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis # type: ignore
from PySide6.QtCore import QPointF, Qt, QTimer # type: ignore
from PySide6.QtGui import QFontDatabase, QFont
#from PySide6.QtWidgets import  # type: ignore
from PySide6.QtCore import Qt, QTimer, Signal

class MainWidget(QtWidgets.QWidget):
    signal_to_main = Signal()
    selectedMonitor="CPU"
    def sendSigToMain(self):
        self.selectedMonitor=self.process_section.selectedMonitor;
        self.signal_to_main.emit()
    def __init__(self, data):
        super().__init__()
        self.setWindowTitle("Pulse X")
	
        #Instantiate Widgets
        self.process_section = ProcessSection()
        graph_section = GraphSection(data)
        self.process_section.signal_to_main.connect(self, self.sendSigToMain);
        #Layout
        layout = QtWidgets.QHBoxLayout(self)
        #layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.process_section)
        layout.addWidget(graph_section)

class Title(QtWidgets.QWidget):
    def __init__(self, name):
        super().__init__()
        #Create Widget
        text = QtWidgets.QLabel(name, alignment=QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        
        font_id = QFontDatabase.addApplicationFont("./font/Exo_2/Exo2-VariableFont_wght.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]

        font = QFont(font_family)
        #font.setPointSize(30)
        font.setPixelSize(65)
        font.setStyleStrategy(QFont.PreferAntialias)
        font.setWeight(QFont.Black)
        text.setFont(font)

        #resize widget
        self.setFixedHeight(58)
        self.setFixedWidth(300)

        #Layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(text)


class ProcessSection(QtWidgets.QWidget):
    signal_to_main = Signal()
    selectedMonitor = "CPU";
    def sendSigToMain(self):
        self.selectedMonitor=self.metricList.selectedMonitor
        self.signal_to_main.emit()
    def __init__(self):
        super().__init__()

        self.setStyleSheet("border: 5px outset #191919;")
        self.setFixedWidth(300)

        title = Title("PulseX")
        self.metricList = MetricList()
        self.metricList.signal_to_main.connect(self, self.sendSigToMain);
        #Layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(title)
        layout.addWidget(self.metricList)


class GraphSection(QtWidgets.QWidget):
    def __init__(self, data):
        super().__init__()
        media_controls = PlayControls()
        graph = CompleteGraphWidget(data)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(media_controls)
        layout.addWidget(graph)


class PlayControls(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.is_playing = False
        self.button = QtWidgets.QPushButton("")
        self.button.setFixedHeight(58)
        self.button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.button.clicked.connect(self.on_button_clicked)
        self.pause_icon = QtGui.QIcon("images/pause-regular-24.png")
        self.play_icon = QtGui.QIcon("images/play-regular-24.png")

        self.button.setIcon(self.pause_icon)
        self.button.setIconSize(QtCore.QSize(32, 32))

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.button)


    def on_button_clicked(self):
        # This function will be executed when the button is clicked
        self.is_playing = not self.is_playing
        if self.is_playing:
            self.button.setIcon(self.play_icon)
        else:
            self.button.setIcon(self.pause_icon)


class MetricList(QtWidgets.QWidget):
    signal_to_main = Signal()
    selectedMonitor="Hello"
    def sendDiskReadSigToMain(self):
         self.sendSigToMain("disk_read_speed_mb_s");
    def sendCPUSigToMain(self):
         self.sendSigToMain("cpu_percent");
    def sendDiskWriteSigToMain(self):
         self.sendSigToMain("disk_write_mb");
    def sendMemorySigToMain(self):
         self.sendSigToMain("memory_mb");

    def sendSigToMain(self,resource="CPU"):
        self.selectedMonitor=resource;
        self.signal_to_main.emit()
    def __init__(self):
        super().__init__()

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create a QScrollArea
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scroll_area.setWidgetResizable(True)
        # Set stylesheet to style the scroll bar
        self.setStyleSheet("""
            QScrollBar:vertical {
                border: 1px solid #999999;
                background: grey;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }

            QScrollBar::handle:vertical {
                background: #191919;
                min-height: 1px;
                border: 1px outset #191919
            }

            QScrollBar::add-line:vertical {
                border: 1px solid #999999;
                background: #c4c4c4;
                height: 15px;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
            }

            QScrollBar::sub-line:vertical {
                border: 1px solid #999999;
                background: #c4c4c4;
                height: 15px;
                subcontrol-position: top;
                subcontrol-origin: margin;
            }

            
        """)
        #self.scroll_area.setStyleSheet(" border: none")

        # Create a widget to hold the process containers
        self.container_widget = QtWidgets.QWidget()
        self.container_widget.setStyleSheet(" border: none")
        self.container_layout = QtWidgets.QVBoxLayout(self.container_widget)
        
        # Add metric containers to the container widget
        self.cpu_item = MetricItem("CPU",0)
        self.memory_item = MetricItem("Memory",1)
        self.disk_write_item = MetricItem("Disk Write",2)
        self.disk_read_item = MetricItem("Disk Read",3)
        #self.disk_item = MetricItem("Disk",4)
        self.container_layout.addWidget(self.cpu_item,alignment=QtCore.Qt.AlignTop)
        self.container_layout.addWidget(self.memory_item,alignment=QtCore.Qt.AlignTop)
        self.container_layout.addWidget(self.disk_write_item,alignment=QtCore.Qt.AlignTop)
        self.container_layout.addWidget(self.disk_read_item,alignment=QtCore.Qt.AlignTop)
        #self.container_layout.addWidget(self.disk_item,alignment=QtCore.Qt.AlignTop)

        self.cpu_item.signal_to_main.connect(self, self.sendCPUSigToMain);
        self.memory_item.signal_to_main.connect(self, self.sendMemorySigToMain);
        self.disk_write_item.signal_to_main.connect(self, self.sendDiskWriteSigToMain);
        self.disk_read_item.signal_to_main.connect(self, self.sendDiskReadSigToMain);
        #self.disk_item.signal_to_main.connect(self, self.sendDiskSigToMain);
        # Set the container widget as the scroll area's widget
        self.scroll_area.setWidget(self.container_widget)

        # Add the scroll area to the main layout
        layout.addWidget(self.scroll_area)

def metric_color(color_choice):
    colors = [
    "#FF0000",
    "#0000FF",
    "#00FF00",
    "#FFFF00",
    "#FF00FF"
]
    #r = random.randint(0, 255)
    #g = random.randint(0, 255)
    #b = random.randint(0, 255)
    #return f'#{r:02x}{g:02x}{b:02x}'
    return colors[color_choice]

def darken(color):
	returnColor=[];
	a = list(color);
	for hex in a:
		returnColor.append(darkenHex(hex,5));
	returnColor="".join(str(x) for x in returnColor);
	return returnColor;
def darkenHex(hexchar,spaces):
	if hexchar=='#':
		 return hexchar;
	hexes=["0","1","2","3","4","5","6","7","8","9","A","B","C","D","E","F"]
	a = hexes.index(hexchar);
	a=max(0,a-spaces);
	return hexes[a];
class MetricItem(QtWidgets.QWidget):
    signal_to_main = Signal()
    def mousePressEvent(self, event):
        self.signal_to_main.emit()
        super().mousePressEvent(event)
    def __init__(self, processName,color_choice):
        super().__init__()

        color = darken(metric_color(color_choice));
        
        #Widget Creation
        self.container = QtWidgets.QFrame()
        self.container.setStyleSheet(f"background-color: {color}; border: 1px solid {color};")
        self.container.setFixedSize(256, 50)

        self.checkbox = QtWidgets.QCheckBox()
        self.checkbox.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.checkbox.setFixedSize(15, 15)
        #self.checkbox.setStyleSheet("QCheckBox::indicator:unchecked { border: none; }")
        self.checkbox.setStyleSheet("QCheckBox::indicator:checked {background-color:" + str(color) +" ; border: none;} QCheckBox::indicator:unchecked { border: none;  };")
        #self.checkbox.setStyleSheet("border: none")
        self.text = QtWidgets.QLabel(processName)
        self.text.setStyleSheet("color: white; font-weight: bold; border: none")

        #border: 1px solid {color};
        
        #folder button
        icon = QIcon("images/grey-folder-solid-24.png")
        self.folderButton = QtWidgets.QPushButton("")
        self.folderButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.folderButton.setIcon(icon)
        self.folderButton.setFixedSize(32, 32)
        self.folderButton.setStyleSheet("""
            QPushButton {
                background-color: #212121;
                border: 2px outset  #212121;
            }
            QPushButton:pressed {
                background-color: #101010;
                border: 2px inset #101010;
            }
        """)

    
        #Layout
        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.container)
        self.container_layout = QtWidgets.QHBoxLayout(self.container)
        self.container_layout.addWidget(self.checkbox)
        self.container_layout.addWidget(self.folderButton)
        self.container_layout.addWidget(self.text)
        


class GraphWidget(QWidget):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        margin = 20

        #gradient = QLinearGradient(0, 0, rect.width(), rect.height())
        #gradient.setColorAt(0.0, random_color())
        #gradient.setColorAt(1.0, random_color())
        pen = QPen(QColor(metric_color(0)), 2)
        #pen.setBrush(gradient)
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
        self.p = processes
        self.i = 0
        self.glow = False

        self.graph_label = QLabel()
        self.graph_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)

        self.pix_map = QPixmap()
        self.temp_widget = QtWidgets.QWidget()
        self.temp_widget.setStyleSheet("background-color: #070f0c;")

        self.stacked_layout = QtWidgets.QStackedLayout(self)
        self.temp_widget.setLayout(self.stacked_layout)
        self.stacked_layout.setStackingMode(self.stacked_layout.StackingMode.StackAll)
        
        self.graph_layout = QtWidgets.QStackedLayout(self)
        self.setLayout(self.graph_layout)

        self.add_widget_timer = QtCore.QTimer()
        self.add_widget_timer.setInterval(1000/60)
        self.add_widget_timer.timeout.connect(self.add)
        self.add_widget_timer.start()

    
    def add(self):
        self.temp_widget.setGeometry(self.rect())
        #for p in processes:
        #print(self.i)
        renders_per_pass = 5
        for offset in range(renders_per_pass):
            self.graph_widget = GraphWidget(self.p[self.i + offset])
            self.graph_widget.setGeometry(self.rect())
            self.stacked_layout.addWidget(self.graph_widget)
        
        self.pix_map = self.temp_widget.grab()
        #self.graph_label.setPixmap(self.pix_map)
        #self.graph_layout.addWidget(self.graph_label)

        #self.blur_label.setPixmap(self.pix_map)
        #self.graph_layout.addWidget(self.blur_label)
        
        #painter = QtGui.QPainter(self)
        #painter.setCompositionMode(QtGui.QPainter.CompositionMode_Screen)
        #painter.drawPixmap(0, 0, self.blur_pixmap)
        #painter.end()

        self.i += renders_per_pass
        if self.i > len(self.p) - 1:
            self.add_widget_timer.stop()
            self.blur_effect = QGraphicsBlurEffect()
            self.blur_effect.setBlurRadius(20)  # Adjust the blur radius
            self.blur_label = QLabel()
            self.blur_label.setGeometry(self.rect())
            self.blur_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
            self.blur_label.setPixmap(self.pix_map)
            self.blur_label.setGraphicsEffect(self.blur_effect)
            self.blur_pixmap = self.blur_label.grab()
            self.glow = True
        
        
    def paintEvent(self, event):
        painter1 = QtGui.QPainter(self)
        painter1.drawPixmap(0, 0, self.pix_map)
        painter1.end()

        if self.glow:
            painter2 = QtGui.QPainter(self)
            painter2.setOpacity(.85)
            #painter2.setCompositionMode(QtGui.QPainter.CompositionMode_Screen)
            #painter2.setCompositionMode(QtGui.QPainter.CompositionMode_Plus)
            #painter2.setCompositionMode(QtGui.QPainter.CompositionMode_Overlay)
            painter2.setCompositionMode(QtGui.QPainter.CompositionMode_Lighten)

            painter2.drawPixmap(0, 0, self.blur_pixmap)
            painter2.end()
            

class ScrollingGrid(QWidget):
    def update_counter(self):
        self.counter += 1
        self.update() 

    def __init__(self, parent=None):
        super().__init__(parent)
        #self.setMask(pixmap.mask())
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
        pen = QPen(Qt.lightGray, .25, QtCore.Qt.DotLine)
        painter.setPen(pen)

        for x in range(margin, rect.width() - margin, grid_size):
            painter.drawLine(x + offset, margin, x + offset, rect.height() - margin)
        for y in range(margin, rect.height() - margin, grid_size):
            painter.drawLine(margin, y, rect.width() - margin, y)


class CompleteGraphWidget(QWidget):
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.graph_widget.deleteLater()

        # Create widgets
        self.graph_widget = GraphWidgetsContainer(self.data)
        self.stacked_layout.addWidget(self.graph_widget)
    
    #def paintEvent(self, event):
        # Draw the pixmap on the widget
        #painter = QtGui.QPainter(self)
        #painter.setCompositionMode(QtGui.QPainter.CompositionMode_Screen)
        #painter.drawPixmap(0, 0, self.pixmap)

    def __init__(self, data):
        super().__init__()
        #self.resize_timer = QtCore.QTimer()
        #self.resize_timer.setInterval(500)  # Update every 500 milliseconds (.5 second)
        #self.resize_timer.timeout.connect(self.delayed_resize_event)

        self.data = data
        #create Widgets
        self.b_widget = QtWidgets.QWidget()
        self.b_widget.setStyleSheet("border: 5px groove #191919;")
        self.graph_widget = GraphWidgetsContainer(self.data)
        self.grid_widget = ScrollingGrid()
        self.time_line_scrubber = TimeLineScrubber()
        
        #self.combined_label = QLabel()
        #self.combined_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        #self.combined_label.setGraphicsEffect(self.blur_effect)

        # Layout
        self.stacked_layout = QtWidgets.QStackedLayout(self)
        self.setLayout(self.stacked_layout)
        self.stacked_layout.setStackingMode(self.stacked_layout.StackingMode.StackAll)
        #Note: graphs_widgets_container is added on resize event
        self.stacked_layout.addWidget(self.time_line_scrubber)
        self.stacked_layout.addWidget(self.b_widget)
        self.stacked_layout.addWidget(self.grid_widget)
        
        #self.stacked_layout.addWidget(self.graph_widget)
        
        
        #stacked_layout.addWidget(self.blured_label)
        #self.stacked_layout.addWidget(self.combined_label)

        self.setLayout(self.stacked_layout)


class TimeLineScrubber(QtWidgets.QWidget):
    def resizeEvent(self, event):
        super().resizeEvent(event)
        #Math Stuff for keeping the TimeScrubber in the correct position when resizing window 🤓
        ratio = (self.selected_time / self.old_width)
        self.selected_time = round(event.size().width() * ratio)
        self.time_scrubber.move(self.selected_time,0 )
        self.old_width = event.size().width()

    def __init__(self):
        super().__init__()
        self.selected_time = 1
        self.old_width = self.width()
        self.is_clicked = False

        #Create Widget
        self.time_scrubber = TimeScrubber()#QtWidgets.QPushButton(" ")
        self.time_scrubber.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))
        self.time_scrubber.setFixedWidth(4)

        #Layout
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.time_scrubber)
        self.setLayout(layout)

    def mouseMoveEvent(self, event):
        if self.time_scrubber.mouse_detector.is_mouse_over and self.is_clicked:
            #print()
            pos = event.position()
            if pos.x() < self.width() and pos.x() > 0:
                self.selected_time = round(pos.x()) - 2
                #print(self.selected_time)
                self.time_scrubber.move(self.selected_time,0 )

    
    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.is_clicked = False
        self.time_scrubber.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))
        #self.test()
    
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.is_clicked = True
        self.time_scrubber.setCursor(QtGui.QCursor(QtCore.Qt.ClosedHandCursor))
        #self.test()
    
    #def time_scrubber_released(self):
        #self.is_clicked = False
        #self.test()
    

    #def test(self):
        #print(self.is_clicked)


class TimeScrubber(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.mouse_detector = MouseDetector()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.mouse_detector)
        self.setLayout(layout)




class MouseDetector(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.is_mouse_over = False

        widget = QtWidgets.QWidget()
        self.setStyleSheet("background-color: white;")
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(widget)
        self.setLayout(layout)

    def enterEvent(self, event):
        #print("enter")
        self.is_mouse_over = True
        super().enterEvent(event)

    def leaveEvent(self, event):
        #print("leave")
        self.is_mouse_over = False
        super().leaveEvent(event)


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
    
    #font.setBold(True)
    #font.setHintingPreference(QFont.PreferAntialias)  # Enable antialiasing
    
    #widget = CompleteGraphWidget(proccess_array)#(data_array)
    #widget = GraphWidgetsContainer(proccess_array)
    #widget = PlayControls()
    #widget = GraphSection(proccess_array)
    widget = MainWidget(proccess_array)
    #widget = ScrollingGrid()
    #widget = TimeLineScrubber()
    #widget = TimeScrubber()
    #widget = MouseDetector()
    widget.resize(1024, 600)
    widget.show()

    #loop.run_until_complete(app.exec())
    sys.exit(app.exec())
    