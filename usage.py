import psutil
import time
import win32api

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


def get_friendly_name(proc):
    """Return the friendly name for a process, using version info if available."""
    try:
        exe_path = proc.exe()  # Get the process executable path
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
    seen = set()
    processes = []
    cpu_count = psutil.cpu_count(logical=True)  # number of logical cores

    proc_ids = [proc_info['pid'] for proc_info in proc_info_list]
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
        try:
            if proc.info['pid'] not in proc_ids:
                continue

            friendly_name = get_friendly_name(proc)
            if friendly_name in seen:
                continue

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
                'name': friendly_name,
                'cpu_percent': normalized_cpu,
                'memory_mb': mem,
                'disk_read_mb': read_mb,
                'disk_write_mb': write_mb
            })

            seen.add(friendly_name)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return processes


if __name__ == "__main__":

    while True:
        time.sleep(1)
        start_time = time.perf_counter() 
        procs = get_usages([{'pid': 0, 'name': 'System Idle Process'}, {'pid': 4, 'name': 'System'}])
        for proc in procs:
            print(f"PID: {proc['pid']}, Name: {proc['name']}, CPU: {proc['cpu_percent']}%, "
                f"Memory: {proc['memory_mb']:.2f} MB, Disk Read: {proc['disk_read_mb']:.2f} MB, "
                f"Disk Write: {proc['disk_write_mb']:.2f} MB"
            )

        elapsed_time = time.perf_counter() - start_time

        print(f"Elapsed time: {elapsed_time:.2f} seconds.")