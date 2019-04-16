import urllib2
import requests
import json

bing_api_key = "3cf74e822848413cb6037eaf13cfec70"
search_url =  "https://api.cognitive.microsoft.com/bing/v7.0/search"

headers = {"Ocp-Apim-Subscription-Key" : bing_api_key}
#params  = {"q": "ip:176.28.50.165", "textDecorations":True, "textFormat":"HTML"}
params  = {"q": "domain:testphp.vulnweb.com", "textDecorations":True, "textFormat":"HTML"}
# s = requests.Session()
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}
response = requests.get(search_url, headers=headers, params=params, proxies=proxies, verify='/Users/howl/Downloads/cert.pem')

response.raise_for_status()
search_results = response.json()

print type(search_results)
print json.dumps(search_results,indent=4)