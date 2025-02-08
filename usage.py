import psutil
import time

def list_processes():
    processes = []
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

            processes.append({
                'pid': info.get('pid'),
                'name': info.get('name'),
                'cpu_percent': info.get('cpu_percent'),
                'memory_mb': mem,
                'disk_read_mb': read_mb,
                'disk_write_mb': write_mb
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return processes

def get_gpu_usage():
    gpus = []
    try:
        import pynvml
        pynvml.nvmlInit()
        device_count = pynvml.nvmlDeviceGetCount()
        for i in range(device_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            name = pynvml.nvmlDeviceGetName(handle)
            utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
            gpus.append({
                'index': i,
                'name': name.decode('utf-8') if isinstance(name, bytes) else name,
                'gpu_utilization': utilization.gpu,
                'memory_utilization': utilization.memory
            })
        pynvml.nvmlShutdown()
    except Exception:
        pass
    return gpus 

if __name__ == "__main__":

    while True:
        start_time = time.perf_counter() 
        procs = list_processes()
        for proc in procs:
            print(f"PID: {proc['pid']}, Name: {proc['name']}, CPU: {proc['cpu_percent']}%, "
                f"Memory: {proc['memory_mb']:.2f} MB, Disk Read: {proc['disk_read_mb']:.2f} MB, "
                f"Disk Write: {proc['disk_write_mb']:.2f} MB")

        gpus = get_gpu_usage()
        if gpus:
            print("\nGPU Usage:")
            for gpu in gpus:
                print(f"GPU {gpu['index']} ({gpu['name']}): {gpu['gpu_utilization']}% GPU, "
                    f"{gpu['memory_utilization']}% Memory")
        else:
            print("\nNo GPU usage data available or NVIDIA GPU not detected.")

        elapsed_time = time.perf_counter() - start_time

        print(f"Elapsed time: {elapsed_time:.2f} seconds.")