import csv
import io

from PIL import Image
from selenium import webdriver
import time
import os

from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class DatasetsBuilder:
    def __init__(self):
        self.BASE_URL = "https://euphonious-concha-ab5c5d.netlify.app/"
        self.OUTPUT_DIR = "datasets"
        os.makedirs(self.OUTPUT_DIR, exist_ok=True)

        self.h_components_xpath = {
            "front_left": "/html/body/div/div/div[2]/button[1]",
            "front_right": "/html/body/div/div/div[2]/button[2]",
            "rear_left": "/html/body/div/div/div[2]/button[3]",
            "rear_right": "/html/body/div/div/div[2]/button[4]",
            "hood": "/html/body/div/div/div[2]/button[5]"
        }

        self.component_names = ["front_left", "front_right", "rear_left", "rear_right", "hood"]

        self.h_components_states = {name: "closed" for name in self.component_names}

        self.camera_views = [
            "view_side_left", "view_front",
            "view_side_right", "view_right",
            "view_rear_side_right", "view_rear",
            "view_rear_side_left", "view_left"
        ]

        self.tilt_idx = 0

        chrome_profile = os.path.join(os.getcwd(), "chrome_profile")  # Creates in current working directory

        if not os.path.exists(chrome_profile):
            os.makedirs(chrome_profile)
            print(f"Created dummy profile directory at: {chrome_profile}")

        chrome_options = Options()
        chrome_options.add_argument(f"user-data-dir={chrome_profile}")

        self.driver = webdriver.Chrome(options=chrome_options)
        self.actions = ActionChains(self.driver)

        self.view_name = ""
        self.camera_view_idx = 0
        self.filename = ''
        self.interactive_area = None

        self.csv_filename = "annotations.csv"
        self.csv_file_path = os.path.join(self.OUTPUT_DIR, self.csv_filename)
        self.csv_file = None
        self.csv_writer = None

        self.mouse_start_x = 0
        self.mouse_start_y = 0


    def set_component_state(self, component_name, desired_state):
        """
        Sets a component to the desired_state ('opened' or 'closed').
        Assumes the corresponding button on the webpage acts as a toggle.
        Updates self.h_components_states to reflect the attempted change.
        """
        current_known_state = self.h_components_states.get(component_name)

        if current_known_state != desired_state:
            print(f"Attempting to set {component_name} from {current_known_state} to {desired_state}...")
            btn_xpath = self.h_components_xpath[component_name]
            try:
                btn_element = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, btn_xpath))
                )
                btn_element.click()
                time.sleep(0.2)
                self.h_components_states[component_name] = desired_state
                print(f"{component_name} state changed to {desired_state}.")

            except Exception as e:
                print(f"Error clicking button for {component_name} to change to {desired_state}: {e}")
        else:
            print(f"{component_name} is already in desired state: {desired_state}.")

    def reset_all_components_to_closed_on_page(self):
        """
        Ensures all components are physically set to 'closed' on the webpage
        by clicking buttons if self.h_components_states shows them as 'opened'.
        This method updates self.h_components_states as it operates.
        """
        print("\nResetting all components to 'closed' state on the page...")
        for component_name in self.component_names:
            if self.h_components_states.get(component_name) == 'opened':
                self.set_component_state(component_name, "closed")

    def move_camera_view_horizontally(self, x_offset=113, y_offset=0):
        """
        Moves the camera view.
        By default it moves horizontally.
        Updates self.camera_view_idx and self.view_name.
        This should be called *after* processing all component states for the current view.
        """
        if self.interactive_area is None:
            print("Error: Interactive area not found. Cannot move camera.")
            return

        # Check if we are already at the last view to avoid unnecessary moves
        if self.camera_view_idx >= len(self.camera_views) - 1:
            print("Already at the last camera view. No more horizontal moves.")
            return

        print(f"Moving camera horizontally from {self.view_name}...")

        self.actions \
            .move_to_element_with_offset(self.interactive_area, self.mouse_start_x, self.mouse_start_y) \
            .click_and_hold() \
            .move_by_offset(x_offset, y_offset) \
            .release() \
            .perform()

        time.sleep(0.2)

        self.camera_view_idx += 1
        self.view_name = self.camera_views[self.camera_view_idx]
        print(f"Camera moved. New view: {self.view_name} (index: {self.camera_view_idx})")


    def move_camera_tilt(self, x_offset=0, y_offset=10):
        print(f"Moving camera tilt from {self.view_name}...")

        self.actions \
            .move_to_element_with_offset(self.interactive_area, self.mouse_start_x, self.mouse_start_y) \
            .click_and_hold() \
            .move_by_offset(x_offset, y_offset) \
            .release() \
            .perform()

        time.sleep(0.2)

    def capture_screenshot(self, crop_size=(1600, 1600)):
        """
        Sets the filename based on current component states and view, then captures a screenshot.
        """
        self.set_filename()  # Ensure filename is up-to-date
        screenshot_path = os.path.join(self.OUTPUT_DIR, self.filename)

        try:
            self.hide_button()
            # Get screenshot as PNG bytes
            png_screenshot = self.driver.get_screenshot_as_png()
            img = Image.open(io.BytesIO(png_screenshot))

            # Get image dimensions
            width, height = img.size

            # Calculate cropping box coordinates
            crop_width, crop_height = crop_size
            left = (width - crop_width) / 2
            top = (height - crop_height) / 2
            right = (width + crop_width) / 2
            bottom = (height + crop_height) / 2

            # Ensure crop coordinates are within image bounds and are integers
            left, top, right, bottom = int(left), int(top), int(right), int(bottom)

            # Crop the image
            img_cropped = img.crop((left, top, right, bottom))

            # reduce dimension 5 times lower 1600,1600 -> 320 x 320 by default
            resize_target_size = (int(crop_size[0]/5), int(crop_size[1]/5))
            img_processed = img_cropped.resize(resize_target_size, Image.Resampling.LANCZOS)

            # Save the cropped image
            img_processed.save(screenshot_path)

            self.show_button()

            print(f"Captured and cropped: {self.filename}")

        except Exception as e:
            print(f"Error capturing or cropping screenshot {self.filename}: {e}")

    def set_filename(self):
        """
        Generates a filename based on the current camera view and the states of all components.
        Uses the order from self.component_names for consistency.
        """
        filename_parts = []
        for comp_name in self.component_names:
            state = self.h_components_states.get(comp_name, "unknown")
            filename_parts.append(f"{comp_name}_{state}")

        states_string = "_".join(filename_parts)
        current_view_for_filename = self.camera_views[self.camera_view_idx]
        self.filename = f"{current_view_for_filename}_{states_string}_{self.tilt_idx}.png"

    def init_csv(self):
        self.csv_file = open(self.csv_file_path, 'w', newline='')
        self.csv_writer = csv.writer(self.csv_file)
        header = ["filename"] + self.component_names  # CSV Header
        self.csv_writer.writerow(header)

    def hide_button(self):
        # hide the button
        button_element = self.driver.find_element(By.XPATH, "/html/body/div/div/div[2]")
        self.driver.execute_script("arguments[0].style.opacity='0';", button_element)

    def show_button(self):
        # hide the button
        button_element = self.driver.find_element(By.XPATH, "/html/body/div/div/div[2]")
        self.driver.execute_script("arguments[0].style.opacity='100';", button_element)

    def move_on_clickable_zone(self):
        safe_x = int(self.canvas_width * 0.2)
        safe_y = int(self.canvas_height * 0.2)

        return safe_x, safe_y

    def generate_annotation(self):
        """
        Logs the current filename and component states to the CSV file.
        States are logged as 0 for 'closed' and 1 for 'opened'.
        """
        if not self.csv_writer:
            print("Error: CSV writer not initialized. Cannot log data.")
            return

        try:
            row_data = [self.filename]
            for comp_name in self.component_names:  # Ensure consistent order
                state = self.h_components_states.get(comp_name, "closed")  # Default to 'closed' if not found
                row_data.append(1 if state == "opened" else 0)

            self.csv_writer.writerow(row_data)
            # print(f"Logged to CSV: {row_data}") # Optional: for verbose logging
        except Exception as e:
            print(f"Error writing to CSV for file {self.filename}: {e}")

    def run(self):
        """
        Main execution function.
        Outer loop: Iterates through camera views.
        Inner loop: Iterates through all 32 component state combinations.
        """
        self.init_csv()

        self.driver.get(self.BASE_URL)
        print(f"Opened base URL: {self.BASE_URL}")
        time.sleep(3)

        canvas_locator = (By.TAG_NAME, "canvas")
        print(f"Waiting for interactive canvas element: {canvas_locator}")
        try:
            self.interactive_area = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located(canvas_locator)
            )
            print("Interactive canvas element found.")

            interactive_area_size = self.interactive_area.size

            interactive_area_size_width = interactive_area_size['width']
            interactive_area_size_height = interactive_area_size['height']
            interactive_area_size_center_x = interactive_area_size_width / 2
            interactive_area_size_center_y = interactive_area_size_height / 2

            self.mouse_start_x = int(interactive_area_size_width * 0.85) - interactive_area_size_center_x
            self.mouse_start_y = int(interactive_area_size_height * 0.85) - interactive_area_size_center_y


        except Exception as e:
            print(f"Fatal: Could not find interactive canvas element. Exiting. Error: {e}")
            self.driver.quit()
            return

        num_components = len(self.component_names)
        total_combinations = 2 ** num_components


        # self.driver.switch_to.window(self.driver.current_window_handle)

        # self.actions.key_down(Keys.COMMAND).send_keys(Keys.SUBTRACT).key_up(Keys.COMMAND).perform()

        for tilt_idx in range(10):
            print(f"\n\n===== TILT LOOP #{tilt_idx} ========")
            self.tilt_idx = tilt_idx

            # Outer loop: Iterate through each camera view
            for view_idx in range(len(self.camera_views)):
                self.camera_view_idx = view_idx
                self.view_name = self.camera_views[self.camera_view_idx]
                print(f"\n\n===== CAMERA VIEW LOOP #{view_idx} ========")
                print(f"Processing Camera View: {self.view_name} ({self.camera_view_idx + 1}/{len(self.camera_views)})")
                print(f"Tilt: {self.tilt_idx})")

                # Inner loop: Iterate through all 32 component state combinations
                for i in range(total_combinations):  # Iterate from 0 to 31
                    print(f"\n\n===== COMBINATION LOOP #{i} ========")
                    print(f"\nProcessing Combination {i + 1}/{total_combinations} for view {self.view_name}")

                    # 1. Reset all components to 'closed' on the page.
                    self.reset_all_components_to_closed_on_page()

                    # 2. Determine and set the target states for the current combination 'i'.
                    target_states_for_this_combination = {}
                    for comp_idx, component_name in enumerate(self.component_names):
                        if (i >> (num_components - 1 - comp_idx)) & 1:
                            target_states_for_this_combination[component_name] = "opened"
                        else:
                            target_states_for_this_combination[component_name] = "closed"

                    # 3. Apply the target states.
                    for component_name, desired_state in target_states_for_this_combination.items():
                        if desired_state == "opened":
                            self.set_component_state(component_name, "opened")

                    print(f"Current component states after setting for combination {i}: {self.h_components_states}")

                    # 4. Capture screenshot for the current view and component combination
                    self.capture_screenshot()

                    # 5. Log the state to CSV
                    self.generate_annotation()

                    time.sleep(0.2)

                    print("Next combination....")
                    print("--------------------------")

                # After processing all 32 combinations for the current view, move the camera view!
                if self.camera_view_idx < len(self.camera_views) - 1:
                    self.move_camera_view_horizontally()
                    print("Next camera view....")
                    print("--------------------------")
                else:
                    print(f"Finished all combinations for the last view: {self.view_name}")

            self.move_camera_tilt()
            print("Next tilt")
            print("--------------------------")

        print("\nData acquisition finished for all views and combinations.")
        self.driver.quit()
        print("Browser closed.")


if __name__ == '__main__':
    dataset_builder = DatasetsBuilder()
    dataset_builder.run()