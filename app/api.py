from server import *

no_result = Protocol(extension='no_result')

def check_client_command(func):
    def wrapper(client_uuid:str, command:str):
        if not connection_thread.is_alive():
            return no_result
        if not is_alive(client_uuid):
            return no_result
        return func(client_uuid, command)
    return wrapper

def check_client(func):
    def wrapper(client_uuid):
        if not connection_thread.is_alive():
            return no_result
        if not is_alive(client_uuid):
            return no_result
        return func(client_uuid)
    return wrapper

@check_client_command
def oneline_command(client_uuid:str, command:str) -> Protocol:
    client_socket = online_clients[client_uuid][0]
    with client_locks[client_uuid]:
        client_status[client_uuid] = command
        Protocol(extension=command).create_stream(client_socket.send)
        respond = Protocol().load_stream(client_socket.recv)
        client_status[client_uuid] = ''
    return respond