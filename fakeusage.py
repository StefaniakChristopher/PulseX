import random
import psutil
import time
import win32api
from concurrent.futures import ThreadPoolExecutor, as_completed

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

def fake_get_usage():
    processes = []

    for _ in range(20):
        try:

            processes.append({
                'pid': random.randint(0, 1000),
                'name': "ljsldkfjds",
                'cpu_percent': 13,
                'memory_mb': 24,
                'disk_read_mb': 23,
                'disk_write_mb': 43
            })

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return processes

if __name__ == "__main__":
    while True:
        time.sleep(1)
        start_time = time.perf_counter()
        procs = fake_get_usage()
        for proc in procs:
            print(f"PID: {proc['pid']}, Name: {proc['name']}, CPU: {proc['cpu_percent']}%, "
                  f"Memory: {proc['memory_mb']:.2f} MB, Disk Read: {proc['disk_read_mb']:.2f} MB, "
                  f"Disk Write: {proc['disk_write_mb']:.2f} MB"
            )

        elapsed_time = time.perf_counter() - start_time
        print(f"Elapsed time: {elapsed_time:.2f} seconds.")