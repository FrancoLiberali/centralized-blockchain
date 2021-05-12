import socket

MAXIMUM_CHUNK_RECEIVE = 2048

class SafeTCPSocket:
    def __init__(self, sock = None):
        if sock == None:
            self.sock = socket.socket(
                family=socket.AF_INET, type=socket.SOCK_STREAM)
        else:
            self.sock = sock

    @classmethod
    def newServer(cls, port):
        safe_socket = cls()
        # bind the socket to this host and a port
        safe_socket.sock.bind(('', port))
        # become a server socket
        # TODO DUDA que poner en este numero y que pasa si se llena: que se loggee lo correspodiente
        safe_socket.sock.listen(5)
        return safe_socket

    @classmethod
    def newClient(cls, server_host, server_port):
        safe_socket = cls()
        safe_socket.sock.connect((server_host, server_port))
        return safe_socket

    def accept(self):
        (client_socket, _) = self.sock.accept()
        return SafeTCPSocket(client_socket)

    def send(self, msg):
        total_sent = 0
        while total_sent < len(msg):
            sent = self.sock.send(msg[total_sent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            total_sent = total_sent + sent

    def send_int(self, int_to_send, len_in_bytes):
        # TODO usar este codigo en varios lados que está repetido
        int_bytes = int_to_send.to_bytes(
            len_in_bytes, byteorder='big', signed=False
        )
        self.sock.send(int_bytes)

    def recv(self, msg_len):
        chunks = []
        bytes_recd = 0
        while bytes_recd < msg_len:
            chunk = self.sock.recv(
                min(msg_len - bytes_recd, MAXIMUM_CHUNK_RECEIVE))
            if chunk == b'':
                raise RuntimeError("socket connection broken")
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)
        return b''.join(chunks)

    def recv_int(self, int_len_in_bytes):
        # TODO usar este codigo en varios lados que está repetido
        int_bytes = self.recv(int_len_in_bytes)
        return int.from_bytes(int_bytes, byteorder='big', signed=False)

    def close(self):
        return self.sock.close()
