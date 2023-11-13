import platform
import psutil
import pyautogui, io
import os
from psutil._common import bytes2human
from datetime import datetime
from rich import print
import re

def join_path(base, relative):
    # 移除基础目录末尾的斜杠
    base = re.sub(r'/$', '', base)
    # 解析相对路径中的连续 ../
    parts = relative.split('/')
    stack = base.split('/')

    for part in parts:
        if part == '.':
            # 跳过 ./ 目录
            continue
        elif part == '..':
            if len(stack) > 1 or stack[0] != '':
                stack.pop()
        else:
            stack.append(part)

    if len(stack) == 0 or stack[0] == '':
        if base[0] == '.':
            stack[0] = './'
        else:
            stack[0] = '/'

    path = '/'.join(stack)
    if path == '.':
        path = './'
    
    return path

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

def screenshot(quality=50) -> io.BytesIO:
    temp = io.BytesIO()
    # 截图
    im = pyautogui.screenshot()
    # 转换为RGB模式
    compressed_image = im.convert('RGB')
    # 优化保存JPEG图像
    compressed_image.save(temp, format='jpeg', optimize=True, quality=quality)
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
    
def folder_files(directory:str) -> list:
    if not os.path.exists(directory):
        print("目录不存在")
        return []
    result = [{}, {}]  # 存储文件夹和文件信息的结果列表
    folders, files = result
    for entry in os.scandir(directory):
        if entry.is_dir():  # 处理文件夹
            subfolders, subfiles = folder_files(entry.path)
            folder_info = {
                'children': len(subfolders) + len(subfiles),
                'date': datetime.fromtimestamp(entry.stat().st_mtime).strftime('%Y-%m-%d')
            }
            folders[entry.name] = folder_info
        else:  # 处理文件
            file_info = {
                'size': entry.stat().st_size,
                'date': datetime.fromtimestamp(entry.stat().st_mtime).strftime('%Y-%m-%d'),
                'type': os.path.splitext(entry.name)[1]
            }
            files[entry.name] = file_info

    return result

def rename(path, name):
    # 检查路径是否存在
    if not os.path.exists(path):
        print(f"├ 路径 '{path}' 不存在")
        return False
    
    # 获取文件或文件夹的完整路径
    full_path = os.path.abspath(path)
    
    # 检查是否为文件夹
    if os.path.isdir(full_path):
        # 重命名文件夹
        folder_path = os.path.dirname(full_path)
        new_path = os.path.join(folder_path, name)
        try:
            os.rename(full_path, new_path)
            print(f"├ 成功将文件夹 '{full_path}' 重命名为 '{new_path}'")
            return True
        except OSError:
            print(f"├ 无法将文件夹 '{full_path}' 重命名为 '{new_path}'")
            return False
    elif os.path.isfile(full_path):
        # 重命名文件
        folder_path, file_name = os.path.split(full_path)
        new_file_path = os.path.join(folder_path, name)
        try:
            os.rename(full_path, new_file_path)
            print(f"├ 成功将文件 '{full_path}' 重命名为 '{new_file_path}'")
            return True
        except OSError:
            print(f"├ 无法将文件 '{full_path}' 重命名为 '{new_file_path}'")
            return False
    else:
        print(f"├ 提供的路径 '{full_path}' 不是有效的文件夹或文件")
        return False