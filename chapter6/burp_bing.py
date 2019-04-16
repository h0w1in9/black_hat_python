from burp import IBurpExtender
from burp import IContextMenuFactory

from javax.swing import JMenuItem
from java.util import List, ArrayList
from java.net import URL

from thread import start_new_thread

import re
import socket
import urllib
import json


bing_api_key = "*********************************"


class BurpExtender(IBurpExtender, IContextMenuFactory):
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        self.context = None

        # we set up our extension
        self._callbacks.setExtensionName("Burp Bing")
        self._callbacks.registerContextMenuFactory(self)
        return

    def createMenuItems(self, context_menu):
        self.context = context_menu
        menu_list = ArrayList()
        menu_list.add(JMenuItem("Send to Bing", actionPerformed=self.bing_menu))

        return menu_list

    def bing_menu(self, event):
        # grab the details of what the user clicked
        http_traffic = self.context.getSelectedMessages()
        print "%d requests highlighted" % len(http_traffic)

        for traffic in http_traffic:
            http_service = traffic.getHttpService()
            host = http_service.getHost()

            print "User selected host: %s" % host

            self.bing_search(host)

        return

    def bing_search(self, host):
        # check if we have an IP or hostname
        is_ip = re.match("[0-9]+(?:\.[0-9]+){3}", host)

        if is_ip:
            ip_address = host
            is_domain = False
        else:
            ip_address = socket.gethostbyname(host)
            is_domain = True

        bing_query_string = "ip:%s" % ip_address
        self.bing_query(bing_query_string)

        if is_domain:
            bing_query_string = "domain:%s" % host
            self.bing_query(bing_query_string)

        return

    # def bing_query(self, bing_query_string):
    #     print "Performing bing search: '%s'" % bing_query_string
    #
    #     # encode our query
    #     quoted_query = urllib.quote(bing_query_string)
    #
    #     http_request = "GET /bing/v7.0/search?q=%s&textFormat=HTML&textDecorations=True HTTP/1.1\r\n" % quoted_query
    #     http_request += "Host: api.cognitive.microsoft.com\r\n"
    #     http_request += "Connection: close\r\n"
    #     http_request += "User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:66.0) Gecko/2\r\n"
    #     http_request += "Ocp-Apim-Subscription-Key: %s\r\n\r\n" % bing_api_key
    #
    #     json_body = self._callbacks.makeHttpRequest("api.cognitive.microsoft.com", 443, True, http_request).tostring()
    #
    #     json_body = json_body.split('\r\n\r\n', 1)[1]
    #
    #     try:
    #         r = json.loads(json_body)
    #         if len(r["webPages"]["value"]):
    #             for site in r["webPages"]["value"]:
    #                 print "*" * 80
    #                 print "Title: %s" % site["name"]
    #                 print "Url: %s" % site["url"]
    #                 print "Description: %s" % site["snippet"]
    #                 print "*" * 80
    #
    #                 j_url = URL(site["url"])
    #
    #                 if not self._callbacks.isInScope(j_url):
    #                     print "Adding to Burp Scope."
    #                     self._callbacks.includeInScope(j_url)
    #     except:
    #         print "No results from bing."
    #         pass
    #
    #     return

    def bing_query(self, bing_query_string):
        print "Performing bing search: '%s'" % bing_query_string

        # encode our query
        quoted_query = urllib.quote(bing_query_string)

        http_request = "GET /bing/v7.0/search?q=%s&textFormat=HTML&textDecorations=True HTTP/1.1\r\n" % quoted_query
        http_request += "Host: api.cognitive.microsoft.com\r\n"
        http_request += "Connection: close\r\n"
        http_request += "User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:66.0) Gecko/2\r\n"
        http_request += "Ocp-Apim-Subscription-Key: %s\r\n\r\n" % bing_api_key

        # print http_request

        start_new_thread(self.send_request_to_bing, ("api.cognitive.microsoft.com", 443, True, http_request,))

    def send_request_to_bing(self, host, port, is_https, message):

        json_body = self._callbacks.makeHttpRequest(host, port, is_https, message).tostring()

        json_body = json_body.split('\r\n\r\n', 1)[1]

        try:
            r = json.loads(json_body)
            if len(r["webPages"]["value"]):
                for site in r["webPages"]["value"]:
                    print "*" * 80
                    print "Title: %s" % site["name"]
                    print "Url: %s" % site["url"]
                    print "Description: %s" % site["snippet"]
                    print "*" * 80

                    j_url = URL(site["url"])

                    if not self._callbacks.isInScope(j_url):
                        print "Adding to Burp Scope."
                        self._callbacks.includeInScope(j_url)
        except:
            print "No results from bing."
            pass

        return

