from flask import Flask, render_template
import socket
import threading

app = Flask(__name__)

# 定义服务器地址和端口
SERVER_ADDRESS = 'localhost'
SERVER_PORT = 12346

# 创建套接字并绑定地址
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_ADDRESS, SERVER_PORT))

# 监听连接
server_socket.listen(5)
print('等待客户端连接...')

# 维护在线客户端的列表
online_clients = []

# 锁，用于在线客户端列表的访问保护
lock = threading.Lock()

# 处理客户端连接的函数
def handle_client(client_socket, client_address):
    with lock:
        online_clients.append(client_socket)

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
        client_socket.send(message)

    # 关闭连接
    with lock:
        online_clients.remove(client_socket)
    client_socket.close()
    print('客户端已断开连接:', client_address)

# 接受客户端连接并创建线程处理
def accept_connections():
    while True:
        client_socket, client_address = server_socket.accept()

        # 创建线程处理客户端连接
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()


# Flask 路由，用于显示已连接的客户端列表
@app.route('/')
def show_clients():
    return str(online_clients)


if __name__ == '__main__':
    # 启动服务器接受客户端连接的线程
    connection_thread = threading.Thread(target=accept_connections)
    connection_thread.start()

    # 运行 Flask 应用
    app.run(host='localhost', port=8000, debug=True)