import socket
import threading
from flask import Flask, jsonify
from protocol import *


# 定义服务器地址和端口
SERVER_ADDRESS = 'localhost'
SERVER_PORT = 12345

# Flask应用程序
app = Flask(__name__)

# 线客户端的列表
online_clients = []

# 锁，用于在线客户端列表的访问保护
lock = threading.Lock()


def generate():
    # 创建套接字并绑定地址
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_ADDRESS, SERVER_PORT))

    # 设置SO_KEEPALIVE选项
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    # 60秒无活动后开始发送探测包
    server_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 60)
    # 每隔10秒发送一个探测包
    server_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 10)
    # 连续发送5个探测包后仍无响应则认为连接断开
    server_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 5)

    return server_socket

# 处理客户端连接的函数
def handle_client(client_socket, client_address):
    with lock:
        online_clients.append(client_socket)

    identity = Protocol().load_stream(client_socket.recv).json
    print(identity)

    # 处理客户端消息
    while True:
        try:
            message = client_socket.recv(1024)
            if message:
                # 在服务端打印客户端发送的消息
                print('客户端消息:', message.decode())
            else:
                break
        except Exception as e:
            print('处理客户端消息出错:', e)
            break

    # 关闭连接
    with lock:
        online_clients.remove(client_socket)
    client_socket.close()
    print('客户端已断开连接:', client_address)

# 接受客户端连接并创建线程处理
def accept_connections():
    # 监听连接
    server_socket = generate()
    server_socket.listen(5)
    print('等待客户端连接...')
    while True:
        client_socket, client_address = server_socket.accept()

        print('客户端连接:', client_address)
        # 创建线程处理客户端连接
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()

# 路由，用于获取在线客户端列表
@app.route('/online_clients', methods=['GET'])
def get_online_clients():
    if not connection_thread.is_alive(): return 'Server is not running.'
    with lock:
        client_addresses = [client_socket.getpeername() for client_socket in online_clients]
    return jsonify(client_addresses)

# 路由，用于启动accept_connections线程
@app.route('/start_server', methods=['GET'])
def start_server():
    if connection_thread.is_alive():
        return 'Server is already running.'
    else:
        connection_thread.start()
        return 'Server started.'



if __name__ == '__main__':
    # 启动服务器接受客户端连接的线程
    connection_thread = threading.Thread(target=accept_connections)

    # 启动Flask应用程序
    app.run(host='0.0.0.0', port=5000)