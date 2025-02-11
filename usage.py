import psutil
import time

def list_processes():
    processes = []
    cpu_count = psutil.cpu_count(logical=True)  # number of logical cores
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
        try:
            info = proc.info
            mem = info.get('memory_info').rss / (1024 * 1024) if info.get('memory_info') else 0

            # Get disk I/O counters per process (read and write in MB)
            try:
                io = proc.io_counters()
                read_mb = io.read_bytes / (1024 * 1024)
                write_mb = io.write_bytes / (1024 * 1024)
            except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
                read_mb = write_mb = 0

            raw_cpu = info.get('cpu_percent')
            normalized_cpu = raw_cpu / cpu_count

            processes.append({
                'pid': info.get('pid'),
                'name': info.get('name'),
                'cpu_percent': normalized_cpu,
                'memory_mb': mem,
                'disk_read_mb': read_mb,
                'disk_write_mb': write_mb
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return processes


if __name__ == "__main__":

    while True:
        time.sleep(1)
        start_time = time.perf_counter() 
        procs = list_processes()
        for proc in procs:
            print(f"PID: {proc['pid']}, Name: {proc['name']}, CPU: {proc['cpu_percent']}%, "
                f"Memory: {proc['memory_mb']:.2f} MB, Disk Read: {proc['disk_read_mb']:.2f} MB, "
                f"Disk Write: {proc['disk_write_mb']:.2f} MB"
            )

        elapsed_time = time.perf_counter() - start_time

        print(f"Elapsed time: {elapsed_time:.2f} seconds.")