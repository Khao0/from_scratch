import pygame
import pygame_gui
import tkinter as tk
from tkinter import filedialog
import os
import sys
import warnings
from cal_tw import *


warnings.simplefilter("ignore", UserWarning)


def main():
    # Initialize Tkinter (for file dialogs)
    root = tk.Tk()
    root.withdraw()  # Hide the main tkinter window

    pygame.init()

    # Set up the window
    SCREEN_WIDTH = 1200
    SCREEN_HEIGHT = 800
    pygame.display.set_caption("Bone Age Labeling Tool")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # Set up the background
    background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    background.fill(pygame.Color("#000000"))  # Black background

    # Create the UI Manager
    manager = pygame_gui.UIManager(
        (SCREEN_WIDTH, SCREEN_HEIGHT), theme_path="theme.json"
    )

    clock = pygame.time.Clock()
    is_running = True

    # State variables
    current_page = 1

    # 1st page
    # select_input_btn = None
    # select_output_btn = None
    # input_path_label =None
    # output_path_label = None
    # next_btn
    first_page_objs = []
    input_folder = ""
    output_folder = ""

    # 2nd page
    images = []
    current_image_index = 0
    bone_labels_list = [
        "Radius",
        "Ulnar",
        "1st Metacarpal",
        "3rd Metacarpal",
        "5th Metacarpal",
        "Proximal Phalange of Thumb",
        "3rd Proximal Phalange",
        "5th Proximal Phalange",
        "3rd Middle Phalange",
        "5th Middle Phalange",
        "Distal Phalange of Thumb",
        "3rd Distal Phalange",
        "5th Distal Phalange",
    ]
    dropdown_options = ["A-I", "A", "B", "C", "D", "E", "F", "G", "H", "I"]
    dropdown_gender_options = ["M/F", "Male", "Female"]
    scroll_container = None
    progress_bar = None
    calculate_button = None
    dropdowns = []
    dropdowns_gender = []
    input_boxes = []
    ex_input_boxes = []
    ex_dropdowns = []
    ex_dropdowns_gender = []

    # Initialize UI Elements for Page 1
    def init_1st_page():
        desc_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((50, 50), (300, 50)),
            text="Description",
            manager=manager,
        )

        description = pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect((50, 100), (1100, 350)),
            html_text=(
                """
                The first page allows users to set up the required inputs before progressing to the main functionality.
                1. Select Gender (Dropdown menu: Male/Female)
                2. Choose Bone Maturity Scores for different bones
                3. Review Entered Data before proceeding
                4. Click 'Calculate' TW to compute the Tanner-Whitehouse (TW) bone age score
                5. Analyze by Greulish-Pyle Approach
                6. Summarized the Bone Age
                7. Save by 'Cmd+s'
                8. Go to Next Image by 'd'
                9. Go to Previous Image by 'a'
                Once all selections are made, users can proceed to Page 2, where they can view results, visualizations, or make further adjustments.
            """
            ),
            manager=manager,
        )

        select_input_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((50, 475), (300, 50)),
            text="Select Input Folder",
            manager=manager,
        )

        select_output_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((50, 535), (300, 50)),
            text="Select Output Folder",
            manager=manager,
        )

        input_path_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((400, 475), (750, 50)),
            text="Input Folder: Not Selected",
            manager=manager,
        )

        output_path_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((400, 535), (750, 50)),
            text="Output Folder: Not Selected",
            manager=manager,
        )

        next_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((950, 605), (200, 50)),
            text="Next",
            manager=manager,
        )
        next_btn.disable()  # Disable until folders are selected

        return [
            select_input_btn,
            select_output_btn,
            input_path_label,
            output_path_label,
            desc_label,
            description,
            next_btn,
        ]

    first_page_objs = init_1st_page()

    # Function to load images from input folder
    def load_images(folder_path):
        supported_extensions = [".png", ".jpg", ".jpeg"]
        files = [
            f
            for f in os.listdir(folder_path)
            if os.path.splitext(f)[1].lower() in supported_extensions
        ]
        files.sort()
        return files

    # Function to load the current image
    def load_current_image():
        nonlocal image_surface
        if images:
            image_path = os.path.join(input_folder, images[current_image_index])
            try:
                loaded_image = pygame.image.load(image_path)
                # Scale image to fit 80% of screen width and full height
                image_width = int(
                    SCREEN_WIDTH * 0.75
                )  # Adjusted to 75% to make room for container
                image_height = SCREEN_HEIGHT
                image_surface = pygame.transform.scale(
                    loaded_image, (image_width, image_height)
                )
            except Exception as e:
                print(f"Error loading image {image_path}: {e}")
                image_surface = None

    # Initialize Scrolling Container and Input Boxes
    def load_existing_inputs():
        nonlocal ex_dropdowns_gender, ex_dropdowns, ex_input_boxes
        image_name = os.path.splitext(images[current_image_index])[0]
        label_path = os.path.join(output_folder, image_name + ".txt")
        if os.path.exists(label_path):
            try:
                with open(label_path, "r") as f:
                    lines = f.readlines()
                    # print(lines)
                    ex_dropdowns_gender = []
                    ex_dropdowns = []
                    ex_input_boxes = []

                    ex_dropdowns_gender.append(lines[0].strip())

                    # print(f"Ex Gender {ex_dropdowns_gender}")
                    # print(f"Value : {lines[0].strip()}")

                    for i in range(1, 14):
                        ex_dropdowns.append(lines[i].strip())
                    for i in range(14, 20):
                        ex_input_boxes.append(lines[i].strip())

            except Exception as e:
                print(f"Error loading labels: {e}")

        else:
            # If label file doesn't exist, set dropdowns to default
            ex_dropdowns_gender = ["M/F"]
            ex_dropdowns = ["A-I" for _ in range(13)]
            ex_input_boxes = ["" for _ in range(8)]

        # print(ex_dropdowns_gender)
        # print(ex_dropdowns)
        # print(ex_input_boxes)

    def init_bones_labels_inputs_scrolling():
        nonlocal scroll_container, dropdowns, dropdowns_gender, input_boxes, calculate_button

        if scroll_container is not None:
            scroll_container.kill()

        # Clear all lists of UI elements
        dropdowns = []
        dropdowns_gender = []
        input_boxes = []
        # Create a scrolling container on the right side
        scroll_container, dropdowns, dropdowns_gender, input_boxes, calculate_button = (
            init_bones_labels_inputs_scrolling_function(
                manager, SCREEN_WIDTH, SCREEN_HEIGHT, bone_labels_list
            )
        )

    def init_bones_labels_inputs_scrolling_function(
        manager, screen_width, screen_height, bone_labels_list
    ):
        container_width, container_height = int(screen_width * 0.2), min(
            700, screen_height - 100
        )
        container_x, container_y, padding = screen_width - container_width - 20, 50, 10
        scrolling_container = pygame_gui.elements.UIScrollingContainer(
            relative_rect=pygame.Rect(
                (container_x, container_y), (container_width, container_height)
            ),
            manager=manager,
            allow_scroll_y=True,
            visible=True,
        )

        current_y, dropdowns, input_boxes, dropdowns_gender = padding, [], [], []
        nonlocal dropdown_gender_options, dropdown_options

        # * ==== Gender ==== *
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((padding, current_y), (80, 30)),
            text="Gender",
            manager=manager,
            container=scrolling_container,
        )
        gender_input = pygame_gui.elements.UIDropDownMenu(
            relative_rect=pygame.Rect((padding + 90, current_y), (100, 30)),
            options_list=dropdown_gender_options,
            starting_option=ex_dropdowns_gender[0],
            manager=manager,
            container=scrolling_container,
        )
        dropdowns_gender.append(gender_input)
        current_y += 40

        # * ==== Bone Labels ==== *
        for i, label_text in enumerate(bone_labels_list):
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect((padding, current_y), (80, 30)),
                text=label_text,
                manager=manager,
                container=scrolling_container,
            )
            dropdowns.append(
                pygame_gui.elements.UIDropDownMenu(
                    relative_rect=pygame.Rect((padding + 90, current_y), (100, 30)),
                    options_list=dropdown_options,
                    starting_option=ex_dropdowns[i],
                    manager=manager,
                    container=scrolling_container,
                )
            )
            current_y += 40

        # * ==== Calculate TW Button ==== *
        calculate_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((padding, current_y), (200, 30)),
            text="Calculate TW",
            manager=manager,
            container=scrolling_container,
        )
        current_y += 40

        # * ==== Bone Age Fields ==== *
        def add_labeled_entry(y_offset, text):
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect((padding, y_offset), (200, 30)),
                text=text,
                manager=manager,
                container=scrolling_container,
            )
            return y_offset + 30

        def add_age_fields(
            y_offset: int, input_boxes: list, ex_vals: list, dis_condition: bool
        ):
            # values = []
            # print(ex_vals)
            for i, label in enumerate(["Year(s)", "Month(s)"]):
                # field =

                field = pygame_gui.elements.UITextEntryLine(
                    relative_rect=pygame.Rect((padding + i * 105, y_offset), (50, 30)),
                    manager=manager,
                    initial_text=ex_vals[i],
                    container=scrolling_container,
                )

                if dis_condition:
                    field.disable()
                input_boxes.append(field)

                pygame_gui.elements.UILabel(
                    relative_rect=pygame.Rect(
                        (padding + i * 105 + 55, y_offset), (60, 30)
                    ),
                    text=label,
                    manager=manager,
                    container=scrolling_container,
                )
                # values.append(field)
            return y_offset + 40, input_boxes  # values

        current_y = add_labeled_entry(current_y, "Tanner-Whitehouse Method")
        current_y, input_boxes = add_age_fields(
            current_y, input_boxes, ex_input_boxes[0:2], True
        )
        current_y = add_labeled_entry(current_y, "Greulich-Pyle Method")
        current_y, input_boxes = add_age_fields(
            current_y, input_boxes, ex_input_boxes[2:4], False
        )
        current_y = add_labeled_entry(current_y, "Finalized Bone Age")
        current_y, input_boxes = add_age_fields(
            current_y, input_boxes, ex_input_boxes[4:6], False
        )

        scrolling_container.set_scrollable_area_dimensions(
            (container_width - 20, current_y + 20)
        )
        return (
            scrolling_container,
            dropdowns,
            dropdowns_gender,
            input_boxes,
            calculate_button,
        )

    def tw_calculation(gender: str, dropdowns_str: list):
        print("Pass to tw calculation")
        sum_bone_score = 0
        bone_score_table, maturity_score_table, bone_age_table = get_gender_tables(
            gender
        )
        for i in range(13):
            bone = bone_labels_list[i]
            label = dropdowns_str[i]
            label = convert_alp_num(label)
            bone_score = bone_score_table[bone][label]
            sum_bone_score += bone_score
        print(f"Sum Bone Score : {sum_bone_score}")
        lower_idx, upper_idx = binary_search_insert_indices(
            maturity_score_table, sum_bone_score
        )
        print(f"lower index : {lower_idx}, upper index :{upper_idx}")
        if not (lower_idx or upper_idx):
            # case that can't predict due to not in the maturity bound
            print(f"Pass out of bound bone maturity case")
            return "", ""
        elif lower_idx == upper_idx:
            ba_y, ba_m = convert_y2ym(bone_age_table[lower_idx])
            print("No need for interpolation")
            print(f"Bone Age Year : {ba_y}, Bone Age Month : {ba_m}")
            return ba_y, ba_m
        else:  # need to interpolate
            ba = linear_interpolation(
                maturity_score_table, bone_age_table, sum_bone_score, lower_idx
            )
            print(f"Bone Age : {ba}")
            print("interpolation case")
            ba_y, ba_m = convert_y2ym(ba)
            print(f"Bone Age Year : {ba_y}, Bone Age Month : {ba_m}")
            return ba_y, ba_m

    def handle_tw_calculation():
        nonlocal dropdowns_gender, dropdowns, input_boxes
        print("Pass Handle TW")
        gender_cond = True
        dropdowns_cond = True
        gender = dropdowns_gender[0].selected_option
        gender = gender[0]
        print(f"Gender : {gender}")
        if gender == "M/F":
            gender_cond = False

        dropdowns_str = []
        for dropdown in dropdowns:
            text = dropdown.selected_option
            text = text[0]
            print(f"Text : {text}")
            if text == "A-I":
                dropdowns_cond = False
            dropdowns_str.append(text)

        if gender_cond and dropdowns_cond:
            print("Pass the conditions")
            ba_y, ba_m = tw_calculation(gender, dropdowns_str)
            input_boxes[0].set_text(str(ba_y))
            input_boxes[1].set_text(str(ba_m))

    def update_progress_bar():
        if progress_bar and images:
            progress = (current_image_index + 1) / len(images) * 100
            progress_bar.set_current_progress(progress)

    # Function to switch to Page 2
    def switch_to_page2():
        nonlocal current_page, progress_bar, first_page_objs
        current_page = 2

        # Hide Page 1 elements
        for obj in first_page_objs:
            obj.hide()

        # progress bar
        progress_bar = pygame_gui.elements.UIProgressBar(
            relative_rect=pygame.Rect(
                (20, SCREEN_HEIGHT - 40), (SCREEN_WIDTH - 40, 20)
            ),
            manager=manager,
        )
        update_progress_bar()

        # Show Page 2 elements
        load_current_image()
        load_existing_inputs()
        init_bones_labels_inputs_scrolling()

    # Function to load images and initialize image_surface
    image_surface = None

    while is_running:
        time_delta = clock.tick(60) / 1000.0  # Seconds since last frame

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False

            # Handle button presses
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == first_page_objs[0]:
                    selected = filedialog.askdirectory()
                    if selected:
                        input_folder = selected
                        first_page_objs[2].set_text(f"Input Folder: {input_folder}")
                        # Load images
                        images = load_images(input_folder)
                        print(f"Found {len(images)} images.")
                        # Enable 'Next' button if both folders are selected
                        if output_folder:
                            first_page_objs[-1].enable()
                elif event.ui_element == first_page_objs[1]:
                    selected = filedialog.askdirectory()
                    if selected:
                        output_folder = selected
                        first_page_objs[3].set_text(f"Output Folder: {output_folder}")
                        # Enable 'Next' button if both folders are selected
                        if input_folder:
                            first_page_objs[-1].enable()
                elif event.ui_element == first_page_objs[-1]:  # nextBtn
                    if images:
                        switch_to_page2()
                elif event.ui_element == calculate_button:
                    print("Pass Put button")
                    handle_tw_calculation()

            # Handle key presses
            if current_page == 2 and event.type == pygame.KEYDOWN:
                # Handle Save (Ctrl+S or Cmd+S)
                if (
                    pygame.key.get_mods() & pygame.KMOD_CTRL and event.key == pygame.K_s
                ) or (
                    sys.platform == "darwin"
                    and pygame.key.get_mods() & pygame.KMOD_META
                    and event.key == pygame.K_s
                ):
                    # Retrieve labels from input boxes
                    gender = dropdowns_gender[0].selected_option
                    dropdown_texts = []
                    for dropdown in dropdowns:
                        text = dropdown.selected_option
                        dropdown_texts.append(text[0])
                    input_texts = [str(box.get_text()) for box in input_boxes]

                    save_list = [gender[0]] + dropdown_texts + input_texts + ["", ""]

                    # * ==== Save to .txt file ==== *
                    if images:
                        image_name = os.path.splitext(images[current_image_index])[0]
                        label_path = os.path.join(output_folder, image_name + ".txt")
                        try:
                            with open(label_path, "w") as f:
                                for label in save_list:
                                    f.write(label + "\n")
                            print(f"Labels saved to {label_path}")
                        except Exception as e:
                            print(f"Error saving labels: {e}")

                #  * ==== Handle D (Next Image)  ==== *
                if event.key == pygame.K_d:
                    if current_image_index < len(images) - 1:
                        current_image_index += 1
                        load_current_image()
                        # Load existing labels if any
                        load_existing_inputs()
                        # Update input boxes
                        init_bones_labels_inputs_scrolling()
                        update_progress_bar()

                #  * ==== Handle A (Previous Image)  ==== *
                if event.key == pygame.K_a:
                    if current_image_index > 0:
                        current_image_index -= 1
                        load_current_image()
                        # Load existing labels if any
                        load_existing_inputs()
                        init_bones_labels_inputs_scrolling()
                        update_progress_bar()

            manager.process_events(event)

        manager.update(time_delta)

        screen.blit(background, (0, 0))

        if current_page == 1:
            manager.draw_ui(screen)
        elif current_page == 2:
            # Draw Image
            if image_surface:
                screen.blit(image_surface, (0, 0))
            else:
                # Display message if image not loaded
                font = pygame.font.SysFont(None, 48)
                text_surface = font.render("Image not available", True, (255, 0, 0))
                screen.blit(text_surface, (SCREEN_WIDTH * 0.4, SCREEN_HEIGHT / 2))

            # Draw input boxes
            manager.draw_ui(screen)

            # Optional: Display image name
            if images:
                image_name = images[current_image_index]
                font = pygame.font.SysFont(None, 36)
                text_surface = font.render(
                    f"Image {current_image_index + 1} of {len(images)}: {image_name}",
                    True,
                    (255, 255, 255),
                )
                screen.blit(text_surface, (20, 20))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
