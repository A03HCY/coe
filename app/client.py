import socket

# 定义服务器地址和端口
SERVER_ADDRESS = 'localhost'
SERVER_PORT = 12344

# 创建套接字并连接服务器
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_ADDRESS, SERVER_PORT))
print('已连接到服务器')

# 不断发送请求
while True:
    # 从用户输入获取请求
    request = input('请输入信息：')

    # 发送请求
    client_socket.send(request.encode())

    # 接收并显示服务器的响应
    response = client_socket.recv(1024)
    print('服务器响应:', response.decode())

    # 检查是否退出
    if request.lower() == 'quit':
        break

# 关闭连接
client_socket.close()
print('已断开连接')