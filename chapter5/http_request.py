import urllib2

url = "http://www.bing.com"

headers = {}
headers["User-Agent"] = "GoogleBot"

request = urllib2.Request(url, headers=headers)
response = urllib2.urlopen(request)

print response.read()
response.close()

