import platform
import psutil
import pyautogui, io
from psutil._common import bytes2human


def get_system_info():
    try:
        system_info = {
            'Operating System': platform.system(),
            'OS Version': platform.release(),
            'Architecture': platform.architecture(),
            'Computer Name': platform.node(),
            'Processor': platform.processor()
        }
        system_info = {k: 'Unknown' if v == '' else v for k, v in system_info.items()}
        return system_info
    except:
        return 'Unable to get system information'

def get_memory_info():
    try:
        mem = psutil.virtual_memory()
        memory = {
            'Total': mem.total,
            'Used': mem.used,
            'Free': mem.free
        }
        return memory
    except:
        return 'Unable to get memory information'

def get_cpu_info():
    try:
        cpu = {
            'Logical CPU': psutil.cpu_count(),
            'CPU': psutil.cpu_count(logical=False),
            'CPU Percent': (str(psutil.cpu_percent(1))) + '%',
            'Frequency': psutil.cpu_freq()[0]
        }
        return cpu
    except:
        return 'Unable to get cpu information'

def used_for_singup():
    try:
        system = get_system_info()
        memory = get_memory_info()['Total']
        cpu    = get_cpu_info()['Frequency']
        system.update({
            'Memory': memory,
        })
        return system
    except:
        return 'Unable to get information'

def screenshot() -> io.BytesIO:
    im = pyautogui.screenshot()
    temp = io.BytesIO()
    im.save(temp, format='png')
    return temp

def get_disk_space(path='C:'):
    usage = psutil.disk_usage(path)
    space_total = bytes2human(usage.total)
    space_used = bytes2human(usage.used)
    space_free = bytes2human(usage.free)
    space_used_percent = bytes2human(usage.percent)
    return  space_total, space_used, space_free, space_used_percent

def get_disk():
    data = [list(i) for i in psutil.disk_partitions()]
    return data
    
