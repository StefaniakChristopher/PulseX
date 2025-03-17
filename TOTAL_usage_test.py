import time

import psutil
from total_usage import get_system_usage


while True:
    disk_io = psutil.disk_io_counters()
    time.sleep(1)
    metrics = get_system_usage(disk_io)
    print(metrics)