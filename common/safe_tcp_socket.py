import socket

MAXIMUM_CHUNK_RECEIVE = 2048

class SafeTCPSocket:
    def __init__(self):
        self.sock = socket.socket(
            family=socket.AF_INET, type=socket.SOCK_STREAM)

    @classmethod
    def newServer(cls, port):
        safe_socket = cls()
        # bind the socket to this host and a port
        safe_socket.sock.bind(('', port))
        # become a server socket
        # TODO que poner en este numero y que pasa si se llena
        safe_socket.sock.listen(5)
        return safe_socket

    @classmethod
    def newClient(cls, server_host, server_port):
        safe_socket = cls()
        safe_socket.sock.connect((server_host, server_port))
        return safe_socket

    def accept(self):
        return self.sock.accept()

    def send(self, msg):
        total_sent = 0
        while total_sent < len(msg):
            sent = self.sock.send(msg[total_sent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            total_sent = total_sent + sent

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
