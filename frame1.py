import sys
import time
import asyncio
import random
import total_usage
import concurrent.futures
from collections import deque
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QMainWindow, QSizePolicy, QGraphicsBlurEffect # type: ignore
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QPen, QFontDatabase, QFont # type: ignore
#from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis # type: ignore
from PySide6.QtCore import Qt, QTimer, Signal # type: ignore


play_overview = True
collect_data_overview = True
data_targets_overview = []
graphs_per_pass_overview = 4

max_size_overview=60;
resource_deque= deque([ {
                'cpu_usage': 0.0,
                'ram_usage': 0.0,
                'disk_read': 0.0,
                'disk_write': 0.0
            } for _ in range(max_size_overview)], maxlen=max_size_overview)
def metric_color(color_choice):
    colorMatch = 0;
    match color_choice:
        case "cpu_usage":
            colorMatch=0;
        case "ram_usage":
            colorMatch=1;
        case "disk_read":
            colorMatch=2;
        case "disk_write":
            colorMatch=3;
        case _:
            print("This isn't a valid color name")
            print(color_choice);
            colorMatch=4;
    colors = [
    "#FF0000",
    "#0000FF",
    "#00FF00",
    "#FFFF00",
    "#FF00FF"
]
    return colors[colorMatch]
def get_color_by_resource(res_name):
    match(res_name):
        case "cpu_usage": 
            metric_color(0)
        case "ram_usage": 
            metric_color(1)
        case "disk_read": 
            metric_color(2)
        case "disk_write": 
            metric_color(3)

def darken(color,val=5):
	returnColor=[];
	a = list(color);
	for hex in a:
		returnColor.append(darkenHex(hex,val));
	returnColor="".join(str(x) for x in returnColor);
	return returnColor;
def darkenHex(hexchar,spaces):
	if hexchar=='#':
		 return hexchar;
	hexes=["0","1","2","3","4","5","6","7","8","9","A","B","C","D","E","F"]
	a = hexes.index(hexchar);
	a=max(0,a-spaces);
	a=min(15,a);
	return hexes[a];

class MainWidget(QtWidgets.QWidget):
    signal_to_main = Signal()
    selectedMonitor="CPU"
    def sendSigToMain(self):
        self.selectedMonitor=self.resource_section.selectedMonitor;
        self.signal_to_main.emit()

    def update_data(self):
        if play_overview == True:
            self.graph_section.graph.update_data()
            self.graph_section.graph.grid_widget.update_counter()
    
    def closeEvent(self, event):
        print("Application is closing")
        global collect_data_overview
        collect_data_overview = False


    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #1E1E1E;")
        self.data_timer = QTimer()
        self.data_timer.setInterval(2000)
        self.data_timer.timeout.connect(self.update_data)
        self.data_timer.start()

        self.setWindowTitle("Pulse X")

        #Instantiate Widgets
        self.resource_section = ResourceSection()
        self.graph_section = GraphSection()
        self.resource_section.signal_to_main.connect(self, self.sendSigToMain);
        #Layout
        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(self.resource_section)
        layout.addWidget(self.graph_section)

#--------------------------------------------------------------------------------------
#RESOURCE SECTION
#--------------------------------------------------------------------------------------
class ResourceList(QtWidgets.QWidget):
    def __init__(self, data):
        super().__init__()
        self.setStyleSheet("background-color: #1E1E1E;")
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        
        self.process_index = 0
        self.processes = data

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

        # Create a widget to hold the process containers
        self.container_widget = QtWidgets.QWidget()
        self.container_widget.setStyleSheet(" border: none")
        self.container_layout = QtWidgets.QVBoxLayout(self.container_widget)
        
        # Set the container widget as the scroll area's widget
        self.scroll_area.setWidget(self.container_widget)
        
        # Add the scroll area to the main layout
        layout.addWidget(self.scroll_area)           


class ResourceSection(QtWidgets.QWidget):
    signal_to_main = Signal()
    selectedMonitor = "CPU";
    
    def sendSigToMain(self):
        self.selectedMonitor=self.metricList.selectedMonitor
        self.signal_to_main.emit()
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #1E1E1E; border: 5px outset #191919;")
        self.setFixedWidth(300)

        self.title = Title("PulseX")
        self.title.setStyleSheet("color: white;")
        self.metricList = MetricList()
        self.metricList.signal_to_main.connect(self, self.sendSigToMain);

        #Layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.title)
        layout.addWidget(self.metricList)

class Title(QtWidgets.QWidget):
    def __init__(self, name):
        super().__init__()
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

        #Create Widget
        self.text = QtWidgets.QLabel(name, alignment=QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        
        font_id = QFontDatabase.addApplicationFont("./font/Exo_2/Exo2-VariableFont_wght.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        font = QFont(font_family)
        font.setPixelSize(65)
        font.setStyleStrategy(QFont.PreferAntialias)
        font.setWeight(QFont.Black)
        self.text.setFont(font)
        

        #resize widget
        self.setFixedHeight(58)
        self.setFixedWidth(300)

        #Layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.text)


class GraphSection(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        media_controls = PlayControls()
        self.graph = CompleteGraphWidget()

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(media_controls)
        layout.addWidget(self.graph)


class CompleteGraphWidget(QWidget):
    def update_data(self):
        self.graph_widget.deleteLater()
        #with lock:
        self.graph_widget = GraphWidgetsContainer(resource_deque, self)
        self.stacked_layout.addWidget(self.graph_widget)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.graph_widget.deleteLater()

        # Create widgets
        self.graph_widget = GraphWidgetsContainer(resource_deque, self)
        self.stacked_layout.addWidget(self.graph_widget)


    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: transparent;")

        #create Widgets
        self.b_widget = QtWidgets.QWidget()
        self.b_widget.setStyleSheet("border: 5px groove #191919;")
        self.graph_widget = GraphWidgetsContainer(resource_deque, self)
        self.grid_widget = ScrollingGrid()


        # Layout
        self.stacked_layout = QtWidgets.QStackedLayout(self)
        self.setLayout(self.stacked_layout)
        self.stacked_layout.setStackingMode(self.stacked_layout.StackingMode.StackAll)
        #Note: graphs_widgets_container is added on resize event

        self.stacked_layout.addWidget(self.b_widget)
        self.stacked_layout.addWidget(self.grid_widget)

        self.setLayout(self.stacked_layout)

class MetricList(QtWidgets.QWidget):
    signal_to_main = Signal()
    selectedMonitor="Hello"
    def sendDiskReadSigToMain(self):
         self.sendSigToMain("disk_read_speed_mb_s");
    def sendCPUSigToMain(self):
         self.sendSigToMain("cpu_percent");
    def sendDiskWriteSigToMain(self):
         self.sendSigToMain("disk_write_speed_mb_s");
    def sendMemorySigToMain(self):
         self.sendSigToMain("memory_mb");

    def sendSigToMain(self,resource="CPU"):
        self.selectedMonitor=resource;
        self.signal_to_main.emit()
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #1E1E1E;")
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
        self.cpu_item = MetricItem("CPU","cpu_usage","cpu_usage")
        self.memory_item = MetricItem("Memory","ram_usage","ram_usage")
        self.disk_write_item = MetricItem("Disk Write","disk_write","disk_write")
        self.disk_read_item = MetricItem("Disk Read","disk_read","disk_read")

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

class MetricItem(QtWidgets.QWidget):
    signal_to_main = Signal()
    def mousePressEvent(self, event):
        self.signal_to_main.emit()
        super().mousePressEvent(event)

    def __init__(self,textValue,color_choice,resourceName="cpu_usage"):
        super().__init__()
        self.resource=resourceName;
        color = darken(metric_color(color_choice));
        
        #Widget Creation
        self.container = QtWidgets.QFrame()
        self.container.setStyleSheet(f"background-color: {color}; border: 1px solid {color};")
        self.container.setFixedSize(256, 50)

        self.checkbox = QtWidgets.QCheckBox()
        self.checkbox.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.checkbox.setFixedSize(15, 15)
        self.checkbox.setStyleSheet("QCheckBox::indicator:checked {background-color:" + darken(str(color),-12) +" ; border: none;} QCheckBox::indicator:unchecked { background-color:" + darken(str(color),-3) +" ;border: none;  };")
        self.checkbox.stateChanged.connect(self.on_checkbox_state_changed)
        #self.checkbox.setStyleSheet("border: none")
        self.text = QtWidgets.QLabel(textValue)
        self.text.setStyleSheet("color: white; font-weight: bold; border: none")
    
        #Layout
        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.container)
        self.container_layout = QtWidgets.QHBoxLayout(self.container)
        self.container_layout.addWidget(self.checkbox)
        self.container_layout.addWidget(self.text)
    def on_checkbox_state_changed(self, state):
        print(f"Checkbox state changed: {state}")
        if state == 2:
            print('mew')
            if self.resource not in data_targets_overview:
                data_targets_overview.append(self.resource)
                
        else:
            if self.resource in data_targets_overview:
                data_targets_overview.remove(self.resource)

        
class PlayControls(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.is_playing = False
        self.button = QtWidgets.QPushButton("")
        self.button.setFixedHeight(58)
        self.button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.button.setStyleSheet("""
            QPushButton {
                background-color: #3C3C3C;
                color: white;
                border: 1px inset #3C3C3C; /* Outset border */
                padding: 10px 20px;
                border-radius: 7px; /* Adjust this value for rounder corners */
            }
            QPushButton:pressed {
                background-color: #5D5D5D; /* Adjust this color to your preferred lighter shade */
            }
        """)


        self.button.clicked.connect(self.on_button_clicked)
        self.pause_icon = QtGui.QIcon("images/pause-regular-24.png")
        self.play_icon = QtGui.QIcon("images/play-regular-24.png")

        self.button.setIcon(self.pause_icon)
        self.button.setIconSize(QtCore.QSize(32, 32))

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.button)


    def on_button_clicked(self):
        # This function will be executed when the button is clicked and set it to play or pause
        self.is_playing = not self.is_playing
        if self.is_playing:
            self.button.setIcon(self.play_icon)
        else:
            self.button.setIcon(self.pause_icon)
         
        global play_overview
        play_overview = not self.is_playing
        print(play_overview)

class GraphWidgetsContainer(QWidget):
        #processes[ [ { mem_mb } ] ]
    def __init__(self, resourceData, parent=None):
        super().__init__(parent)
        self.resize(parent.size())
        global graphs_per_pass_overview
        self.graphs_per_pass = graphs_per_pass_overview
        #print(parent.size())
        #print("SIZE1: ",self.size())
        self.resources = resourceData
        self.i = 0
        self.glow = False

        self.pix_map = QPixmap()
        self.temp_widget = QtWidgets.QWidget()
        self.temp_widget.resize(self.size())
        self.temp_widget.setStyleSheet("background-color: #070f0c;")
        
        # Layout
        self.stacked_layout = QtWidgets.QStackedLayout(self)
        self.temp_widget.setLayout(self.stacked_layout)
        self.stacked_layout.setStackingMode(self.stacked_layout.StackingMode.StackAll)
    
        # timer for graph throttling
        self.add_widget_timer = QTimer()
        self.add_widget_timer.setInterval(1000/60)
        self.add_widget_timer.timeout.connect(self.add)
        self.add()
        self.add_widget_timer.start()
        #print("-----------------------------------------------------------------------------------------------------")

    
    def add(self):  
        size = len(self.resources) - self.i
        count = 4
        for recresource in data_targets_overview:
            print("making resource graph: ");
            self.graph_widget = MainGraphWidget(self.resources,recresource)
            self.graph_widget.resize(self.size())
            self.stacked_layout.addWidget(self.graph_widget)
        self.i += count
        self.pix_map = self.temp_widget.grab()
        
        #print(len(processes_deque[59]))
        print(size);
        if self.i >= size:
            self.add_widget_timer.stop()

            #Glow Effect
            self.blur_effect = QGraphicsBlurEffect()
            self.blur_effect.setBlurRadius(20)  # Adjust the blur radius
            self.blur_label = QLabel()
            self.blur_label.resize(self.size())
            self.blur_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
            self.blur_label.setPixmap(self.pix_map)
            self.blur_label.setGraphicsEffect(self.blur_effect)
            self.blur_pixmap = self.blur_label.grab()
            self.glow = True
        self.update()
        
    def paintEvent(self, event):
        painter1 = QtGui.QPainter(self)
        painter1.drawPixmap(0, 0, self.pix_map)
        painter1.end()

        if self.glow:
            glow_painter = QtGui.QPainter(self)
            glow_painter.setOpacity(.85)
            glow_painter.setCompositionMode(QtGui.QPainter.CompositionMode_Lighten)

            glow_painter.drawPixmap(0, 0, self.blur_pixmap)
            glow_painter.end()
            
class MainGraphWidget(QWidget):
    def __init__(self, data, resource_monitor, parent=None):
        super().__init__(parent)
        self.data = data
        self.resource_data = []
        self.resource = resource_monitor
        #print(process_index)
        for time_index in range(60):
            if (len(data) >= time_index):
                print(data[time_index]);
                #print(len(data[time_index]), " ", process_index)
                self.resource_data.append(data[time_index][self.resource])
            
            else:
                self.resource_data.append(0)

        #print(data)
        
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        margin = 20
        pen = QPen(QColor( metric_color(self.resource) ), 2)
        painter.setPen(pen)

        overview_resource_max_values = {
            "cpu_usage": 10,#100,
            "ram_usage": 500,#16000, 
            "disk_read": 500,
            "disk_write": 500
        }
        overview_max_value = overview_resource_max_values[self.resource]
        scale_x = (rect.width() - 2 * margin) / (len(self.data) - 1)
        scale_y = (rect.height() - 2 * margin) / overview_max_value

        for i in range(len(self.resource_data ) - 1):
            x1 = margin + i * scale_x
            y1 = rect.height() - margin - self.resource_data[i] * scale_y
            x2 = margin + (i + 1) * scale_x
            y2 = rect.height() - margin - self.resource_data[i + 1] * scale_y
            painter.drawLine(x1, y1, x2, y2)
            #memory_mb
            #cpu_percent
        #print(self.name)


class ScrollingGrid(QWidget):
    def update_counter(self):
        self.counter += self.rect().width() // 60

    def __init__(self, parent=None):
        super().__init__(parent)
        self.counter = 0.0
        #for testing
        #self.timer = QTimer()
        #self.timer.timeout.connect(self.update_counter)
        #self.timer.start(16.67)  # 60fps 
        

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        self.margin = 20
        grid_size = 60
        offset = (-self.counter * rect.width() / 1000.2)%(grid_size) #Modulus 😎

        # Draw the grid
        pen = QPen(Qt.lightGray, .25, QtCore.Qt.DotLine)
        painter.setPen(pen)

        for x in range(self.margin, rect.width() - self.margin, grid_size):
            painter.drawLine(x + offset, self.margin, x + offset, rect.height() - self.margin)
        for y in range(self.margin, rect.height() - self.margin, grid_size):
            painter.drawLine(self.margin, y, rect.width() - self.margin, y)
        
        painter.end()


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

def gui_thread_overview():
    app = QtWidgets.QApplication([]) 
    widget = MainWidget()
    widget.resize(1024, 600)
    widget.show()
    sys.exit(app.exec())

def data_thread_overview():
    global collect_data_overview
    while collect_data_overview:
        time.sleep(2)
        add_data_overview(total_usage.get_system_usage())

def add_data_overview(new_data):
    resource_deque.append(new_data)
if __name__ == "__main__":
    
    with concurrent.futures.ThreadPoolExecutor() as executor_OV:
            #Submit the function to the executor
            future_overview = executor_OV.submit(data_thread_overview)
            executor_OV.submit(gui_thread_overview)


            future_overview.result()

    