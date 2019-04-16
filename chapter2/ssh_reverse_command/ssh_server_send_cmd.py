import paramiko
import socket
import sys
import threading

# using the key from the Paramiko demo files
host_key = paramiko.RSAKey(filename="/etc/ssh/ssh_host_rsa_key")


class Server(paramiko.ServerInterface):
    def _init_(self):
        self.event = threading.Event()
        return

    def check_auth_password(self, username, password):
        if username == "root" and password == "*******":
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED


server = sys.argv[1]
ssh_port = int(sys.argv[2])

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((server, ssh_port))
    sock.listen(100)
    print "[+] Listening for connection..."
    client, addr = sock.accept()
except Exception, e:
    print "[-] Listen failed: %s" % str(e)
    sys.exit(1)
    pass

print "[+] Got a connection!"

try:
    ssh_session = paramiko.Transport(client)
    ssh_session.add_server_key(host_key)
    server = Server()

    try:
        ssh_session.start_server(server=server)

    except paramiko.SSHException, e:
        print "[-] SSH negotiation failed."

    chan = ssh_session.accept(20)
    print "[+] Authenticated."

    print chan.recv(1024)

    chan.send('Welcome to bh_ssh.')
    while True:

        try:
            command = raw_input("Enter command: ").strip('\n')
            if command != "exit":
                if len(command):
                    chan.send(command)
                    output = chan.recv(1024)
                    print output+'\n'
            else:
                chan.send('exit')
                print "exiting."
                ssh_session.close()
                raise Exception("exit")
        except KeyboardInterrupt:
            ssh_session.close()
except Exception, e:
    print "[-] Caught exception: %s" % str(e)
    try:
        ssh_session.close()
    except:
        pass
    sys.exit(1)
