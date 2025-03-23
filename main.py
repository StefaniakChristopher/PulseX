from PySide6.QtWidgets import QApplication, QWidget, QStackedLayout
import time
import frame1
import frame2
import usage
import concurrent.futures
import random

class MainWindow(QWidget):

    
    def handle_sig_one(self,resource = "hi"):
        print("Hello");
    def handle_signal(self, resource = "cpu_percent"):
        self.frame2.set_resource(resource) # set resource to be displayed
        self.layout.setCurrentIndex( not self.layout.currentIndex() ) # toggle between 0 and 1

    def __init__(self):
        super().__init__()
        print("Check 1");
	#data to generate, remove later
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
        print("check 2");
        proccess_array = []
        for i in range(10):
            print(i);
            random.shuffle(data_array)
            proccess_array.append(data_array[:]) #shallow copy
	
        print("check 3");
        # init widgets
        self.frame1 = frame1.MainWidget(proccess_array)
        #self.frame2 = frame2.MainWidget()
        print("check 4");
        # connect signals
        self.frame1.signal_to_main.connect(self, self.handle_sig_one)
        #self.frame2.process_section.title.signal_to_main.connect(self, self.handle_signal) 
        print("check 5");
        # create layout
        self.layout = QStackedLayout()
        self.layout.addWidget(self.frame1)
        #self.layout.addWidget(self.frame2)
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
