import os


def run(**args):
    print "[*] In dirlistr module."

    files = os.listdir(".")
    return str(files)


