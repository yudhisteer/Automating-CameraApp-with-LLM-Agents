import sys
import time
import subprocess
from pywinauto import Application


class MEPControllerCameraApp:
    def __init__(self):
        self._eye_contact_map = {"OFF": 0, "STD": 3, "TLP": 4}
        self._background_effect_map = {"OFF": 0, "STD": 5, "PORT": 6}
        self._creative_filter_map = {"OFF": 0, "ILU": 7, "ANI": 8, "WTR": 9}
        self._auto_framing_map = {"OFF": 0, "ON": 1}
        self._portrait_light_map = {"OFF": 0, "ON": 2}

    def open_camera(self):
        try:
            subprocess.run("start microsoft.windows.camera:", shell=True, check=True)
            print("Camera app opened successfully.")
            time.sleep(3)
        except subprocess.CalledProcessError as e:
            print(f"Failed to open the Camera app. Error: {e}")

    def close_camera(self):
        try:
            app = Application(backend="uia").connect(title_re="Camera")
            window = app.window(title_re="Camera")
            window.close()
            print("Camera app closed successfully.")
        except Exception as e:
            print(f"Failed to close the Camera app. Error: {e}")

    def click_windows_studio_effects(self):
        try:
            app = Application(backend="uia").connect(title_re="Camera")
            window = app.window(title_re="Camera")
            button = window.child_window(
                title="Windows Studio Effects",
                control_type="Button",
                class_name="ToggleButton"
            )
            if button.exists() and button.is_enabled():
                button.click_input()
                time.sleep(1)
                print("'Windows Studio Effects' button clicked.")
            else:
                print("'Windows Studio Effects' button is not accessible.")
        except Exception as e:
            print(f"Failed to interact with 'Windows Studio Effects' button. Error: {e}")

    def toggle_feature(self, feature_name, desired_state, class_name="ToggleSwitch"):
        try:
            app = Application(backend="uia").connect(title_re="Camera")
            window = app.window(title_re="Camera")
            toggle_button = window.child_window(
                title=feature_name,
                control_type="Button",
                class_name=class_name
            )
            if not toggle_button.exists() or not toggle_button.is_enabled():
                print(f"{feature_name} toggle is not accessible.")
                return
            current_state = toggle_button.get_toggle_state()
            if desired_state > 0:  # ON states (e.g., 1 or 2)
                if current_state == 0:
                    toggle_button.click_input()
                    print(f"'{feature_name}' toggled to ON.")
                else:
                    print(f"'{feature_name}' is already ON.")
            else:  # OFF state
                if current_state == 1:
                    toggle_button.click_input()
                    print(f"'{feature_name}' toggled to OFF.")
                else:
                    print(f"'{feature_name}' is already OFF.")
        except Exception as e:
            print(f"Failed to toggle '{feature_name}'. Error: {e}")

    def select_radio_button(self, radio_name):
        try:
            app = Application(backend="uia").connect(title_re="Camera")
            window = app.window(title_re="Camera")
            radio_button = window.child_window(
                title=radio_name,
                control_type="RadioButton"
            )
            if radio_button.exists() and not radio_button.is_selected():
                radio_button.click_input()
                print(f"'{radio_name}' radio button selected.")
            else:
                print(f"'{radio_name}' is already selected or not accessible.")
        except Exception as e:
            print(f"Failed to select '{radio_name}' radio button. Error: {e}")

    def toggle_features(self, auto_framing, portrait_light, eye_contact, background_effect, creative_filter):
        try:
            self.click_windows_studio_effects()

            if auto_framing:
                desired_state = self._auto_framing_map.get(auto_framing.upper(), 0)
                self.toggle_feature("Automatic framing", desired_state)

            if portrait_light:
                desired_state = self._portrait_light_map.get(portrait_light.upper(), 0)
                self.toggle_feature("Portrait light", desired_state)

            if eye_contact:
                desired_state = self._eye_contact_map.get(eye_contact.upper(), 0)
                if desired_state == 0:
                    self.toggle_feature("Eye contact", 0)
                elif desired_state in [3, 4]:
                    self.toggle_feature("Eye contact", 1)
                    if desired_state == 3:
                        self.select_radio_button("Standard")
                    elif desired_state == 4:
                        self.select_radio_button("Teleprompter")

            if background_effect:
                desired_state = self._background_effect_map.get(background_effect.upper(), 0)
                if desired_state == 0:
                    self.toggle_feature("Background effects", 0)
                elif desired_state in [5, 6]:
                    self.toggle_feature("Background effects", 1)
                    if desired_state == 5:
                        self.select_radio_button("Standard blur")
                    elif desired_state == 6:
                        self.select_radio_button("Portrait blur")

            if creative_filter:
                desired_state = self._creative_filter_map.get(creative_filter.upper(), 0)
                if desired_state == 0:
                    self.toggle_feature("Creative filters", 0)
                elif desired_state in [7, 8, 9]:
                    self.toggle_feature("Creative filters", 1)
                    if desired_state == 7:
                        self.select_radio_button("Illustrated")
                    elif desired_state == 8:
                        self.select_radio_button("Animated")
                    elif desired_state == 9:
                        self.select_radio_button("Water color")
        except Exception as e:
            print(f"Error toggling features: {e}")


def main():
    if len(sys.argv) != 6:
        print("Usage: python camera_app_mep_controller.py <auto_framing> <portrait_light> <eye_contact> <background_effect> <creative_filter>")
        print("Example: python camera_app_mep_controller.py ON OFF STD STD ILU")
        return

    auto_framing = sys.argv[1]
    portrait_light = sys.argv[2]
    eye_contact = sys.argv[3]
    background_effect = sys.argv[4]
    creative_filter = sys.argv[5]

    controller = MEPControllerCameraApp()
    controller.open_camera()
    controller.toggle_features(auto_framing, portrait_light, eye_contact, background_effect, creative_filter)
    controller.close_camera()


if __name__ == "__main__":
    main()
