import psutil
import time
import win32api
import subprocess

# Global dictionary to store previous disk I/O counters for each process
prev_disk_io = {}

def get_exe_info(exe_path):
    """Retrieve version info from an executable."""
    try:
        info = win32api.GetFileVersionInfo(exe_path, "\\")
        # Read the language and codepage
        lang, codepage = win32api.GetFileVersionInfo(exe_path, "\\VarFileInfo\\Translation")[0]
        str_info = {}
        for key in ("FileDescription", "ProductName"):
            str_key = "\\StringFileInfo\\%04X%04X\\%s" % (lang, codepage, key)
            str_info[key] = win32api.GetFileVersionInfo(exe_path, str_key)
        return str_info
    except Exception:
        return {}

def get_friendly_name(proc, exe_path):
    """Return the friendly name for a process, using version info if available."""
    try:
        info = get_exe_info(exe_path)
        # Prefer FileDescription, then ProductName; otherwise fallback to process name.
        if info.get("FileDescription"):
            return info["FileDescription"]
        elif info.get("ProductName"):
            return info["ProductName"]
    except Exception:
        pass
    return proc.name()

def get_usages(proc_info_list):
    global prev_disk_io
    seen = set()
    processes = []
    cpu_count = psutil.cpu_count(logical=True)  # number of logical cores

    proc_ids = [proc_info['pid'] for proc_info in proc_info_list]
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
        try:
            if proc.info['pid'] not in proc_ids:
                continue

            friendly_name = get_friendly_name(proc, proc.exe())
            if friendly_name in seen:
                continue

            info = proc.info
            mem = info.get('memory_info').rss / (1024 * 1024) if info.get('memory_info') else 0

            # Get disk I/O counters per process (read and write speeds in MB/s)
            try:
                io = proc.io_counters()
                prev_io = prev_disk_io.get(proc.info['pid'], io)
                read_speed = (io.read_bytes - prev_io.read_bytes) / (1024 * 1024)  # Convert bytes to MB
                write_speed = (io.write_bytes - prev_io.write_bytes) / (1024 * 1024)  # Convert bytes to MB
                prev_disk_io[proc.info['pid']] = io  # Update previous I/O counters
            except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
                read_speed = write_speed = 0

            raw_cpu = info.get('cpu_percent')
            normalized_cpu = raw_cpu / cpu_count

            processes.append({
                'pid': info.get('pid'),
                'name': friendly_name,
                'cpu_percent': normalized_cpu,
                'memory_mb': mem,
                'disk_read_speed_mb_s': read_speed,
                'disk_write_speed_mb_s': write_speed
            })

            seen.add(friendly_name)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return processes

def open_file_location(exe_path):
    try:
        subprocess.run(['explorer', '/select,', exe_path])
    except Exception:
        print("Could not find: ", exe_path)
        pass

if __name__ == "__main__":
    while True:
        time.sleep(1)
        start_time = time.perf_counter()
        procs = get_usages([{'pid': 0, 'name': 'System Idle Process'}, {'pid': 4, 'name': 'System'}])
        for proc in procs:
            print(f"PID: {proc['pid']}, Name: {proc['name']}, CPU: {proc['cpu_percent']}%, "
                  f"Memory: {proc['memory_mb']:.2f} MB, Disk Read Speed: {proc['disk_read_speed_mb_s']:.2f} MB/s, "
                  f"Disk Write Speed: {proc['disk_write_speed_mb_s']:.2f} MB/s"
                  )

        elapsed_time = time.perf_counter() - start_time
        print(f"Elapsed time: {elapsed_time:.2f} seconds.")