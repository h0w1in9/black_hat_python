
import socket

# target_host="www.baidu.com"
# target_port=80

target_host="127.0.0.1"
target_port=8081

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect((target_host,target_port))

# client.send("GET / HTTP/1.1\r\nHOST:www.baidu.com\r\n\r\n")
client.send("AAABBB")

response=client.recv(4096)

while response:
    print response
    # print len(response)
    response=client.recv(4096)








