from flask import Blueprint, jsonify, request, send_file, Response, make_response, current_app, stream_with_context
from server import *
import mimetypes
import json, base64, os

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

@check_client
def save_file(client_uuid:str):
    pass


def base64_decode(text):
    # 替换特殊字符
    text = text.replace('-', '+').replace('_', '/')
    # 填充缺失的字符
    padding = len(text) % 4
    if padding > 0:
        text += '=' * (4 - padding)
    # 解码 Base64 字符串
    decoded_bytes = base64.b64decode(text)
    try:
        # 使用 UTF-8 编解码器将字节解码为字符串
        decoded_string = decoded_bytes.decode('utf-8')
    except UnicodeDecodeError:
        # 如果 UTF-8 解码失败，则回退到使用 Latin-1 编解码器
        decoded_string = decoded_bytes.decode('latin-1')
    return decoded_string


web_api = Blueprint('api', __name__)

@web_api.route('/upload', methods=['POST'])
def upload_file():
    uploaded_file = request.files['file']
    client_uuid = request.values.get('uuid', '')
    if uploaded_file.filename == '':
        return ''
    return ''

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
    data = base64_decode(data)
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

'''@web_api.route('/trans_file', methods=['GET'])
def trans_file():
    client_uuid = request.args.get('uuid', '')
    directory = request.args.get('directory', '')
    data = base64_decode(directory)
    respond = oneline_command(client_uuid, 'trans_file', {
        'directory': data
    })
    file_name = os.path.basename(directory)
    respons = make_response(respond.meta)
    mime_type = mimetypes.guess_type(file_name)[0]
    respons.headers['Content-Disposition'] = 'attachment; filename={}'.format(file_name.encode().decode('latin-1'))
    return respons'''

@web_api.route('/remove_file', methods=['GET'])
def remove_file():
    client_uuid = request.args.get('uuid', '')
    directory = request.args.get('directory', '')
    data = base64_decode(directory)
    respond = oneline_command(client_uuid, 'remove_file', {
        'directory': data
    })
    return ''

@web_api.route('/rename_path_file', methods=['GET'])
def rename_path_file():
    client_uuid = request.args.get('uuid', '')
    directory = request.args.get('directory', '')
    new = request.args.get('new', '')
    data = base64_decode(directory)
    new = base64_decode(new)
    respond = oneline_command(client_uuid, 'rename_path_file', {
        'directory': data,
        'new': new
    })
    return str(respond.json.get('result', 'unknow'))

@web_api.route('/trans_file')
def trans_file():
    client_uuid = request.args.get('uuid', '')
    directory = request.args.get('directory', '')
    seek = request.args.get('seek', '')
    byte = request.args.get('byte', '')
    data = base64_decode(directory)
    print(data)
    if seek and byte:
        file_info = oneline_command(client_uuid, 'folder_files', {
            'directory': os.path.dirname(data)
        })
        file_info = file_info.json['file_list'][1].get(os.path.split(data)[1])
        file_size = file_info['size']
        print(seek, '-', byte, '-', seek+byte, '/', file_size)
        respond = oneline_command(client_uuid, 'read_file', {
            'directory': data,
            'seek': seek,
            'byte': byte
        })
        return respond.meta
    else:
        # 不支持断点续传，直接发送整个文件
        respond = oneline_command(client_uuid, 'trans_file', {
            'directory': data
        })
        file_name = os.path.basename(directory)
        respons = make_response(respond.meta)
        mime_type = mimetypes.guess_type(file_name)[0]
        respons.headers['Content-Disposition'] = 'attachment; filename={}'.format(file_name.encode().decode('latin-1'))
        return respons