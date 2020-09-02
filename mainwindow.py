import tkinter
import tkinter.filedialog
import PIL.Image
import PIL.ImageTk
import cv2
import os
import random
# TODO move non-interface commands to separate module. ex: resize image, levels, etc


class MainWindow:

    menubar = None
    file_menu = None
    view_menu = None
    image_menu = None
    window_menu = None
    help_menu = None

    menubar_sel = None
    submenu_sel = None

    image_frame = None
    image_label = None
    cv2_image = None
    pil_image = None
    tk_image = None

    screen_width = 0
    screen_height = 0
    win_width = 640
    win_height = 480
    win_x_offset = 2500
    win_y_offset = 100
    image_width = 0
    image_height = 0

    SBW = 21  # scrollbar width

    image_scrollbar = None

    def __init__(self, mainWindow):
        self.screen_width = mainWindow.winfo_screenwidth()
        self.screen_height = mainWindow.winfo_screenheight()
        # for lock aspect ratio check button
        self.aspect_locked = tkinter.IntVar()
        self.status_text = tkinter.StringVar()
        self.status_text.set("  Welcome to Viewy!")
        self.info_text = tkinter.StringVar()

        self.image_index = None
        self.filenames_string = None
        self.filenames_list = []
        self.total_images = None

        self.load_dir_bool = False
        self.random_on = tkinter.IntVar()
        self.auto_zoom_var = tkinter.IntVar()

        mainWindow.title("Viewy")
        mainWindow.geometry("{}x{}+{}+{}".format(self.win_width,
                                                 self.win_height,
                                                 self.win_x_offset,
                                                 self.win_y_offset))
        mainWindow.configure()
        mainWindow.bind('<Key>', self.load_image)

        self.win_location()  # TODO del ???

        # Create Menu, Image backing frame, and Canvas
        self.menubar = tkinter.Menu(mainWindow)
        self.menubar.bind('<<MenuSelect>>', self.menubar_selected)

        self.image_frame = tkinter.Frame(
            mainWindow)
        self.image_frame.pack(fill=tkinter.BOTH, expand=True)
        self.canvas = tkinter.Canvas(
            self.image_frame, bg='black')

        # Create Scrollbars
        self.vert_scrollbar = tkinter.Scrollbar(
            self.image_frame)
        self.vert_scrollbar.config(command=self.canvas.yview)
        self.vert_scrollbar.pack(side=tkinter.RIGHT,
                                 fill='y')

        self.horz_scrollbar = tkinter.Scrollbar(
            self.image_frame, orient=tkinter.HORIZONTAL)
        self.horz_scrollbar.pack(side=tkinter.BOTTOM, fill='x')
        self.horz_scrollbar.config(command=self.canvas.xview)

        self.canvas.pack(fill=tkinter.BOTH, expand=True)
        self.canvas.config(
            yscrollcommand=self.vert_scrollbar.set,
            xscrollcommand=self.horz_scrollbar.set,
            scrollregion=(0, 0, self.image_width, self.image_height))

        self.file_menu = tkinter.Menu(self.menubar, tearoff=0)
        self.file_menu.bind('<<MenuSelect>>', self.status_update)
        self.view_menu = tkinter.Menu(self.menubar, tearoff=0)
        self.view_menu.bind('<<MenuSelect>>', self.status_update)
        self.image_menu = tkinter.Menu(self.menubar, tearoff=0)
        self.image_menu.bind('<<MenuSelect>>', self.status_update)
        self.window_menu = tkinter.Menu(self.menubar, tearoff=0)
        self.window_menu.bind('<<MenuSelect>>', self.status_update)
        self.help_menu = tkinter.Menu(self.menubar, tearoff=0)
        self.help_menu.bind('<<MenuSelect>>', self.status_update)

        self.menu_dict = {
            0: {
                0: "Load 1 or more images",
                1: "Load a directory of images",
                2: "Start a new session and customize timing options",
                3: "Save your current session",
                4: "Load a previously saved session",
                5: None,
                6: "Exit the program"
            },
            1: {
                0: "Zoom into the image",
                1: "Zoom out from the image",
                2: "Zoom image to fit the width of the window",
                3: "Zoom image to fit the height of the window",
                4: "Automatically zoom every image to fit the window",
                5: "Reset the image to its original aspect",
                6: None,
                7: "Flip the image vertically",
                8: "Flip the image horizontally",
                9: "Rotate the image counter-clockwise",
                10: "Rotate the image clockwise",
                11: "Rotate the image by a custom amount",
                12: None,
                13: "Randomize the order of the images"
            },
            2: {
                0: "Undo the last action",
                1: "Redo the undone action",
                2: "Go to the next image",
                3: "Go back to the previous image",
                4: "Search this image on Google",
                5: None,
                6: "Resize the image by custom amount",
                7: "Add a vignette border to the image",
                8: "Brighten the image",
                9: "Apply Levels - Darken to the image",
                10: "Apply a Median filter to the image",
                11: "Upscale the image",
                12: None,
                13: "Show information about the image"
            },
            3: {
                0: "Minimize the program window",
                1: "Restore the program window",
                2: "Fit the window to the screen's width",
                3: "Fit the window to the screen's height",
                4: "Maximize the window",
                5: None,
                6: "Lock the current aspect ratio of the window",
                7: None,
                8: "Fit the window to the width of the image",
                9: "Fit the window to the height of the image",
                10: "Fit the window to the size of the image",
                11: None,
                12: "Show the tools sidebar",
                13: "Hide the tools sidebar"
            },
            4: {
                0: "Access help documentation",
                1: None,
                2: "About this program"
            }
        }

        self.file_types = [
            ('Image Files', '*.jpeg;*.jpg;*.jpe;*.jp2;*.jfif;*.png;*.bmp;*.dib;*.webp;*.tiff;*.tif'),
            ('All Files', '*.*')
        ]
        self.file_types_list = self.file_types[0][1].split(';')

        # add menubar labels
        self.menubar.add_cascade(label="File", menu=self.file_menu)
        self.menubar.add_cascade(
            label="View", menu=self.view_menu, state='disabled')
        self.menubar.add_cascade(
            label="Image", menu=self.image_menu, state='disabled')
        self.menubar.add_cascade(
            label="Window", menu=self.window_menu)
        self.menubar.add_cascade(label="Help", menu=self.help_menu)

        self.file_menu.add_command(
            label="Load Image(s)", command=self.load_image)
        # self.file_menu.bind("<<MenuSelect>>", self.status_update)
        self.file_menu.add_command(
            label="Load Directory", command=self.load_dir)
        self.file_menu.add_command(
            label="New Session", command=self.new_session)
        self.file_menu.add_command(
            label="Save Session", command=self.save_session)
        self.file_menu.entryconfig("Save Session", state="disabled")
        self.file_menu.add_command(
            label="Load Session", command=self.load_session)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=mainWindow.quit)

        self.view_menu.add_command(label="Zoom In", command=self.zoom_in)
        self.view_menu.add_command(label="Zoom Out", command=self.zoom_out)
        self.view_menu.add_command(
            label="Zoom to Window Width", command=self.zoom_to_width)
        self.view_menu.add_command(
            label="Zoom to Window Height", command=self.zoom_to_height)
        self.view_menu.add_checkbutton(
            label="Auto Zoom to Fit Window", variable=self.auto_zoom_var, command=self.auto_zoom)
        self.view_menu.add_command(label="Reset Zoom", command=self.zoom_reset)
        self.view_menu.add_separator()
        self.view_menu.add_command(
            label="Flip Vertical", command=self.flip_vert)
        self.view_menu.add_command(
            label="Flip Horizontal", command=self.flip_horz)
        self.view_menu.add_command(
            label="Rotate Left", command=self.rotate_left)
        self.view_menu.add_command(
            label="Rotate Right", command=self.rotate_right)
        self.view_menu.add_command(
            label="Rotate Amount", command=self.rotate_amount)
        self.view_menu.add_separator()
        self.view_menu.add_command(label="Image Info", command=self.image_info)

        self.image_menu.add_command(label="Undo", command=self.undo)
        self.image_menu.add_command(label="Redo", command=self.redo)
        self.image_menu.add_command(
            label="Next Image", command=self.skip_image)
        self.image_menu.add_command(
            label="Previous Image", command=self.prev_image)
        self.image_menu.add_command(
            label="Search Image on Google", command=self.search_google)
        self.image_menu.add_separator()
        self.image_menu.add_command(
            label="Resize Image", command=self.resize_image)
        self.image_menu.add_command(label="Vignette Border")
        self.image_menu.add_command(label="Brighten", command=self.brighten)
        self.image_menu.add_command(
            label="Levels - Darken", command=self.levels_darken)
        self.image_menu.add_command(label="Median", command=self.median)
        self.image_menu.add_command(
            label="Upscale Image", command=self.upscale)
        self.image_menu.add_separator()
        self.image_menu.add_checkbutton(
            label="Random Order of Images", variable=self.random_on, command=self.randomizer)

        self.window_menu.add_command(label="Minimize", command=self.min_window)
        self.window_menu.add_command(
            label="Restore", command=self.restore_window)
        self.window_menu.add_command(
            label="Fit to Screen Width", command=self.fit_screen_width)
        self.window_menu.add_command(
            label="Fit to Screen Height", command=self.fit_screen_height)
        self.window_menu.add_command(label="Maximize", command=self.max_window)
        self.window_menu.add_separator()
        self.window_menu.add_checkbutton(
            label="Lock Aspect Ratio", variable=self.aspect_locked, command=self.lock_aspect)
        self.window_menu.add_separator()
        self.window_menu.add_command(
            label="Fit to Width of Image", command=self.win_fit_width, state='disabled')
        self.window_menu.add_command(
            label="Fit to Height of Image", command=self.win_fit_height, state='disabled')
        self.window_menu.add_command(
            label="Fit to Size of Image", command=self.win_fit_size, state='disabled')
        self.window_menu.add_separator()
        self.window_menu.add_command(
            label="Show Sidebar", state='disabled', command=self.show_sidebar)
        self.window_menu.add_command(
            label="Hide Sidebar", state='disabled', command=self.hide_sidebar)

        self.help_menu.add_command(label="Help", command=self.help)
        self.help_menu.add_separator()
        self.help_menu.add_command(label="About", command=self.about)

        mainWindow.config(menu=self.menubar)

        # Status bar at bottom of screen
        # Using anchor= instead of justify= because justify on ly works for multiline
        self.status_bar = tkinter.Label(
            relief=tkinter.SUNKEN, anchor='w', textvariable=self.status_text)
        self.status_bar.pack(side='left', fill='x', expand=True)
        # Info bar which sits beside status bar
        self.info_bar = tkinter.Label(
            relief='sunken',
            anchor='e',
            textvariable=self.info_text,
            width=20)
        self.info_bar.pack(side='right', fill='x')

    def menubar_selected(self, event=None):
        # update the menubar item attribute for use in status bar function
        self.menubar_sel = mainWindow.call(event.widget, 'index', 'active')

    def status_update(self, event=None):
        self.submenu_sel = mainWindow.call(event.widget, 'index', 'active')
        if isinstance(self.menubar_sel, int) and isinstance(self.submenu_sel, int):

            # TODO may not need this condition anymore ??
            if self.menu_dict[self.menubar_sel-1][self.submenu_sel] is not None:
                # print(self.menu_dict[self.menubar_sel-1][self.submenu_sel])
                self.status_text.set("  {}".format(
                    self.menu_dict[self.menubar_sel-1][self.submenu_sel]))

        else:
            self.status_text.set("")

    # TODO: requires refactoring !!!!!!!
    def load_image(self, event=None, state=None):

        # poll window location before refreshing
        self.win_location()

        # load one or more images
        if event is None and (self.load_dir_bool is False) and state is None:
            # disable randomization at beginning
            self.random_on.set(0)
            self.total_images = 0
            self.filenames_list.clear()

            try:
                # returns tuple of image paths
                self.filenames_string = tkinter.filedialog.askopenfilenames(title="Select one or more images",
                                                                            filetypes=self.file_types)
                # populate tuple items into list items
                for item in self.filenames_string:
                    self.filenames_list.append(item)

                # this index is always 0 here, it will get ++ or -- as images are iterated later
                self.image_index = 0

                self.total_images = len(self.filenames_list)
                assert self.total_images >= 1

            except:
                # raise
                self.status_text.set("  No image loaded")

            else:
                if self.total_images == 1:
                    self.status_text.set("  Image was loaded successfully")
                elif self.total_images > 1:
                    self.info_text.set("{} of {} images  ".format(
                        self.image_index, self.total_images))
                    self.status_text.set("  {} images were queued successfully".format(
                        len(self.filenames_string)))
                # enable menu items once an image is loaded
                # NOTE: add_separator does not have a state!
                self.file_menu.entryconfig(3, state='normal')
                self.menubar.entryconfig("View", state='normal')
                self.menubar.entryconfig("Image", state='normal')
                self.lock_aspect()
                self.window_menu.entryconfig(8, state='normal')
                self.window_menu.entryconfig(9, state='normal')
                self.window_menu.entryconfig(10, state='normal')
                self.window_menu.entryconfig(12, state='normal')
                self.window_menu.entryconfig(13, state='normal')

        # load directory
        elif event is None and (self.load_dir_bool is True) and state is None:
            # reset load dir boolean
            self.load_dir_bool = False
            # disable randomization at beginning
            self.random_on.set(0)
            # reset filenames_list
            self.filenames_list.clear()

            try:
                # returns tuple of image paths
                self.dir_path = tkinter.filedialog.askdirectory(
                    title="Select a directory of images to load")
                # this index is always 0 here, it will get ++ or -- as images are iterated later
                self.image_index = 0

                for file_name in os.listdir(self.dir_path):
                    full_path = os.path.join(self.dir_path, file_name)

                    # for every extension type in the reference list
                    for string in self.file_types_list:
                        # if the extension exists in the element
                        if (file_name[-4:] in string):
                            # then add it to the list
                            self.filenames_list.append(full_path)
                    # NOTE: list comprehension version; for loop is more readable in this case
                    # [self.filenames_list.append(full_path) for string in self.file_types_list if (
                    #     file_name[-4:] in string)]

                self.total_images = len(self.filenames_list)
                assert self.total_images >= 1

            except:
                # raise
                self.status_text.set("  No directory loaded")

            else:
                if self.total_images == 1:
                    self.status_text.set("  Image was loaded successfully")
                else:
                    self.info_text.set("{} of {} images  ".format(
                        self.image_index, self.total_images))
                    self.status_text.set("  {} images were queued successfully".format(
                        len(self.filenames_list)))
                # TODO refactor this code to avoid repetition
                # enable menu items once an image is loaded
                # NOTE: add_separator does not have a state!
                self.file_menu.entryconfig(3, state='normal')
                self.menubar.entryconfig("View", state='normal')
                self.menubar.entryconfig("Image", state='normal')
                self.lock_aspect()
                self.window_menu.entryconfig(8, state='normal')
                self.window_menu.entryconfig(9, state='normal')
                self.window_menu.entryconfig(10, state='normal')
                self.window_menu.entryconfig(12, state='normal')
                self.window_menu.entryconfig(13, state='normal')

        # AUTO ZOOM
        elif event is None and state == 'zoom on':
            print("\t", self.auto_zoom_var.get())
            print("\tAuto zoom is on")
            # TODO add code to resize image for zoom
            print("win size:", mainWindow.winfo_width(),
                  mainWindow.winfo_height())
            print("image size:", self.image_width, self.image_height)

            w1 = mainWindow.winfo_width()
            h1 = mainWindow.winfo_height()
            w2 = self.image_width
            h2 = self.image_height

            min_of_window = min(w1, h1)
            max_of_image = max(w2, h2)

            win_ratio = w1 / h1
            image_ratio = w2 / h2

            print("Min of window:", min_of_window)
            print("Max of image:", max_of_image)
            print("Win ratio:", win_ratio)
            print("Image ratio:", image_ratio)

            # if ratios = same, resize both w and h to same size as window w and h
            if win_ratio == 1 and image_ratio == 1:
                self.image_resize(w1, h1)

            # if both are horizontal
            elif win_ratio > 1 and image_ratio > 1:
                # same size
                if win_ratio == image_ratio:
                    self.image_resize(w1, h1)
                #
                elif win_ratio > image_ratio:
                    pass
                else:
                    pass

            # if both are vertical
            elif win_ratio < 1 and image_ratio < 1:
                # same size
                if win_ratio == image_ratio:
                    self.image_resize(w1, h1)
                elif win_ratio > image_ratio:
                    pass
                else:
                    pass

            # if win is horz and image is vertical
            elif win_ratio < 1 and image_ratio > 1:
                #
                if win_ratio > image_ratio:
                    pass
                else:
                    pass

            # if win is vertical and image is horizontal
            elif win_ratio > 1 and image_ratio < 1:
                #
                if win_ratio > image_ratio:
                    pass
                else:
                    pass

            # self.resize_image()

        elif event is None and state == 'zoom off':
            print("\t", self.auto_zoom_var.get())
            print("\tAuto zoom is off")

        # if a key has been pressed, cycle to next/prev image
        if event is not None:
            if event.keysym == 'Right' and self.image_index < len(self.filenames_list) - 1:
                self.image_index += 1
            elif event.keysym == 'Left' and self.image_index > 0:
                self.image_index -= 1

        # load the first image into CV2 array
        self.cv2_image = cv2.imread(self.filenames_list[self.image_index])
        # convert to PIL colour order
        self.cv2_image = cv2.cvtColor(
            self.cv2_image, cv2.COLOR_BGR2RGB)
        # convert array to PIL format
        self.pil_image = PIL.Image.fromarray(self.cv2_image)
        # convert to tkinter format
        self.tk_image = PIL.ImageTk.PhotoImage(self.pil_image)
        self.image_dimensions(self.tk_image)

        self.refresh_image()

        # poll window location after window was refreshed
        self.win_location()

        if self.total_images >= 1:
            self.info_text.set("Image {} of {}  ".format(
                self.image_index+1, self.total_images))

    def load_dir(self):
        # redirects to load_image() with directory functionality turned on
        self.load_dir_bool = True
        self.load_image()

    def new_session(self):
        # this will require a pop-up window with options
        # such as: automatic zoom to window size
        pass

    def save_session(self):
        # use pickle ??
        pass

    def load_session(self):
        pass

    def zoom_in(self):
        # need to ensure that there is a copy of the original image
        # so that zoom can be reverted for the next few methods
        pass

    def zoom_out(self):
        pass

    def zoom_to_width(self):
        pass

    def zoom_to_height(self):
        pass

    def auto_zoom(self):
        if self.auto_zoom_var.get() == 1:
            self.load_image(event=None, state='zoom on')
        else:
            self.load_image(event=None, state='zoom off')

    def zoom_reset(self):
        pass

    def flip_vert(self):
        pass

    def flip_horz(self):
        pass

    def rotate_left(self):
        pass

    def rotate_right(self):
        pass

    def rotate_amount(self):
        pass

    def image_info(self):
        # TODO add a popup window with info about image...size, name, etc
        pass

    def undo(self):
        pass

    def redo(self):
        pass

    def skip_image(self):
        pass

    def prev_image(self):
        pass

    def search_google(self):
        pass

    def resize_image(self, x, y):
        # use earlier pil_image to resize then reconvert and display
        self.tk_image = self.pil_image.resize((x, y), PIL.Image.ANTIALIAS)
        # convert to PhotoImage format again
        self.tk_image = PIL.ImageTk.PhotoImage(self.tk_image)
        # destroy the image before refreshing
        self.canvas.delete("image")
        self.refresh_image()

    def brighten(self):
        pass

    def levels_darken(self):
        pass

    def median(self):
        pass

    def upscale(self):
        pass

    # disable randomizer until image is loaded
    def randomizer(self):
        if self.random_on.get() == 1:
            # if random is ON then make a copy of the original order
            # so that it can be reverted when turned off
            self.filenames_list_backup = self.filenames_list.copy()
            random.shuffle(self.filenames_list)
        else:
            # restore original order
            self.filenames_list = self.filenames_list_backup.copy()

    @staticmethod
    def min_window():
        mainWindow.wm_state('icon')

    @staticmethod
    def restore_window():
        mainWindow.wm_state('normal')

    def fit_screen_width(self):
        self.win_location()  # poll location coords
        self.win_x_offset = 1922
        # -8 pixels to fit perfectly on screen
        self.win_width = self.screen_width-8
        mainWindow.geometry("{}x{}+{}+{}".format(self.win_width,
                                                 mainWindow.winfo_height(), self.win_x_offset, self.win_y_offset))

    def fit_screen_height(self):
        self.win_location()
        self.win_y_offset = 0
        # -51 pixels to fit bottom perfectly on screen
        self.win_height = self.screen_height-51
        print("Win height:", self.win_height)
        print("Screen height:", self.screen_height)
        mainWindow.geometry("{}x{}+{}+{}".format(mainWindow.winfo_width(),
                                                 self.win_height, self.win_x_offset, self.win_y_offset))

    @staticmethod
    def max_window():
        mainWindow.wm_state('zoomed')

    def lock_aspect(self):
        # if there's no image loaded
        if not [item for item in self.canvas.find_all()]:
            if self.aspect_locked.get() == 1:
                mainWindow.resizable(False, False)
                self.window_menu.entryconfig(1, state='disabled')
                self.window_menu.entryconfig(2, state='disabled')
                self.window_menu.entryconfig(3, state='disabled')
                self.window_menu.entryconfig(4, state='disabled')
                self.window_menu.entryconfig(8, state='disabled')
                self.window_menu.entryconfig(9, state='disabled')
                self.window_menu.entryconfig(10, state='disabled')
            else:
                mainWindow.resizable(True, True)
                self.window_menu.entryconfig(1, state='normal')
                self.window_menu.entryconfig(2, state='normal')
                self.window_menu.entryconfig(3, state='normal')
                self.window_menu.entryconfig(4, state='normal')
                self.window_menu.entryconfig(8, state='disabled')
                self.window_menu.entryconfig(9, state='disabled')
                self.window_menu.entryconfig(10, state='disabled')
        else:
            if self.aspect_locked.get() == 1:
                mainWindow.resizable(False, False)
                self.window_menu.entryconfig(1, state='disabled')
                self.window_menu.entryconfig(2, state='disabled')
                self.window_menu.entryconfig(3, state='disabled')
                self.window_menu.entryconfig(4, state='disabled')
                self.window_menu.entryconfig(8, state='disabled')
                self.window_menu.entryconfig(9, state='disabled')
                self.window_menu.entryconfig(10, state='disabled')
            else:
                mainWindow.resizable(True, True)
                self.window_menu.entryconfig(1, state='normal')
                self.window_menu.entryconfig(2, state='normal')
                self.window_menu.entryconfig(3, state='normal')
                self.window_menu.entryconfig(4, state='normal')
                self.window_menu.entryconfig(8, state='normal')
                self.window_menu.entryconfig(9, state='normal')
                self.window_menu.entryconfig(10, state='normal')

    def win_fit_width(self):
        self.win_location()
        if (self.image_width < self.screen_width):
            mainWindow.geometry(
                "{}x{}+{}+{}".format(self.image_width + self.SBW, mainWindow.winfo_height(), self.win_x_offset, self.win_y_offset))
        else:
            mainWindow.geometry(
                "{}x{}+{}+{}".format(self.screen_width, mainWindow.winfo_height(), self.win_x_offset, self.win_y_offset))

    def win_fit_height(self):
        self.win_location()
        if self.image_height < self.screen_height:
            mainWindow.geometry(
                "{}x{}+{}+{}".format(mainWindow.winfo_width(), self.image_height + self.SBW, self.win_x_offset, self.win_y_offset))
        else:
            mainWindow.geometry(
                "{}x{}+{}+{}".format(mainWindow.winfo_width(), self.screen_height, self.win_x_offset, self.win_y_offset))

    def win_fit_size(self):
        self.win_location()

        # restore window before applying changes
        if mainWindow.wm_state() == 'zoomed':
            mainWindow.state('normal')

        if (self.image_width < self.screen_width) and (self.image_height < self.screen_height):
            mainWindow.geometry(
                "{}x{}+{}+{}".format(self.image_width + self.SBW, self.image_height + self.SBW,  self.win_x_offset, self.win_y_offset))
        elif (self.image_width < self.screen_width) and (self.image_height >= self.screen_height):
            mainWindow.geometry(
                "{}x{}+{}+{}".format(self.image_width + self.SBW, self.screen_height,  self.win_x_offset, self.win_y_offset))
        elif (self.image_height < self.screen_height) and (self.image_width >= self.screen_width):
            mainWindow.geometry(
                "{}x{}+{}+{}".format(self.screen_width, self.image_height + self.SBW,  self.win_x_offset, self.win_y_offset))
        else:
            mainWindow.state('zoomed')  # maximize window

    def show_sidebar(self):
        pass

    def hide_sidebar(self):
        pass

    def refresh_image(self):
        # delete any previous image before refreshing
        self.canvas.delete("image")

        # load image into canvas
        self.canvas.create_image(
            0, 0, anchor=tkinter.NW, image=self.tk_image, tag="image")
        self.image_dimensions(self.tk_image)
        self.canvas.config(
            yscrollcommand=self.vert_scrollbar.set,
            xscrollcommand=self.horz_scrollbar.set,
            scrollregion=(0, 0, self.image_width, self.image_height))

        # store a reference to the image so it won't be deleted
        # by the garbage collector
        self.tk_image.image = self.tk_image
        # print(mainWindow.wm_state()) # TODO del

    def image_dimensions(self, image):
        self.image_width = image.width()
        self.image_height = image.height()

    def help(self):
        pass

    def about(self):
        pass

    def win_location(self):
        self.screen_width, self.screen_height = mainWindow.winfo_screenwidth(
        ), mainWindow.winfo_screenheight()
        self.win_x_offset, self.win_y_offset = mainWindow.winfo_rootx() - \
            8, mainWindow.winfo_rooty()-51


if __name__ == "__main__":
    # initial declarations
    mainWindow = tkinter.Tk()
    # create instance of MainWindow class, call it 'app'
    app = MainWindow(mainWindow)
    # load program window
    mainWindow.mainloop()
