from collections import deque
import time
from usage import list_processes


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


while True:
    time.sleep(2)
    processes_deque.append(list_processes())

    print(processes_deque)

