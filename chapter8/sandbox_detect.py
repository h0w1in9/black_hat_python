import ctypes
import time
import random
import sys
import win32api

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

keystrokes = 0
mouse_clicks = 0


class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_uint),
                ("dwTime", ctypes.c_ulong)]


def get_last_input():
    struct_lastinputinfo = LASTINPUTINFO()
    struct_lastinputinfo.cbSize = ctypes.sizeof(LASTINPUTINFO)

    # get last input registered
    user32.GetLastInputInfo(ctypes.byref(struct_lastinputinfo))

    # now determine how long the machine has been running
    run_time = kernel32.GetTickCount()

    elapsed = run_time - struct_lastinputinfo.dwTime

    print "[*] It's been %d milliseconds since last input event." % elapsed

    return elapsed


def test():
    while True:
        get_last_input()
        time.sleep(1)


# test()
def get_key_press():
    global keystrokes
    global mouse_clicks

    for i in range(0, 0xff):
        # print "i:",i
        # print win32api.GetAsyncKeyState(i)
        if win32api.GetAsyncKeyState(i):
            # print "i1:",i
            if i == 0x1:
                mouse_clicks += 1
                return time.time()
            elif 32 <= i < 127:
                keystrokes += 1
        # time.sleep(0.01)
    return None


def detect_sandbox():
    global mouse_clicks
    global keystrokes

    max_key_strokes = random.randint(10, 25)
    max_mouse_clicks = random.randint(5, 25)

    double_clicks = 0
    max_double_clicks = 10
    double_click_threshold = 0.25  # in seconds
    first_double_click = None

    average_mousetime = 0
    max_input_threshold = 30000  # in milliseconds

    previous_timestamp = None
    detection_complete = False

    last_input = get_last_input()
    print "last_input:", last_input

    # if we hit our threshold let's bail out
    if last_input >= max_input_threshold:
        sys.exit(0)

    while not detection_complete:

        keypress_time = get_key_press()
        # print "keypress_time:", keypress_time

        if keypress_time is not None and previous_timestamp is not None:
            # calculate the time between double clicks
            elapsed = keypress_time - previous_timestamp
            if elapsed <= double_click_threshold:
                double_clicks += 1
                if first_double_click is None:
                    # grab the timestamp of the first double click
                    first_double_click = keypress_time

            else:
                if double_clicks == max_double_clicks:
                    if keypress_time - first_double_click <= (max_double_clicks * double_click_threshold):
                        sys.exit(0)

            previous_timestamp = keypress_time

        elif keypress_time is not None:

            previous_timestamp = keypress_time

        print mouse_clicks, keystrokes, double_clicks

        # we are happy there's enough user input
        if mouse_clicks >= max_mouse_clicks and keystrokes >= max_key_strokes and double_clicks >= max_double_clicks:
            return

        # print "mouse_clicks: %d, keystrokes: %d, double_clicks: %d"%(mouse_clicks, keystrokes, double_clicks)
        time.sleep(0.1)


detect_sandbox()
print "We are OK!"
