import paramiko


def ssh_command(ip, user, passwd, command):
    client = paramiko.SSHClient()


    # login with public key
    # client.load_host_keys('/Users/howl/.ssh/known_hosts')
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    # login with username and password
    client.connect(hostname=ip, port=22, username=user, password=passwd)
    ssh_session = client.get_transport().open_session()
    if ssh_session.active:
        ssh_session.exec_command(command)
        print ssh_session.recv(1024)
    return

ssh_command('192.168.199.231', 'root', '*******','whoami')
