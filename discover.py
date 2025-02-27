import psutil
import time
import win32api
from usage import get_friendly_name

def list_processes():
    seen = set()
    processes = []
    for proc in psutil.process_iter(['pid']):
        try:
            friendly_name = get_friendly_name(proc)
            if friendly_name in seen or friendly_name == "":
                continue
            info = proc.info
            

            processes.append({
                'pid': info.get('pid'),
                'name': friendly_name,
            })

            seen.add(friendly_name)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return processes


if __name__ == "__main__":

    while True:
        time.sleep(1)
        start_time = time.perf_counter() 
        procs = list_processes()
        # for proc in procs:
        #     print(f"PID: {proc['pid']}, Name: {proc['name']} ")
        print(procs)

        elapsed_time = time.perf_counter() - start_time

        print(f"Elapsed time: {elapsed_time:.2f} seconds.")