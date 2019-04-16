import socket
import threading

server_host = "0.0.0.0"
server_port = 8081

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((server_host, server_port))

server.listen(5)
print "[*] Listening on %s:%d" % (server_host, server_port)


def handler_client(client_socket):
    response = client_socket.recv(1014)
    print "[*] Received:%s" % response
    client_socket.send("ACK!")
    client_socket.close()


while True:
    req, addr = server.accept()
    print "[*] Received from: %s:%s" % (addr[0], addr[1])
    client_handler = threading.Thread(target=handler_client, args=(req,))
    client_handler.start()
