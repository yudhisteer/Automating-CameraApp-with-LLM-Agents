import sys
import time
import subprocess
from pywinauto import Application

from utils.tools import *


if __name__ == "__main__":
    open_camera()
    app = Application(backend="uia").connect(title_re="Camera")
    window = app.window(title_re="Camera")
    # print control indentifiers
    # print(window.dump_tree())
    # minimize_camera()
    # restore_camera()
    click_windows_studio_effects()
    state = check_background_effects_state()
    print(f"Background effects state: {state}")
    # print(window.dump_tree())
    # set_blur_type('portrait')  # or 'portrait'

    # Test automatic framing
    state = check_automatic_framing_state()
    print(f"Automatic framing state: {state}")

    set_automatic_framing(True)  # Turn ON
    time.sleep(1)
    set_automatic_framing(False)  # Turn OFF
    time.sleep(1)
    set_automatic_framing()  # Toggle current state
