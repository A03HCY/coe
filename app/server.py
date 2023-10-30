import socket
import threading
import uuid
from protocol import *


# 定义服务器地址和端口
SERVER_ADDRESS = '0.0.0.0'
SERVER_PORT = 12345
SERVER_LISTEN = 5

# 在线客户端的字典
online_clients = {}

# 锁，用于在线客户端字典的访问保护
lock = threading.Lock()

# 锁字典，用于每个客户端的访问保护
client_locks = {}

# 字典，用于让前端操作每个客户端的断开
client_ends = {}


def generate():
    # 创建套接字并绑定地址
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_ADDRESS, SERVER_PORT))

    # 设置SO_KEEPALIVE选项
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    #30秒无活动后开始发送探测包
    server_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 30)
    # 每隔10秒发送一个探测包
    server_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 10)
    # 连续发送5个探测包后仍无响应则认为连接断开
    server_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 5)

    return server_socket

# 处理客户端连接的函数
def handle_client(client_socket, client_address):
    identity = Protocol().load_stream(client_socket.recv).json
    print(identity)
    # {'Operating System': 'Linux', 'OS Version': '5.15.124-20281-g306376f9e9db', 'Architecture': ('64bit', 'ELF'), 'Computer Name': 'penguin', 'Processor': 'Unknown'}

    client_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(identity)))

    # 检查是否存在相同的 UUID
    with lock:
        if client_uuid in online_clients:
            print('重复的 UUID，断开已存在连接:', client_address)
            online_clients[client_uuid][0].close()

        online_clients[client_uuid] = [client_socket, identity]

    # 创建客户端的线程锁
    client_locks[client_uuid] = threading.Lock()
    client_ends[client_uuid]  = False

    # 处理客户端消息
    while True:
        if client_ends[client_uuid]: break

    # 关闭连接
    with lock:
        del online_clients[client_uuid]
    # 删除客户端的线程锁
    del client_locks[client_uuid]
    client_socket.close()
    print('客户端已断开连接:', client_address)

# 接受客户端连接并创建线程处理
def accept_connections():
    # 监听连接
    server_socket = generate()
    server_socket.listen(SERVER_LISTEN)
    print('等待客户端连接...')
    while True:
        client_socket, client_address = server_socket.accept()
        # 设置SO_KEEPALIVE选项
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        #30秒无活动后开始发送探测包
        client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 30)
        # 每隔10秒发送一个探测包
        client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 10)
        # 连续发送5个探测包后仍无响应则认为连接断开
        client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 5)

        print('客户端连接:', client_address)
        # 创建线程处理客户端连接
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()


connection_thread = threading.Thread(target=accept_connections)