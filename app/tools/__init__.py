import platform
import psutil


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

'''system_info = get_system_info()
if isinstance(system_info, dict):
    for key, value in system_info.items():
        print(f"{key}: {value}")
else:
    print(system_info)'''


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

#print(get_memory_info())


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