import sys
import time
import subprocess
from pywinauto import Application

from src.tools.tools import *


if __name__ == "__main__":
    open_camera()
    app = Application(backend="uia").connect(title_re="Camera")
    window = app.window(title_re="Camera")
    # print control indentifiers
    # print(window.dump_tree())
    # minimize_camera()
    # restore_camera()
    # state = check_background_effects_state()
    # print(f"Background effects state: {state}")
    # print(window.dump_tree())
    # set_blur_type('portrait')  # 'standard' or 'portrait'

    # # Test automatic framing
    # state = check_automatic_framing_state()
    # print(f"Automatic framing state: {state}")

    # set_automatic_framing(True)  # Turn ON
    # time.sleep(1)
    # set_automatic_framing(False)  # Turn OFF
    # time.sleep(1)
    # set_automatic_framing()  # Toggle current state

    #switch_camera()
    # camera_mode('video')
    # camera_mode('photo')
    # take_photo()
    # take_video(5)
    # open_system_menu()
    # open_video_settings()
    #options = get_video_quality_options()
    # switch_camera('FFC') # switch to 'FFC' or 'RFC'
    # current_type, message = get_current_camera()
    # print(f"Current camera: {current_type} ({message})")
    switch_camera('RFC') # switch to 'FFC' or 'RFC'
    current_type, message = get_current_camera()
    print(f"Current camera: {current_type} ({message})")
    #print(window.print_control_identifiers())
    # switch_camera('FFC') # switch to 'FFC' or 'RFC'
    # switch_camera('RFC') # switch to 'FFC' or 'RFC'
    # #set_video_quality('1440p 16:9 30fps')
    
