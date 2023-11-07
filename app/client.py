from tools.protocol import *
import socket, time
import tools

# 定义服务器地址和端口
SERVER_ADDRESS = 'localhost'
SERVER_PORT = 12345

# 创建套接字并连接服务器
def connect_to_server():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_ADDRESS, SERVER_PORT))
    identity = Protocol(extension='signup').upmeta(tools.used_for_singup())
    identity.create_stream(client_socket.send)
    print('已连接到服务器')
    return client_socket

def read_file(file_path):
    try:
        with open(file_path, 'rb') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        print(f"文件 '{file_path}' 不存在.")
    except IOError:
        print(f"读取文件 '{file_path}' 时发生错误.")

def handle(client_socket):
    # 从用户输入获取请求
    request = Protocol().load_stream(client_socket.recv)
    respons = {}
    
    command = request.extn
    print(command)
    
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
        print('|--> 流传输, 质量:', quality)
        while True:
            respons = Protocol(extension='response')
            respons.meta = tools.screenshot(quality).getvalue()
            respons.create_stream(client_socket.send)
            request = Protocol().load_stream(client_socket.recv) # if recv
    elif command == 'folder_files':
        directory = request.json.get('directory')
        if directory:
            file_list = tools.folder_files(directory)
            respons = {'file_list': file_list}
        else:
            respons = {'error': 'Missing directory parameter'}
    elif command == 'trans_file':
        directory = request.json.get('directory')
        if directory:
            respons = read_file(directory)
        else:
            respons = {'error': 'Missing directory parameter'}
    else:
        respons = {'error': 'Unknown command'}
        
    Protocol(extension='response').upmeta(respons).create_stream(client_socket.send)

def main_loop():
    while True:
        try:
            client_socket = connect_to_server()
            while True:
                handle(client_socket)
                print('|--> sended')
        except (ConnectionResetError, ConnectionRefusedError) as e:
            print('连接已断开，正在尝试重新连接...')
            time.sleep(5)  # 等待5秒后重新连接
        except (struct.error, ConnectionAbortedError) as e:
            print('服务端要求的重置连接...')

main_loop()