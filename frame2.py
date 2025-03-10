import sys
import random
import time
import usage
import signal
import concurrent.futures
#import threading
from collections import deque
from discover import list_processes
from fakeusage import fake_get_usage
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QMainWindow, QSizePolicy, QGraphicsBlurEffect # type: ignore
from PySide6.QtGui import QIcon, QFont, QPixmap, QPainter, QColor, QPen, QLinearGradient # type: ignore
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis # type: ignore
from PySide6.QtCore import QPointF, Qt, QTimer # type: ignore
from PySide6.QtGui import QFontDatabase, QFont
#from PySide6.QtWidgets import  # type: ignore

play = True
collect_data = True
data_targets = []
graphs_per_pass = 10
#lock = threading.Lock()

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
    return random.choice(colors)


def get_color_by_pid(pid):
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
    return colors[ pid // 4 % len(colors) ]

class MainWidget(QtWidgets.QWidget):
    def update_data(self):
        global play
        if play == True:
            self.graph_section.graph.update_data()
            self.graph_section.graph.grid_widget.update_counter()
    
    def closeEvent(self, event):
        print("Application is closing")
        global collect_data
        collect_data = False


    def __init__(self):
        super().__init__()

        self.setStyleSheet("background-color: #1E1E1E;")
        self.data_timer = QtCore.QTimer()
        self.data_timer.setInterval(2000)
        self.data_timer.timeout.connect(self.update_data)
        self.data_timer.start()




        self.setWindowTitle("Pulse X")

        #Instantiate Widgets
        self.process_section = ProcessSection()
        self.graph_section = GraphSection()

        #Layout
        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(self.process_section)
        layout.addWidget(self.graph_section)

#---------------------------------------------------------------------------------------------------
#                                   PROCESS SECTION
#---------------------------------------------------------------------------------------------------

all_processes = list_processes()

class ProcessSection(QtWidgets.QWidget):
    def update_data(self):
        self.processList.deleteLater()
        self.processList = ProcessList(all_processes)
        self.layout.addWidget(self.processList)

    def __init__(self):
        super().__init__()
        #self.setStyleSheet("background-color: #191919;")
        self.setStyleSheet("background-color: #1E1E1E; border: 5px outset #191919;")
        self.setFixedWidth(300)

        title = Title("RAM")
        title.setStyleSheet("color: white;")
        self.processList = ProcessList(all_processes)

        #Layout
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(title)
        self.layout.addWidget(self.processList)


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

class ProcessList(QtWidgets.QWidget):
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
        #self.scroll_area.setStyleSheet(" border: none")

        # Create a widget to hold the process containers
        self.container_widget = QtWidgets.QWidget()
        self.container_widget.setStyleSheet(" border: none")
        self.container_layout = QtWidgets.QVBoxLayout(self.container_widget)
        
        # Set the container widget as the scroll area's widget
        self.scroll_area.setWidget(self.container_widget)
        
        # Add process containers to the container widget
        
        #for process in data[time_index]:
        #    self.process_item = ProcessItem(process["name"], get_color_by_pid(int(process["pid"])))
        #    self.container_layout.addWidget(self.process_item,alignment=QtCore.Qt.AlignTop)
        
        # Add the scroll area to the main layout
        layout.addWidget(self.scroll_area)

        self.data_timer = QtCore.QTimer()
        self.data_timer.setInterval(1000/30)
        self.data_timer.timeout.connect(self.add)
        self.data_timer.start()

    def add(self):
        process = self.processes[self.process_index]
        self.process_item = ProcessItem(process, get_color_by_pid(int(process["pid"])))
        self.container_layout.addWidget(self.process_item,alignment=QtCore.Qt.AlignTop)
        self.process_index += 1

        if self.process_index >= len(self.processes):
            self.data_timer.stop()


class ProcessItem(QtWidgets.QWidget):
    def __init__(self, process, color):
        super().__init__()

        #color = random_color()
        self.process = process
        
        #self.setStyleSheet("background-color: #69C4E8;")
        #self.setFixedSize(256, 50)
        
        #Widget Creation
        self.container = QtWidgets.QFrame()
        self.container.setStyleSheet(f"background-color: #191919; border: 1px solid {color}")
        self.container.setFixedSize(256, 50)

        self.checkbox = QtWidgets.QCheckBox()
        self.checkbox.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.checkbox.setFixedSize(15, 15)
        self.checkbox.setStyleSheet("QCheckBox::indicator:checked {background-color:" + str(color) +" ; border: none;} QCheckBox::indicator:unchecked { border: none;  };")
        self.checkbox.stateChanged.connect(self.on_checkbox_state_changed)
        #self.checkbox.setStyleSheet("border: none")
        self.text = QtWidgets.QLabel(process['name'])
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
        self.folderButton.clicked.connect(self.on_button_clicked)

    
        #Layout
        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.container)
        self.container_layout = QtWidgets.QHBoxLayout(self.container)
        self.container_layout.addWidget(self.checkbox)
        self.container_layout.addWidget(self.text)
        self.container_layout.addWidget(self.folderButton)
    
    def on_checkbox_state_changed(self, state):
        print(f"Checkbox state changed: {state}")
        if state == 2:
            print('mew')
            if self.process not in data_targets:
                data_targets.append(self.process)
                
        else:
            if self.process in data_targets:
                data_targets.remove(self.process)
    
    def on_button_clicked(self):
        usage.open_file_location(self.process['exe_path'])
                


#-----------------------------------------------------------------------------------------------------
#                                        GRAPH SECTION
#-----------------------------------------------------------------------------------------------------

class GraphSection(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        media_controls = PlayControls()
        self.graph = CompleteGraphWidget()

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(media_controls)
        layout.addWidget(self.graph)


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
         
        global play
        play = not self.is_playing
        print(play)


class CompleteGraphWidget(QWidget):
    def update_data(self):
        self.graph_widget.deleteLater()
        #with lock:
        self.graph_widget = GraphWidgetsContainer(processes_deque, self)
        self.stacked_layout.addWidget(self.graph_widget)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.graph_widget.deleteLater()

        # Create widgets
        self.graph_widget = GraphWidgetsContainer(processes_deque, self)
        self.stacked_layout.addWidget(self.graph_widget)


    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: transparent;")

        #create Widgets
        self.b_widget = QtWidgets.QWidget()
        self.b_widget.setStyleSheet("border: 5px groove #191919;")
        self.graph_widget = GraphWidgetsContainer(processes_deque, self)
        self.grid_widget = ScrollingGrid()
        # self.time_line_scrubber = TimeLineScrubber()

        # Layout
        self.stacked_layout = QtWidgets.QStackedLayout(self)
        self.setLayout(self.stacked_layout)
        self.stacked_layout.setStackingMode(self.stacked_layout.StackingMode.StackAll)
        #Note: graphs_widgets_container is added on resize event
        # self.stacked_layout.addWidget(self.time_line_scrubber)
        self.stacked_layout.addWidget(self.b_widget)
        self.stacked_layout.addWidget(self.grid_widget)

        self.setLayout(self.stacked_layout)


class GraphWidgetsContainer(QWidget):
        #processes[ [ { mem_mb } ] ]
    def __init__(self, processes, parent=None):
        super().__init__(parent)
        self.resize(parent.size())
        global graphs_per_pass
        self.graphs_per_pass = graphs_per_pass
        #print(parent.size())
        #print("SIZE1: ",self.size())
        self.p = processes
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
        self.add_widget_timer = QtCore.QTimer()
        self.add_widget_timer.setInterval(1000/60)
        self.add_widget_timer.timeout.connect(self.add)
        self.add()
        self.add_widget_timer.start()
        #print("-----------------------------------------------------------------------------------------------------")

    
    def add(self):  
        size = len(processes_deque[59]) - self.i
        count = min(size, self.graphs_per_pass)
        #print("COUNT: ",count)
        
        for process_index in range(count):
            self.graph_widget = GraphWidget(self.p, process_index + self.i)
            self.graph_widget.resize(self.size())
            self.stacked_layout.addWidget(self.graph_widget)
        
        self.i += count
        self.pix_map = self.temp_widget.grab()
        
        #print(len(processes_deque[59]))
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


class GraphWidget(QWidget):
    def __init__(self, data, process_index, parent=None):
        super().__init__(parent)
        self.data = data
        self.process_data = []
        self.pid = 0
        self.name = ""
        #print(process_index)

        for time_index in range(60):
            if (len(data[time_index]) > process_index):
                #print(len(data[time_index]), " ", process_index)
                self.process_data.append(data[time_index][process_index])
                self.pid = int( data[time_index][process_index]["pid"] )
                self.name = data[time_index][process_index]["name"]
            
            else:
                self.process_data.append({'pid': self.pid,
                'name': self.name,
                'cpu_percent': 0.0,
                'memory_mb': 0.0,
                'disk_read_mb': 0.0,
                'disk_write_mb': 0.0
            })

        #print(data)
        
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QtGui.QPainter(self)
        #painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        margin = 20
        pen = QPen(QColor( get_color_by_pid( int( self.pid ) ) ), 2)
        painter.setPen(pen)
        
        max_value = 500.0#max(self.data)
        scale_x = (rect.width() - 2 * margin) / (len(self.data) - 1)
        scale_y = (rect.height() - 2 * margin) / max_value

        for i in range(len(self.process_data ) - 1):
            x1 = margin + i * scale_x
            y1 = rect.height() - margin - self.process_data[i]["memory_mb"] * scale_y
            x2 = margin + (i + 1) * scale_x
            y2 = rect.height() - margin - self.process_data[i + 1]["memory_mb"] * scale_y
            painter.drawLine(x1, y1, x2, y2)
            #memory_mb
            #cpu_percent
        #print(self.name)


class ScrollingGrid(QWidget):
    def update_counter(self):
        #print(self.rect().width() / 60)
        self.counter += self.rect().width() // 60 #1
        #print("!!!")
        #self.update() 

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
        
        painter.end()


# class TimeLineScrubber(QtWidgets.QWidget):
#     def resizeEvent(self, event):
#         super().resizeEvent(event)
#         #Math Stuff for keeping the TimeScrubber in the correct position when resizing window 🤓
#         ratio = (self.selected_time / self.old_width)
#         self.selected_time = round(event.size().width() * ratio)
#         self.time_scrubber.move(self.selected_time,0 )
#         self.old_width = event.size().width()

#     def __init__(self):
#         super().__init__()
#         self.selected_time = 1
#         self.old_width = self.width()
#         self.is_clicked = False

#         #Create Widget
#         self.time_scrubber = TimeScrubber()#QtWidgets.QPushButton(" ")
#         self.time_scrubber.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))
#         self.time_scrubber.setFixedWidth(4)

#         #Layout
#         layout = QtWidgets.QHBoxLayout(self)
#         layout.setContentsMargins(0, 0, 0, 0)
#         layout.addWidget(self.time_scrubber)
#         self.setLayout(layout)

#     def mouseMoveEvent(self, event):
#         if self.time_scrubber.mouse_detector.is_mouse_over and self.is_clicked:
#             #print()
#             pos = event.position()
#             if pos.x() < self.width() and pos.x() > 0:
#                 self.selected_time = round(pos.x()) - 2
#                 #print(self.selected_time)
#                 self.time_scrubber.move(self.selected_time,0 )

    
#     def mouseReleaseEvent(self, event):
#         super().mouseReleaseEvent(event)
#         self.is_clicked = False
#         self.time_scrubber.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))
#         #self.test()
    
#     def mousePressEvent(self, event):
#         super().mousePressEvent(event)
#         self.is_clicked = True
#         self.time_scrubber.setCursor(QtGui.QCursor(QtCore.Qt.ClosedHandCursor))
        #self.test()
    
    #def time_scrubber_released(self):
        #self.is_clicked = False
        #self.test()
    

    #def test(self):
        #print(self.is_clicked)


# class TimeScrubber(QtWidgets.QWidget):
#     def __init__(self):
#         super().__init__()
#         self.mouse_detector = MouseDetector()

#         layout = QVBoxLayout()
#         layout.setContentsMargins(0, 0, 0, 0)
#         layout.addWidget(self.mouse_detector)
#         self.setLayout(layout)


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


# Create a deque with a fixed size
max_size = 60
processes_deque = deque([[ {'pid': -1,
                'name': "null",
                'cpu_percent': 0.0,
                'memory_mb': 0.0,
                'disk_read_mb': 0.0,
                'disk_write_mb': 0.0
            }, {'pid': -2,
                'name': "null",
                'cpu_percent': 0.0,
                'memory_mb': 0.0,
                'disk_read_mb': 0.0,
                'disk_write_mb': 0.0
            } ] for _ in range(max_size)], maxlen=max_size)



#processed_data = []

def refactor_data(data):
    process_array = []
    refactored_data = []

    time_index = 0
    for process_index in range(len(data[time_index])):
        for i in range(60):
            process_array.append(data[i][process_index])
        
        #print(time_index)
        time_index += 1

        

        refactored_data.append(process_array[:])
        process_array = []
    
    return refactored_data

def gui_thread():
    app = QtWidgets.QApplication([]) 
    widget = MainWidget()
    widget.resize(1024, 600)
    widget.show()
    sys.exit(app.exec())


def data_thread():
    global collect_data
    while collect_data:
        time.sleep(2)
        processes_deque.append(usage.get_usages(data_targets))


if __name__ == "__main__":
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
            #Submit the function to the executor
            future = executor.submit(data_thread)
            executor.submit(gui_thread)


            future.result()
   