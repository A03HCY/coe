from server import *

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
def oneline_command(client_uuid:str, command:str) -> Protocol:
    client_socket = online_clients[client_uuid][0]
    with client_locks[client_uuid]:
        client_status[client_uuid] = command
        Protocol(extension=command).create_stream(client_socket.send)
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