import time
import subprocess
from pywinauto import Application
from typing import Optional, Annotated


def open_camera() -> Annotated[Optional[str], "Camera app opened successfully." ]:
    """
    Open the Camera app.
    """
    try:
        subprocess.run("start microsoft.windows.camera:", shell=True, check=True)
        print("Camera app opened successfully.")
        time.sleep(3)
        return "Camera app opened successfully."
    except subprocess.CalledProcessError as e:
        print(f"Failed to open the Camera app. Error: {e}")
        return f"Failed to open the Camera app. Error: {e}"


def minimize_camera():
    """
    Minimize the Camera app.
    """
    try:
        app = Application(backend="uia").connect(title_re="Camera")
        window = app.window(title_re="Camera")
        minimize_button = window.child_window(
            title="Minimize Camera", auto_id="Minimize", control_type="Button"
        )
        if minimize_button.exists() and minimize_button.is_enabled():
            minimize_button.click_input()
            print("Camera app minimized successfully.")
        else:
            print("Minimize button is not accessible.")
    except Exception as e:
        print(f"Failed to minimize Camera app. Error: {e}")


def restore_camera():
    """
    Restore the Camera app.
    """
    try:
        app = Application(backend="uia").connect(title_re="Camera")
        window = app.window(title_re="Camera")
        # Ensure window is visible and restored from minimized state
        if window.exists():
            window.restore()
            window.set_focus()
            print("Camera app restored successfully.")
        else:
            print("Camera window not found.")
    except Exception as e:
        print(f"Failed to restore Camera app. Error: {e}")


def click_windows_studio_effects():
    """
    Click the 'Windows Studio Effects' button.
    """
    try:
        app = Application(backend="uia").connect(title_re="Camera")
        window = app.window(title_re="Camera")
        button = window.child_window(
            title="Windows Studio Effects",
            control_type="Button",
            class_name="ToggleButton",
        )
        if button.exists() and button.is_enabled():
            button.click_input()
            time.sleep(1)
            print("'Windows Studio Effects' button clicked.")
        else:
            print("'Windows Studio Effects' button is not accessible.")
    except Exception as e:
        print(f"Failed to interact with 'Windows Studio Effects' button. Error: {e}")


def check_background_effects_state() -> int:    
    """
    Check the state of the background effects toggle button.
    Returns:
        int: The state of the toggle button (0 for off, 1 for on).
    """
    try:
        app = Application(backend="uia").connect(title_re="Camera")
        window = app.window(title_re="Camera")
        button = window.child_window(
            title="Background effects", auto_id="Switch", control_type="Button"
        )
        if button.exists():
            # 0 means off, 1 means on
            toggle_state = button.get_toggle_state()
            state = "ON" if toggle_state == 1 else "OFF"
            print(f"Background effects is {state}")
            return toggle_state
        else:
            print("Background effects button not found")
            return None
    except Exception as e:
        print(f"Failed to check Background effects state. Error: {e}")
        return None


def check_automatic_framing_state() -> int:
    """
    Check the state of the automatic framing toggle button.
    Returns:
        int: The state of the toggle button (0 for off, 1 for on).
    """
    try:
        app = Application(backend="uia").connect(title_re="Camera")
        window = app.window(title_re="Camera")
        button = window.child_window(
            title="Automatic framing - The camera will keep you in frame and in focus for videos",
            auto_id="Switch",
            control_type="Button",
        )
        if button.exists():
            # 0 means off, 1 means on
            toggle_state = button.get_toggle_state()
            state = "ON" if toggle_state == 1 else "OFF"
            print(f"Automatic framing is {state}")
            return toggle_state
        else:
            print("Automatic framing button not found")
            return None
    except Exception as e:
        print(f"Failed to check Automatic framing state. Error: {e}")
        return None


def set_blur_type(blur_type: str):
    """
    Set the blur type to either 'standard' or 'portrait'.
    First checks if background effects is enabled, enables it if not.

    Args:
        blur_type (str): Either 'standard' or 'portrait'
    """
    try:
        app = Application(backend="uia").connect(title_re="Camera")
        window = app.window(title_re="Camera")

        # First check if background effects is enabled
        effects_state = check_background_effects_state()
        if effects_state != 1:
            # Background effects is off, need to enable it first
            effects_button = window.child_window(
                title="Background effects", auto_id="Switch", control_type="Button"
            )
            if effects_button.exists():
                effects_button.click_input()
                time.sleep(1)
                print("Enabled background effects")

        # Now select the blur type
        if blur_type.lower() == "standard":
            radio_button = window.child_window(
                title="Standard blur - Apply a heavy blur to obscure background objects",
                control_type="RadioButton",
            )
        elif blur_type.lower() == "portrait":
            radio_button = window.child_window(
                title="Portrait blur - Blur the background to help keep focus on you",
                control_type="RadioButton",
            )
        else:
            print(f"Invalid blur type: {blur_type}. Use 'standard' or 'portrait'")
            return

        if radio_button.exists():
            radio_button.click_input()
            print(f"Set blur type to: {blur_type}")
        else:
            print(f"Could not find {blur_type} blur radio button")

    except Exception as e:
        print(f"Failed to set blur type. Error: {e}")


def set_background_effects(desired_state: bool = None):
    """
    Toggle background effects on/off or set to a specific state.

    Args:
        desired_state (bool, optional): If provided, will set to this state (True=ON, False=OFF).
                                      If None, will toggle current state.
    """
    try:
        app = Application(backend="uia").connect(title_re="Camera")
        window = app.window(title_re="Camera")
        button = window.child_window(
            title="Background effects", auto_id="Switch", control_type="Button"
        )

        if button.exists():
            current_state = button.get_toggle_state() == 1

            # Determine if we need to click
            should_click = False
            if desired_state is None:
                # Toggle mode - always click
                should_click = True
            else:
                # Set to specific state - click only if different
                should_click = current_state != desired_state

            if should_click:
                button.click_input()
                time.sleep(1)
                new_state = "ON" if button.get_toggle_state() == 1 else "OFF"
                print(f"Background effects switched to: {new_state}")
            else:
                print(
                    f"Background effects already in desired state: {'ON' if current_state else 'OFF'}"
                )
        else:
            print("Background effects button not found")

    except Exception as e:
        print(f"Failed to set background effects. Error: {e}")


def set_automatic_framing(desired_state: bool = None):
    """
    Toggle automatic framing on/off or set to a specific state.

    Args:
        desired_state (bool, optional): If provided, will set to this state (True=ON, False=OFF).
                                      If None, will toggle current state.
    """
    try:
        app = Application(backend="uia").connect(title_re="Camera")
        window = app.window(title_re="Camera")
        button = window.child_window(
            title="Automatic framing - The camera will keep you in frame and in focus for videos",
            auto_id="Switch",
            control_type="Button",
        )

        if button.exists():
            current_state = check_automatic_framing_state()
            if current_state is None:
                print("Could not determine current automatic framing state")
                return

            # Determine if we need to click
            should_click = False
            if desired_state is None:
                # Toggle mode - always click
                should_click = True
            else:
                # Set to specific state - click only if different
                should_click = (current_state == 1) != desired_state

            if should_click:
                button.click_input()
                time.sleep(1)
                new_state = "ON" if check_automatic_framing_state() == 1 else "OFF"
                print(f"Automatic framing switched to: {new_state}")
            else:
                print(
                    f"Automatic framing already in desired state: {'ON' if current_state == 1 else 'OFF'}"
                )
        else:
            print("Automatic framing button not found")

    except Exception as e:
        print(f"Failed to set automatic framing. Error: {e}")
