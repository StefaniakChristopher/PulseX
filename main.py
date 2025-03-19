from PySide6.QtWidgets import QApplication, QWidget, QStackedLayout
import time
import frame1
import frame2
import usage
import concurrent.futures

class MainWindow(QWidget):
    def handle_signal(self, resource = "cpu_percent"):
        self.frame2.set_resource(resource) # set resource to be displayed
        self.layout.setCurrentIndex( not self.layout.currentIndex() ) # toggle between 0 and 1

    def __init__(self):
        super().__init__()

        # init widgets
        #self.frame1 = frame1.MainWidget()
        self.frame2 = frame2.MainWidget()

        # connect signals
        #frame1.signal_to_main.connect(self, self.handle_signal)
        self.frame2.process_section.title.signal_to_main.connect(self, self.handle_signal) 

        # create layout
        self.layout = QStackedLayout()
        #self.layout.addWidget(self.frame1)
        self.layout.addWidget(self.frame2)
        self.setLayout(self.layout)


def gui_thread():
    app = QApplication([])
    window = MainWindow()
    window.resize(1024, 600)
    window.show()
    app.exec()


def data_thread():
    while frame2.collect_data:
        time.sleep(2)
        frame2.add_data(usage.get_usages(frame2.data_targets))


def init_threads():
    with concurrent.futures.ThreadPoolExecutor() as executor:
            # Submit the function to the executor
            future = executor.submit(data_thread)
            executor.submit(gui_thread)
            future.result()


if __name__ == "__main__":    
    init_threads()
    #gui_thread()
