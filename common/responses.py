RESPONSE_SIZE_IN_BYTES = 2
OK_RESPONSE_CODE = 200
BAD_REQUEST_RESPONSE_CODE = 400
NOT_FOUND_RESPONSE_CODE = 404
SERVICE_UNAVAILABLE_RESPONSE_CODE = 503

def respond_ok(clientsocket, close_socket=True):
    respond(clientsocket, OK_RESPONSE_CODE, close_socket)

def respond_bad_request(clientsocket):
    respond(clientsocket, BAD_REQUEST_RESPONSE_CODE)

def respond_not_found(clientsocket):
    respond(clientsocket, NOT_FOUND_RESPONSE_CODE)

def respond_service_unavaliable(clientsocket):
    respond(clientsocket, SERVICE_UNAVAILABLE_RESPONSE_CODE)

def respond(clientsocket, response_code, close_socket=True):
    clientsocket.send_int(response_code, RESPONSE_SIZE_IN_BYTES)
    if close_socket:
        clientsocket.close()
