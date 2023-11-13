from tools.protocol import *
import socket, time, os
import tools

# 定义服务器地址和端口
SERVER_ADDRESS = 'localhost'
SERVER_PORT = 12345

ROOT_PATH = 'D:/Users/32069/Downloads'

# 创建套接字并连接服务器
def connect_to_server():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_ADDRESS, SERVER_PORT))
    identity = Protocol(extension='signup').upmeta(tools.used_for_singup())
    identity.create_stream(client_socket.send)
    print('├ 已连接到服务器')
    return client_socket

def justify_path(path):
    return os.path.join(ROOT_PATH, tools.join_path('./', path))

def read_file(file_path):
    try:
        with open(file_path, 'rb') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        print(f"文件 '{file_path}' 不存在.")
    except IOError:
        print(f"读取文件 '{file_path}' 时发生错误.")

def save_file(client_socket, data:Protocol):
    directory = justify_path(data.json.get('directory', ''))
    file_name = data.json.get('file_name', 'temp.file')
    if not os.path.isdir(directory):
        data.ignore_stream(client_socket.recv)
        return
    with open(os.path.join(directory, file_name), 'wb') as f:
        data.convet_full_io_stream(client_socket.recv, f.write, save_head=False)



def handle(client_socket):
    # 从用户输入获取请求
    request = Protocol().load_stream(client_socket.recv)
    respons = {}
    
    command = request.extn
    print('○', command)
    
    if command == 'cpu_status':
        respons = tools.get_cpu_info()
    
    elif command == 'memory_status':
        respons = tools.get_memory_info()
    
    elif command == 'screenshot':
        respons = Protocol(extension='response')
        respons.meta = tools.screenshot(100).getvalue()
        respons.create_stream(client_socket.send)
        return
    
    elif command == 'screen_stream':
        quality = request.json.get('quality', 0)
        try: quality = int(quality)
        except: quality = 50
        print('├ 流传输, 质量:', quality)
        while True:
            respons = Protocol(extension='response')
            respons.meta = tools.screenshot(quality).getvalue()
            respons.create_stream(client_socket.send)
            request = Protocol().load_stream(client_socket.recv) # if recv
    
    elif command == 'folder_files':
        directory = justify_path(request.json.get('directory', ''))
        if os.path.isdir(directory):
            file_list = tools.folder_files(directory)
            respons = {'file_list': file_list}
        else:
            respons = {'error': 'Missing directory parameter'}
    
    elif command == 'trans_file':
        directory = justify_path(request.json.get('directory', ''))
        if os.path.isfile(directory):
            respons = Protocol(extension='response')
            respons.meta = read_file(directory)
            respons.create_stream(client_socket.send)
            return
        else:
            respons = {'error': 'Missing directory parameter'}
    
    elif command == 'remove_file':
        directory = justify_path(request.json.get('directory', ''))
        if os.path.isfile(directory):
            try:
                os.remove(directory)
                time.sleep(0.5)
            except:pass
    
    elif command == 'save_file':
        save_file(client_socket, request)
    
    # read_file write_file 用于大文件操作
    elif command == 'read_file':
        try:
            directory = justify_path(request.json.get('directory', ''))
            seek = int(request.json.get('seek', 0))
            byte = int(request.json.get('byte', 0))
        except:
            Protocol(extension='args_error').create_stream(client_socket.send)
            return
        if not os.path.isfile(directory):
            Protocol(extension='path_error').create_stream(client_socket.send)
            return
        size = os.path.getsize(directory)
        try:
            with open(directory, 'rb') as f:
                if seek > size: pass
                elif seek + byte > size:
                    meta = f.read(size - seek)
                else:
                    meta = f.read(byte)
            Protocol(meta=meta, extension='read_file_result').create_stream(client_socket.send)
        except:
            Protocol(extension='io_error').create_stream(client_socket.send)
        return
    
    elif command == 'write_file':
        directory = justify_path(request.json.get('directory', ''))
        if not os.path.isfile(directory):
            Protocol(extension='path_error').create_stream(client_socket.send)
        try:
            with open(directory, 'wb') as f:
                f.write(request.meta)
            Protocol(extension='ok').create_stream(client_socket.send)
        except:
            Protocol(extension='io_error').create_stream(client_socket.send)
        return
    
    elif command == 'rename_path_file':
        directory = justify_path(request.json.get('directory', ''))
        new = request.json.get('new', '')
        if new == '' or new.isspace():
            respons['result'] = False
        else:
            respons['result'] = tools.rename(directory, new)
        time.sleep(0.5)
    
    else:
        respons = {'error': 'Unknown command'}
        
    Protocol(extension='response').upmeta(respons).create_stream(client_socket.send)

def main_loop():
    while True:
        try:
            client_socket = connect_to_server()
            while True:
                handle(client_socket)
                print('├ sended')
        except (ConnectionResetError, ConnectionRefusedError) as e:
            print('○ 连接已断开，正在尝试重新连接...')
            time.sleep(5)  # 等待5秒后重新连接
        except (struct.error, ConnectionAbortedError) as e:
            print('├ 服务端要求的重置连接...')

main_loop()