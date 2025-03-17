import psutil
import time

def get_system_usage(prev_disk_io):
    # Get CPU usage
    cpu_usage = psutil.cpu_percent(interval=1)

    # Get RAM usage
    memory_info = psutil.virtual_memory()
    ram_usage = memory_info.percent

    # Get disk usage
    current_disk_io = psutil.disk_io_counters()
    disk_read = (current_disk_io.read_bytes - prev_disk_io.read_bytes) // (1024 * 1024)  # Convert bytes to MB
    disk_write = (current_disk_io.write_bytes - prev_disk_io.write_bytes) // (1024 * 1024)  # Convert bytes to MB

    return {
        "cpu_usage": cpu_usage,
        "ram_usage": ram_usage,
        "disk_read": disk_read,
        "disk_write": disk_write
    }

if __name__ == "__main__":
    while True:
        time.sleep(1)
        start_time = time.perf_counter()
        usage = get_system_usage()
        print(f"CPU Usage: {usage['cpu_usage']}%")
        print(f"RAM Usage: {usage['ram_usage']}%")
        print(f"Disk Read: {usage['disk_read']} MB/S")
        print(f"Disk Write: {usage['disk_write']} MB/S")
        elapsed_time = time.perf_counter() - start_time
        print(f"Elapsed time: {elapsed_time:.2f} seconds.")