import os
import sys
import ctypes

INADDR_ANY = 0x00000000
AF_INET = 2
SOCK_STREAM = 1
IPPROTO_TCP = 6
PORT = 8080
BUFFER_SIZE = 1024

ws2_32 = ctypes.windll.ws2_32

class sockaddr_in(ctypes.Structure):
    _fields_ = [("sin_family", ctypes.c_short),
                ("sin_port", ctypes.c_ushort),
                ("sin_addr", ctypes.c_ulong),
                ("sin_zero", ctypes.c_char * 8)]

def htons(value):
    return (value << 8 & 0xFF00) | (value >> 8 & 0x00FF)

def create_socket():
    return ws2_32.socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)

def bind_socket(sock, address):
    return ws2_32.bind(sock, ctypes.byref(address), ctypes.sizeof(address))

def listen_socket(sock):
    return ws2_32.listen(sock, 5)

def accept_socket(sock):
    addr = sockaddr_in()
    addr_len = ctypes.c_int(ctypes.sizeof(addr))
    client_sock = ws2_32.accept(sock, ctypes.byref(addr), ctypes.byref(addr_len))
    return client_sock

def recv_data(sock, buffer_size):
    buffer = ctypes.create_string_buffer(buffer_size)
    received = ws2_32.recv(sock, buffer, buffer_size, 0)
    return buffer.value if received != -1 else None

def send_data(sock, data):
    return ws2_32.send(sock, data, len(data), 0)

def close_socket(sock):
    return ws2_32.closesocket(sock)

def run_server(response):
    ws2_32.WSAStartup(0x0202, ctypes.byref(ctypes.create_string_buffer(32)))

    server_sock = create_socket()
    if server_sock == -1:
        print("Socket creation failed.")
        return

    server_addr = sockaddr_in()
    server_addr.sin_family = AF_INET
    server_addr.sin_port = htons(PORT)
    server_addr.sin_addr = INADDR_ANY

    if bind_socket(server_sock, server_addr) != 0:
        print("Bind failed.")
        close_socket(server_sock)
        return

    if listen_socket(server_sock) != 0:
        print("Listen failed.")
        close_socket(server_sock)
        return

    print(f"Server is running on port {PORT}")

    while True:
        client_sock = accept_socket(server_sock)
        if client_sock == -1:
            print("Accept failed.")
            close_socket(server_sock)
            return

        data = recv_data(client_sock, BUFFER_SIZE)
        if data:
            print("Request received:")
            print(data.decode())
            response = f'b"{response}"'
            send_data(client_sock, response)

        close_socket(client_sock)

    close_socket(server_sock)
    ws2_32.WSACleanup()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: _client_socket.py _response.txt')
    run_server(sys.argv[1])
