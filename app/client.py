from protocol import *
import socket
import tools

# 定义服务器地址和端口
SERVER_ADDRESS = 'localhost'
SERVER_PORT = 12345

# 创建套接字并连接服务器
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_ADDRESS, SERVER_PORT))
print('已连接到服务器')

identity = Protocol(extension='signup').upmeta(tools.used_for_singup())
identity.create_stream(client_socket.send)

# 不断发送请求
while True:
    # 从用户输入获取请求
    request = Protocol().load_stream(client_socket.recv)

    Protocol(extension='response').upmeta(request.meta).create_stream(client_socket.send)

# 关闭连接
client_socket.close()
print('已断开连接')