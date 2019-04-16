import socket
import threading
import sys
import subprocess
import getopt

# define some global variables
target = ""
port = 0
listen = False
command = False
execute = ""
upload = False
upload_destination = ""
end_str = "<###Finished###>\n"


def usage():
    print "BHP Net Tool"
    print
    print "Usage: bpnet.py -t target_host -p port"
    print "-l --listen - listen on [host]:[port] for incoming connections"
    print "-e --execute=file_to_run - execute the given file upon receiving a connection"
    print "-c --command - initialize a command shell"
    print "-u --upload=destination - upon receiving connection upload a file and write to[destination]"
    print
    print
    print "Examples: "
    print "bpnet.py -t 192.168.0.1 -p 5555 -l -c"
    print "bpnet.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe"
    print "bpnet.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/passwd\""
    print "echo 'ABCDEFGHI' | ./bpnet.py -t 192.168.11.12 -p 135"
    sys.exit(0)


def main():
    global target
    global listen
    global command
    global execute
    global upload
    global port
    global upload_destination

    if not len(sys.argv[1:]):
        usage()

    # read the commandline options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu:",
                                   ["help", "listen", "execute", "target", "port", "command", "upload"])
    except getopt.GetoptError as err:
        print str(err)
        usage()

    for opt, optarg in opts:
        if opt in ["-h", "--help"]:
            usage()
        elif opt in ["-l", '--listen']:
            listen = True
        elif opt in ["-e", "--excute"]:
            execute = optarg
        elif opt in ["-t", "--target"]:
            target = optarg
        elif opt in ["-p", "--port"]:
            port = int(optarg)
        elif opt in ["-c", "--commandshell"]:
            command = True
        elif opt in ["-u", "--upload"]:
            upload = True
            upload_destination = optarg
        else:
            assert False, "Unhandled Arguments."

    # are we going to listen or just send data from stdin?
    if not listen and port > 0 and len(target) > 0:
        # read in the buffer from the commandline
        # this will block, so send CTRL-D (EOF) if not sending input
        # to stdin

        buffer = sys.stdin.read()
        # buffer = raw_input()
        # buffer += '\n'
        # send data off
        client_sender(buffer)

    # we are going to listen and potentially
    # upload things, execute commands, and drop a shell back
    # depending on our command line options above
    if listen:
        server_loop()


def client_sender(buffer):
    global target
    global port
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # client.setblocking(False)

    #set non block mode of socket
    client.settimeout(0.2)
    try:
        # connect to our target host
        client.connect((target, port))
        try:
            data = client.recv(4096)
            print data
        except:
            pass

        if len(buffer) > 0:
            client.send(buffer)

        while True:
            response = ""
            while True:
                try:
                    data = client.recv(4096)
                    response += data
                except:
                    print response
                    break

            buffer = sys.stdin.readline()


            # send it off
            client.send(buffer)

    except:
        print "[*] Exception! Exiting."

        # tear down the connection
        client.close()


def server_loop():
    global target
    global port
    if not len(target):
        target = "0.0.0.0"

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))
    server.listen(5)

    while True:
        client_socket, addr = server.accept()
        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        client_thread.start()
    return


def client_handler(client_socket):
    global upload
    global upload_destination
    global command
    global execute
    global end_str

    # check for upload
    if upload and len(upload_destination) > 0:
        # read in all of the bytes and write to our destination
        file_buffer = ""
        client_socket.settimeout(0.2)
        while True:
            try:
                data = client_socket.recv(4096)
                file_buffer += data
            except:
                break

        # now we take these bytes and try to write them out
        try:
            file_descriptor = open(upload_destination, "wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()

            client_socket.send("Successfully saved file to %s\r\n" % upload_destination)
        except:
            client_socket.send("Failed to save file to %s\r\n" % upload_destination)

    if len(execute):
        output = run_command(execute)
        client_socket.send(output)

    if command:
        while True:
            # show a simple prompt
            client_socket.send("<BPSHELL:#>")

            # now we receive until we see a linefeed (enter key)
            cmd_buffer = ""
            while '\n' not in cmd_buffer:
                cmd_buffer += client_socket.recv(4096)

            output = run_command(cmd_buffer)
            # send back the command output
            client_socket.send(output)

            #client_socket.send(end_str)


def run_command(command):
    # trim the newline
    command = command.rstrip()

    try:
        # run the command and get the output back
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except:
        output = "Failed to execute command.\r\n"

    # send the output back to the client
    return output


if __name__ == '__main__':
    main()

#echo -ne "GET / HTTP/1.1\r\nHost: www.google.com\r\n\r\n" | python bpnet.py -t www.google.com -p 80