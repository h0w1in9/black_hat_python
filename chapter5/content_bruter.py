import threading
import urllib2
import Queue

threads = 50
target_url = "http://testphp.vulnweb.com"
# from SVNDigger
wordlist_file = "all.txt"
resume = None
user_agent = "Mozilla/5.0 (X11; Linux x86_64; rv:66.0) Gecko/2"


def build_wordlist(wordlist_file):
    # read in the word list
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
                if word == resume:
                    found_resume = True
                    print "Resuming wordlist from: %s" % resume
        else:
            words.put(word)

    return words


def dir_bruter(word_quene, extensions=None):
    while not word_quene.empty():
        attempt = word_quene.get()
        attempt_list = []

        # check to see if there is a file extension; if not,
        # it's a directory path we're bruting
        if '.' not in attempt:
            attempt_list.append("/%s/" % attempt)
        else:
            attempt_list.append("/%s" % attempt)

        # if we want to bruteforce extensions
        if extensions:
            for extension in extensions:
                attempt_list.append("/%s%s" % (attempt, extension))

        # iterate over our list of attempts
        for brute in attempt_list:
            url = "%s%s" % (target_url, urllib2.quote(brute))
            try:
                headers = {}
                headers['User-Agent'] = user_agent
                request = urllib2.Request(url, headers=headers)

                response = urllib2.urlopen(request)
                if len(response.read()):
                    print "[%d] ==> %s" % (response.code, url)

            except urllib2.URLError, error:

                if hasattr(error, "code") and error.code != 404:
                    print "!!! %d ==> %s" % (error.code, url)

    return


word_queue = build_wordlist(wordlist_file)
extensions = [".php", ".bak", ".orig", ".inc"]

for i in range(threads):
    t = threading.Thread(target=dir_bruter, args=(word_queue, extensions))
    t.start()

