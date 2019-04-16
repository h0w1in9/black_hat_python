from burp import IBurpExtender
from burp import IContextMenuFactory

from java.util import ArrayList
from javax.swing import JMenuItem

from datetime import datetime
import re
from HTMLParser import HTMLParser


class TagStripper(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.page_text = []

    def handle_data(self, data):
        self.page_text.append(data)

    def handle_comment(self, data):
        self.handle_data(data)

    def strip(self, html):
        self.feed(html)
        return " ".join(self.page_text)


class BurpExtender(IBurpExtender, IContextMenuFactory):
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        self.context = None

        self.hosts = set()

        self.wordlists = set(["password"])

        callbacks.setExtensionName("Burp Wordlist")
        callbacks.registerContextMenuFactory(self)
        return

    def createMenuItems(self, context_menu):
        self.context = context_menu
        menu_list = ArrayList()
        menu_list.add(JMenuItem("Create wordlist",actionPerformed = self.wordlist_menu))
        return menu_list

    def wordlist_menu(self, event):
        # grab the details of what the user clicked
        http_traffic = self.context.getSelectedMessages()

        for traffic in http_traffic:
            http_service = traffic.getHttpService()
            host = http_service.getHost()

            self.hosts.add(host)

            http_response = traffic.getResponse()

            if http_response:
                self.get_words(http_response)

        self.display_wordlist()
        return

    def get_words(self, http_response):
        headers, body = http_response.tostring().split("\r\n\r\n",1)

        # skip non-text responses
        if headers.lower().find("content-type: text") == -1:
            return

        tag_stripper = TagStripper()

        page_text = tag_stripper.strip(body)

        print page_text

        words = re.findall("[a-zA-Z]\w{2,}", page_text)

        for word in words:
            # filter out long strings
            if len(word) <= 12:
                self.wordlists.add(word.lower())

        return

    def display_wordlist(self):
        print "#!comment: Burp wordlist for site: %s" % ", ".join(self.hosts)
        for word in sorted(self.wordlists):
            for password in self.mingle(word):
                print password

        return

    def mingle(self, word):
        year = datetime.now().year
        suffixes = ["", "!", "1", year]
        mingled = []
        for password in (word, word.capitalize()):
            for suffix in suffixes:
                mingled.append("%s%s"%(password,suffix))

        return mingled

