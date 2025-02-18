import subprocess
import time
from typing import Annotated, Any, Literal, Optional, Tuple

from pywinauto import Application
from pywinauto.findwindows import ElementNotFoundError


def open_camera() -> Annotated[Optional[str], "Camera app opened successfully."]:
    """
    Open the Camera app if it's not already running.
    """
    try:
        # First try to connect to existing Camera window
        try:
            app = Application(backend="uia").connect(title_re="Camera")
            print("Camera app is already running.")
            return "Camera app is already running."
        except ElementNotFoundError:
            # If connect fails, then open new instance
            subprocess.run("start microsoft.windows.camera:", shell=True, check=True)
            print("Camera app opened successfully.")
            time.sleep(3)
            return "Camera app opened successfully."
    except subprocess.CalledProcessError as e:
        print(f"Failed to open the Camera app. Error: {e}")
        return f"Failed to open the Camera app. Error: {e}"
    except Exception as e:
        print(f"An error occurred: {e}")
        return f"An error occurred: {e}"


def close_camera() -> Annotated[Optional[str], "Camera app closed successfully."]:
    """
    Close the Camera app.
    """
    try:
        app = Application(backend="uia").connect(title_re="Camera")
        window = app.window(title_re="Camera")
        window.close()
        print("Camera app closed successfully.")
        return "Camera app closed successfully."
    except Exception as e:
        print(f"Failed to close Camera app. Error: {e}")
        return f"Failed to close Camera app. Error: {e}"


def minimize_camera() -> Annotated[Optional[str], "Camera app minimized successfully."]:
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
            time.sleep(1)
            print("Camera app minimized successfully.")
            return "Camera app minimized successfully."
        else:
            print("Minimize button is not accessible.")
            return "Minimize button is not accessible."
    except Exception as e:
        print(f"Failed to minimize Camera app. Error: {e}")
        return f"Failed to minimize Camera app. Error: {e}"


def restore_camera() -> Annotated[Optional[str], "Camera app restored successfully."]:
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
            time.sleep(1)
            print("Camera app restored successfully.")
            return "Camera app restored successfully."
        else:
            print("Camera window not found.")
            return "Camera window not found."
    except Exception as e:
        print(f"Failed to restore Camera app. Error: {e}")
        return f"Failed to restore Camera app. Error: {e}"


def click_windows_studio_effects() -> (
    Annotated[Optional[str], "'Windows Studio Effects' button clicked."]
):
    """
    Click the 'Windows Studio Effects' button if it's not already expanded.
    """
    try:
        # First ensure we're in video mode
        mode_result = camera_mode("video")
        if (
            mode_result != "Already in video mode"
            and mode_result != "Camera mode switched to video"
        ):
            print("Failed to ensure video mode")
            return "Failed to ensure video mode"

        app = Application(backend="uia").connect(title_re="Camera")
        window = app.window(title_re="Camera")
        button = window.child_window(
            title="Windows Studio Effects",
            control_type="Button",
            class_name="ToggleButton",
        )
        if button.exists() and button.is_enabled():
            # Check if the button is already in pressed state (panel is open)
            if not button.get_toggle_state():
                button.click_input()
                time.sleep(1)
                print("'Windows Studio Effects' button clicked.")
                return "'Windows Studio Effects' button clicked."
            else:
                print("'Windows Studio Effects' panel is already open.")
                return "'Windows Studio Effects' panel is already open."
        else:
            print("'Windows Studio Effects' button is not accessible.")
            return "'Windows Studio Effects' button is not accessible."
    except Exception as e:
        print(f"Failed to interact with 'Windows Studio Effects' button. Error: {e}")
        return f"Failed to interact with 'Windows Studio Effects' button. Error: {e}"


def check_background_effects_state() -> (
    Annotated[Optional[int], "The state of the toggle button (0 for off, 1 for on)."]
):
    """
    Check the state of the background effects toggle button.
    Returns:
        int: The state of the toggle button (0 for off, 1 for on).
    """
    try:
        app = Application(backend="uia").connect(title_re="Camera")
        window = app.window(title_re="Camera")
        click_windows_studio_effects()
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


def set_blur_type(
    blur_type: Annotated[str, "Either 'standard' or 'portrait'"],
) -> Annotated[Optional[str], "Blur type set successfully."]:
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
                title="Standard blur",
                control_type="RadioButton",
            )
        elif blur_type.lower() == "portrait":
            radio_button = window.child_window(
                title="Portrait blur",
                control_type="RadioButton",
            )
        else:
            print(f"Invalid blur type: {blur_type}. Use 'standard' or 'portrait'")
            return f"Invalid blur type: {blur_type}. Use 'standard' or 'portrait'"

        if radio_button.exists():
            radio_button.click_input()
            print(f"Set blur type to: {blur_type}")
        else:
            print(f"Could not find {blur_type} blur radio button")
            return f"Could not find {blur_type} blur radio button"
    except Exception as e:
        print(f"Failed to set blur type. Error: {e}")
        return f"Failed to set blur type. Error: {e}"


def set_background_effects(
    desired_state: Annotated[bool, "True=ON, False=OFF"],
) -> Annotated[str, "Background effects toggled successfully."]:
    """
    Set background effects to a specific state, ensuring FFC camera is active first.
    Note: This function leaves the Windows Studio Effects panel open after completion.

    Args:
        desired_state (bool): True to set ON, False to set OFF
    """
    try:
        # First ensure we're on FFC
        current_type, detect_msg = get_current_camera()
        if current_type is None:
            return f"Failed to detect camera type: {detect_msg}"

        if current_type != "FFC":
            switch_result = switch_camera(target_type="FFC")
            if "successfully" not in switch_result:
                return f"Failed to switch to FFC camera: {switch_result}"
            time.sleep(2)

        app = Application(backend="uia").connect(title_re="Camera")
        window = app.window(title_re="Camera")

        # Check Windows Studio Effects panel state - will open if closed, stay open if already open
        effects_result = click_windows_studio_effects()
        if "not accessible" in effects_result or "Failed" in effects_result:
            return f"Failed to access Windows Studio Effects: {effects_result}"

        # Panel is now open, proceed with background effects
        button = window.child_window(
            title="Background effects", auto_id="Switch", control_type="Button"
        )

        if button.exists():
            # Check current state using the dedicated function
            current_state = check_background_effects_state() == 1

            # Only click if current state doesn't match desired state
            should_click = current_state != desired_state

            if should_click:
                button.click_input()
                time.sleep(1)
                new_state = "ON" if button.get_toggle_state() == 1 else "OFF"
                print(f"Background effects switched to: {new_state}")
                return f"Background effects toggled successfully."
            else:
                print(
                    f"Background effects already in desired state: {'ON' if current_state else 'OFF'}"
                )
                return f"Background effects already in desired state."
        else:
            print("Background effects button not found")
            return "Background effects button not found"

    except Exception as e:
        print(f"Failed to set background effects. Error: {e}")
        return f"Failed to set background effects. Error: {e}"


def check_automatic_framing_state() -> int:
    """
    Check the state of the automatic framing toggle button.
    Returns:
        int: The state of the toggle button (0 for off, 1 for on).
    """
    try:
        app = Application(backend="uia").connect(title_re="Camera")
        window = app.window(title_re="Camera")
        click_windows_studio_effects()
        button = window.child_window(
            title="Automatic framing",
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


def set_automatic_framing(
    desired_state: Annotated[bool, "True=ON, False=OFF"],
) -> Annotated[str, "Automatic framing toggled successfully."]:
    """
    Set automatic framing to a specific state.

    Args:
        desired_state (bool): True to set ON, False to set OFF
    """
    try:

        # First ensure we're on FFC
        current_type, detect_msg = get_current_camera()
        if current_type is None:
            return f"Failed to detect camera type: {detect_msg}"

        if current_type != "FFC":
            switch_result = switch_camera(target_type="FFC")
            if "successfully" not in switch_result:
                return f"Failed to switch to FFC camera: {switch_result}"
            time.sleep(2)

        app = Application(backend="uia").connect(title_re="Camera")
        window = app.window(title_re="Camera")

        # Check Windows Studio Effects panel state - will open if closed, stay open if already open
        effects_result = click_windows_studio_effects()
        if "not accessible" in effects_result or "Failed" in effects_result:
            return f"Failed to access Windows Studio Effects: {effects_result}"

        button = window.child_window(
            title="Automatic framing",
            auto_id="Switch",
            control_type="Button",
        )

        if button.exists():
            # Check current state using the dedicated function
            current_state = check_automatic_framing_state() == 1

            # Only click if current state doesn't match desired state
            should_click = current_state != desired_state

            if should_click:
                button.click_input()
                time.sleep(1)
                new_state = "ON" if button.get_toggle_state() == 1 else "OFF"
                print(f"Automatic framing switched to: {new_state}")
                return f"Automatic framing toggled successfully."
            else:
                print(
                    f"Automatic framing already in desired state: {'ON' if current_state else 'OFF'}"
                )
                return f"Automatic framing already in desired state."
        else:
            print("Automatic framing button not found")
            return "Automatic framing button not found"

    except Exception as e:
        print(f"Failed to set automatic framing. Error: {e}")
        return f"Failed to set automatic framing. Error: {e}"


def get_current_camera() -> Tuple[Optional[Literal["FFC", "RFC"]], str]:
    """
    Detect current camera type (FFC or RFC) based on UI elements present.
    In video mode, uses Windows Studio Effects panel visibility to detect FFC.

    Returns:
        Tuple[Optional[CameraType], str]: (camera_type, message)
        camera_type will be "FFC" or "RFC" if detected, None if detection fails
    """
    try:
        app = Application(backend="uia").connect(title_re="Camera")
        window = app.window(title_re="Camera")

        # First determine if we're in photo or video mode
        take_photo_button = window.child_window(
            title="Take photo",
            auto_id="CaptureButton_0",
            control_type="Button",
            found_index=None,
        )

        take_video_button = window.child_window(
            title="Take video",
            auto_id="CaptureButton_1",
            control_type="Button",
            found_index=None,
        )

        is_video_mode = take_video_button.exists()

        if is_video_mode:
            # In video mode, check for Windows Studio Effects button
            windows_effects_button = window.child_window(
                title="Windows Studio Effects",
                control_type="Button",
                class_name="ToggleButton",
            )

            if windows_effects_button.exists() and windows_effects_button.is_enabled():
                return (
                    "FFC",
                    "Front-facing camera detected (Windows Studio Effects available)",
                )

            # If Windows Studio Effects not found, check for panorama mode
            panorama_mode_button = window.child_window(
                title="Switch to panorama mode",
                auto_id="CaptureButton_2",
                control_type="Button",
                found_index=None,
            )

            if panorama_mode_button.exists():
                return (
                    "RFC",
                    "Rear-facing camera detected (panorama mode available in video)",
                )

            # If neither Windows Effects nor panorama available, we can't determine definitively
            return (
                None,
                "Camera in video mode but type cannot be determined definitively",
            )

        else:
            # In photo mode, check for barcode/document modes
            barcode_button = window.child_window(
                title="Switch to barcode mode",
                auto_id="CaptureButton_5",
                control_type="Button",
                found_index=None,
            )

            document_button = window.child_window(
                title="Switch to document mode",
                auto_id="CaptureButton_3",
                control_type="Button",
                found_index=None,
            )

            if barcode_button.exists():
                return "FFC", "Front-facing camera detected (barcode mode available)"
            elif document_button.exists():
                return "RFC", "Rear-facing camera detected (document mode available)"

        # If we reached here, we couldn't determine the camera type
        if take_photo_button.exists() or take_video_button.exists():
            return None, "Camera active but type cannot be determined definitively"

        return None, "Could not determine camera type - no identifying buttons found"

    except Exception as e:
        return None, f"Failed to detect camera type. Error: {e}"


def switch_camera(
    target_type: Optional[Literal["FFC", "RFC"]] = None,
) -> Annotated[str, "Operation result message"]:
    """
    Switch between available cameras with optional target type specification.

    Args:
        target_type: Target camera type ("FFC" or "RFC"). If None, simply switches to other camera.

    Returns:
        str: Operation result message
    """
    try:
        # First check current camera type
        current_type, detect_msg = get_current_camera()
        print(f"Current camera type: {current_type}")

        if current_type is None:
            print(f"Warning: {detect_msg}")
        elif target_type and current_type == target_type:
            return f"Already using {target_type} camera, no switch needed"

        # Proceed with switch
        app = Application(backend="uia").connect(title_re="Camera")
        window = app.window(title_re="Camera")
        button = window.child_window(
            title="Change camera", auto_id="SwitchCameraButtonId", control_type="Button"
        )

        if button.exists() and button.is_enabled():
            button.click_input()
            time.sleep(2)  # Increased wait time to 2 seconds

            # # Verify switch result if target was specified
            # if target_type:
            #     # Try up to 3 times to detect the correct camera type
            #     for _ in range(3):
            #         new_type, _ = get_current_camera()
            #         if new_type == target_type:
            #             return f"Successfully switched to {target_type} camera"
            #         elif new_type is None:
            #             time.sleep(1)  # Wait a bit more if detection failed
            #             continue
            #         else:
            #             # If wrong type detected, try one more camera switch
            #             if _ == 0:  # Only try one additional switch
            #                 button.click_input()
            #                 time.sleep(1)
            #             else:
            #                 time.sleep(0.5)

            #     # If we get here, the switch wasn't successful
            #     final_type, _ = get_current_camera()
            #     if final_type == target_type:
            #         return f"Successfully switched to {target_type} camera"
            #     elif final_type is None:
            #         return "Switch completed but camera type verification failed"
            #     else:
            #         return f"Switch completed but wrong camera type detected. Current: {final_type}, Target: {target_type}"

            return "Camera switched successfully"
        else:
            return "Camera switch button is not accessible"

    except Exception as e:
        print(f"Failed to switch camera. Error: {e}")
        return f"Failed to switch camera. Error: {e}"


def camera_mode(
    mode: Annotated[str, "Either 'photo' or 'video'"],
) -> Annotated[Optional[str], "Camera mode set successfully."]:
    """
    Set the camera mode to either 'photo' or 'video'.

    Args:
        mode (str): Either 'photo' or 'video'
    """
    try:
        app = Application(backend="uia").connect(title_re="Camera")
        window = app.window(title_re="Camera")

        # Try to find the "Switch to photo mode" button
        switch_to_photo = window.child_window(
            title="Switch to photo mode", auto_id="CaptureButton_0"
        )
        # Try to find the "Take video" button
        take_video_button = window.child_window(
            title="Take video", auto_id="CaptureButton_1"
        )

        if mode.lower() == "photo":
            if switch_to_photo.exists():
                # If we can see "Switch to photo mode", we're in video mode and need to switch
                switch_to_photo.click_input()
                time.sleep(1)
                print("Camera mode switched to photo")
                return "Camera mode switched to photo"
            else:
                # If we can't see it, we're already in photo mode
                print("Already in photo mode")
                return "Already in photo mode"

        elif mode.lower() == "video":
            if take_video_button.exists():
                # If we can see "Take video", we're already in video mode
                print("Already in video mode")
                return "Already in video mode"
            else:
                # If we can't see it, we need to switch to video mode
                # Look for the switch to video button
                switch_to_video = window.child_window(auto_id="CaptureButton_1")
                if switch_to_video.exists():
                    switch_to_video.click_input()
                    time.sleep(1)
                    print("Camera mode switched to video")
                    return "Camera mode switched to video"
                else:
                    print("Video mode button not found")
                    return "Video mode button not found"
        else:
            print(f"Invalid mode: {mode}. Use either 'photo' or 'video'")
            return f"Invalid mode: {mode}. Use either 'photo' or 'video'"

    except Exception as e:
        print(f"Failed to switch camera mode. Error: {e}")
        return f"Failed to switch camera mode. Error: {e}"


# def take_photo() -> Annotated[Optional[str], "Photo taken successfully."]:
#     """
#     Take a photo.
#     """
#     try:
#         app = Application(backend="uia").connect(title_re="Camera")
#         window = app.window(title_re="Camera")

#         # First ensure we're in photo mode
#         photo_result = camera_mode('photo')
#         if photo_result and "Failed" in photo_result:
#             return photo_result  # Return the error from camera_mode

#         # Find and click the take photo button
#         take_button = window.child_window(title="Take photo", auto_id="CaptureButton_0")
#         if take_button.exists() and take_button.is_enabled():
#             take_button.click_input()
#             time.sleep(1)  # Wait for photo to be taken
#             print("Photo taken successfully")
#             return "Photo taken successfully"
#         else:
#             print("Photo button is not accessible")
#             return "Photo button is not accessible"

#     except Exception as e:
#         print(f"Failed to take photo. Error: {e}")
#         return f"Failed to take photo. Error: {e}"


def take_photo(
    num_photos: Annotated[int, "Number of photos to take"] = 1,
) -> Annotated[Optional[str], "Photos taken successfully."]:
    """
    Take one or more photos. If Windows Studio Effects button exists and panel is open, closes it before taking photos.

    Args:
        num_photos (int): Number of photos to take (default: 1)
    """
    try:
        app = Application(backend="uia").connect(title_re="Camera")
        window = app.window(title_re="Camera")

        # First check if Windows Studio Effects button exists before attempting interaction
        button = window.child_window(
            title="Windows Studio Effects",
            control_type="Button",
            class_name="ToggleButton",
        )

        # Only attempt to close panel if button exists (not in FFC mode)
        if button.exists():
            if button.is_enabled() and button.get_toggle_state():
                button.click_input()
                time.sleep(1)  # Wait for panel to close
                print("Closed Windows Studio Effects panel")
        else:
            print("Windows Studio Effects button not found (possibly in FFC mode)")

        # Switch to photo mode
        photo_result = camera_mode("photo")
        if photo_result and "Failed" in photo_result:
            return photo_result  # Return the error from camera_mode

        # Find and click the take photo button
        take_button = window.child_window(title="Take photo", auto_id="CaptureButton_0")
        if take_button.exists() and take_button.is_enabled():
            for i in range(num_photos):
                take_button.click_input()
                time.sleep(2)  # Wait for photo to be taken
                print(f"Photo {i+1}/{num_photos} taken successfully")

            return (
                f"{num_photos} photo{'s' if num_photos > 1 else ''} taken successfully"
            )
        else:
            print("Photo button is not accessible")
            return "Photo button is not accessible"

    except Exception as e:
        print(f"Failed to take photos. Error: {e}")
        return f"Failed to take photos. Error: {e}"


# def take_video(duration: Annotated[float, "Recording duration in seconds"]) -> Annotated[Optional[str], "Video recorded successfully."]:
#     """
#     Record a video for a specified duration.

#     Args:
#         duration (float): Recording duration in seconds
#     """
#     try:
#         app = Application(backend="uia").connect(title_re="Camera")
#         window = app.window(title_re="Camera")

#         # Ensure we're in video mode
#         video_result = camera_mode('video')
#         if video_result and "Failed" in video_result:
#             return video_result

#         # Find the take video button by its title
#         record_button = window.child_window(title="Take video", auto_id="CaptureButton_1")
#         if not record_button.exists() or not record_button.is_enabled():
#             print("Video record button is not accessible")
#             return "Video record button is not accessible"

#         # Start recording
#         record_button.click_input()
#         print(f"Recording video for {duration} seconds...")

#         # Wait for specified duration
#         time.sleep(duration)

#         # For stopping, we need to find the stop button (might have different title when recording)
#         stop_button = window.child_window(auto_id="CaptureButton_1")
#         if stop_button.exists() and stop_button.is_enabled():
#             stop_button.click_input()
#             time.sleep(1)  # Wait for recording to finalize
#             print("Video recorded successfully")
#             return "Video recorded successfully"
#         else:
#             print("Failed to stop recording - stop button not accessible")
#             return "Failed to stop recording - stop button not accessible"

#     except Exception as e:
#         print(f"Failed to record video. Error: {e}")
#         return f"Failed to record video. Error: {e}"


def take_video(
    duration: Annotated[float, "Recording duration in seconds"],
) -> Annotated[Optional[str], "Video recorded successfully."]:
    """
    Record a video for a specified duration. If Windows Studio Effects button exists and panel is open, closes it before recording.

    Args:
        duration (float): Recording duration in seconds
    """
    try:
        app = Application(backend="uia").connect(title_re="Camera")
        window = app.window(title_re="Camera")

        # First check if Windows Studio Effects button exists before attempting interaction
        button = window.child_window(
            title="Windows Studio Effects",
            control_type="Button",
            class_name="ToggleButton",
        )

        # Only attempt to close panel if button exists (not in FFC mode)
        if button.exists():
            if button.is_enabled() and button.get_toggle_state():
                button.click_input()
                time.sleep(1)  # Wait for panel to close
                print("Closed Windows Studio Effects panel")
        else:
            print("Windows Studio Effects button not found (possibly in FFC mode)")

        # Ensure we're in video mode
        video_result = camera_mode("video")
        if video_result and "Failed" in video_result:
            return video_result

        # Find the take video button by its title
        record_button = window.child_window(
            title="Take video", auto_id="CaptureButton_1"
        )
        if not record_button.exists() or not record_button.is_enabled():
            print("Video record button is not accessible")
            return "Video record button is not accessible"

        # Start recording
        record_button.click_input()
        print(f"Recording video for {duration} seconds...")

        # Wait for specified duration
        time.sleep(duration)

        # For stopping, we need to find the stop button (might have different title when recording)
        stop_button = window.child_window(auto_id="CaptureButton_1")
        if stop_button.exists() and stop_button.is_enabled():
            stop_button.click_input()
            time.sleep(1)  # Wait for recording to finalize
            print("Video recorded successfully")
            return "Video recorded successfully"
        else:
            print("Failed to stop recording - stop button not accessible")
            return "Failed to stop recording - stop button not accessible"

    except Exception as e:
        print(f"Failed to record video. Error: {e}")
        return f"Failed to record video. Error: {e}"


def open_system_menu() -> Annotated[Optional[str], "System menu opened successfully."]:
    """
    Open the system menu in the Camera app.
    """
    try:
        app = Application(backend="uia").connect(title_re="Camera")
        window = app.window(title_re="Camera")

        # Find the system menu button
        system_menu = window.child_window(
            title="Open Settings Menu", auto_id="settingsButton", control_type="Button"
        )

        if system_menu.exists() and system_menu.is_enabled():
            system_menu.click_input()
            time.sleep(1)  # Wait for menu to open
            print("System menu opened successfully")
            return "System menu opened successfully"
        else:
            print("System menu is not accessible")
            return "System menu is not accessible"

    except Exception as e:
        print(f"Failed to open system menu. Error: {e}")
        return f"Failed to open system menu. Error: {e}"


def open_photo_settings() -> (
    Annotated[Optional[str], "Photo settings opened successfully."]
):
    """
    Open the photo settings menu in the Camera app.
    """
    try:
        app = Application(backend="uia").connect(title_re="Camera")
        window = app.window(title_re="Camera")

        # Find the photo settings button
        settings_button = window.child_window(
            title="Photo settings", control_type="Button"
        )

        if settings_button.exists() and settings_button.is_enabled():
            settings_button.click_input()
            time.sleep(0.5)  # Wait for settings to open
            print("Photo settings opened successfully")
            return "Photo settings opened successfully"
        else:
            print("Photo settings button is not accessible")
            return "Photo settings button is not accessible"

    except Exception as e:
        print(f"Failed to open photo settings. Error: {e}")
        return f"Failed to open photo settings. Error: {e}"


def open_video_settings() -> (
    Annotated[Optional[str], "Video settings opened successfully."]
):
    """
    Open the video settings menu in the Camera app.
    """
    try:
        app = Application(backend="uia").connect(title_re="Camera")
        window = app.window(title_re="Camera")

        # Find the photo settings button
        settings_button = window.child_window(
            title="Video settings", control_type="Button"
        )

        if settings_button.exists() and settings_button.is_enabled():
            settings_button.click_input()
            time.sleep(0.5)  # Wait for settings to open
            print("Video settings opened successfully")
            return "Video settings opened successfully"
        else:
            print("Video settings button is not accessible")
            return "Video settings button is not accessible"

    except Exception as e:
        print(f"Failed to open video settings. Error: {e}")
        return f"Failed to open video settings. Error: {e}"


def open_video_quality() -> (
    Annotated[Optional[Any], "Video quality ComboBox or error message"]
):
    """
    Open the video quality settings in the Camera app.
    Returns the ComboBox element if successful, error message string if not.
    """
    try:
        app = Application(backend="uia").connect(title_re="Camera")
        window = app.window(title_re="Camera")

        # Find all video quality ComboBoxes
        video_qualities = window.children(
            title="Video quality", control_type="ComboBox"
        )

        if not video_qualities:
            print("Video quality settings not found")
            return "Video quality settings not found"

        # Use the first ComboBox we find
        video_quality = video_qualities[0]

        if video_quality.exists() and video_quality.is_enabled():
            video_quality.click_input()
            time.sleep(0.5)  # Wait for menu to open
            print("Video quality settings opened successfully")
            return video_quality
        else:
            print("Video quality settings are not accessible")
            return "Video quality settings are not accessible"

    except Exception as e:
        print(f"Failed to open video quality settings. Error: {e}")
        return f"Failed to open video quality settings. Error: {e}"


def get_video_quality_options() -> (
    Annotated[list[str], "List of available video quality options"]
):
    """
    Get a list of all available video quality options from the Camera app.

    Returns:
        list[str]: List of available quality options (e.g., ['1440p 16:9 30fps', ...])
    """
    try:
        app = Application(backend="uia").connect(title_re="Camera")
        window = app.window(title_re="Camera")

        # Find the video quality ComboBox
        quality_combo = window.child_window(
            title="Video quality", control_type="ComboBox"
        )

        if not quality_combo.exists():
            print("Video quality ComboBox not found")
            return []

        # Click and send Down key to expand the ComboBox
        quality_combo.click_input()
        time.sleep(0.5)
        from pywinauto.keyboard import send_keys

        send_keys("{VK_DOWN}")
        time.sleep(0.5)

        # Get unique quality options (using the shorter format)
        quality_options = set()
        for desc in window.descendants():
            text = desc.window_text()
            # Only get the shorter format options (e.g., "1080p 16:9 30fps")
            if (
                any(res in text for res in ["1080p", "720p", "1440p", "480p", "360p"])
                and ":" in text
            ):
                quality_options.add(text)

        # Convert to sorted list
        quality_options = sorted(
            list(quality_options),
            key=lambda x: (int(x.split("p")[0]), "16:9" in x),
            reverse=True,
        )

        print(f"Found {len(quality_options)} video quality options: {quality_options}")
        return quality_options

    except Exception as e:
        print(f"Failed to get video quality options. Error: {e}")
        return []


def set_video_quality(quality: str) -> str:
    try:
        app = Application(backend="uia").connect(title_re="Camera")

        # Click through menus to open video quality
        app.window(title_re="Camera").menu_select("Settings->Video settings")

        # Get the ComboBox and click it to open
        quality_combo = app.window(title_re="Camera").child_window(
            title="Video quality", control_type="ComboBox"
        )
        quality_combo.click_input()

        # Use type_keys for keyboard navigation
        # First go to top
        for _ in range(10):
            app.window(title_re="Camera").type_keys("{UP}")
            time.sleep(0.1)

        # Now move to desired option
        quality_list = [
            "1440p 16:9 30fps",
            "1440p 4:3 30fps",
            "1080p 16:9 30fps",
            "1080p 4:3 30fps",
            "720p 16:9 30fps",
            "480p 4:3 30fps",
            "360p 16:9 30fps",
        ]

        target_index = quality_list.index(quality)
        for _ in range(target_index):
            app.window(title_re="Camera").type_keys("{DOWN}")
            time.sleep(0.1)

        # Select with enter
        app.window(title_re="Camera").type_keys("{ENTER}")

        return f"Set quality to {quality}"

    except Exception as e:
        return f"Error: {str(e)}"
