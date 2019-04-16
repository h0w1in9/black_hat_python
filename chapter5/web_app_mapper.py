import urllib2
import Queue
import threading
import os

threads = 10

target = "http://192.168.211.154/wordpress"
directory = "./wordpress"
file_filter = [".jpg", ".png", ".css", ".gif"]

os.chdir(directory)

web_paths = Queue.Queue()

for dirpath, dirnames, filenames in os.walk("."):
    for filename in filenames:
        remote_path = "%s/%s" % (dirpath, filename)
        if remote_path.startswith('.'):
            remote_path = remote_path[1:]
        if os.path.splitext(filename)[1] not in file_filter:
            web_paths.put(remote_path)


def test_remote():
    while not web_paths.empty():
        path = web_paths.get()
        url = "%s%s" % (target, path)

        request = urllib2.Request(url)
        try:
            response = urllib2.urlopen(request)
            # content = response.read()
            print "[%d] => %s" % (response.code, path)
        except urllib2.HTTPError as error:
            pass


for i in range(threads):
    print "Spawning thread: %d" % i
    t = threading.Thread(target=test_remote)
    t.start()
