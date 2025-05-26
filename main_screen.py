import tkinter as tk
from tkinter import filedialog
import cv2
from PIL import Image, ImageTk
from decoraters import repeat_every

DELAY_FOR_RESIZING = 0.5
MARGIN_PERCENTAGE_IMAGE = 0.95

class MainScreen(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Main Screen")
        self.geometry("800x600")
        self.configure(bg="lightblue")
        menu_bar = tk.Menu(self)

        # creating file menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open File", command=lambda: print("opened a file"))
        file_menu.add_command(label="Save")

        # creating exit button
        menu_bar.add_cascade(label="File", menu=file_menu)

        menu_bar.add_command(label="Exit", command=self.quit)

        # configuig the menu as the menu
        self.config(menu=menu_bar)

        # creating the main frame
        self.photo_display_frame = tk.Frame(self, bg="lightblue")
        self.photo_display_frame.pack(expand=True)

        # creating a button
        self.add_image_button = tk.Button(
            self.photo_display_frame, text="Load Image", command=self.load_image
        )

        self.add_image_button.pack()

        # adding the image label
        self.main_image_label = tk.Label(self.photo_display_frame, bg="lightblue")
        self.main_image_label.pack()

        # creating the image state 
        self.orig_image = None

        # FLAGS 
        self.resise_pending = False
        self.currentDim = tuple()

    def load_image(self):
        file_path = filedialog.askopenfilename(
            title="Select an image to be loaded",
        )

        if file_path:
            print("Selected file:", file_path)
            image = cv2.imread(file_path)
            if image is not None:
                print("Image loaded successfully!")
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                self.orig_image = Image.fromarray(image)
                
                # initial resizing
                self.delayed_resize()
                self.add_image_button.pack_forget()

            else:
                print("Failed to load image.")

    def get_sizes(self, orig_width, orig_height):
        self.update_idletasks()
        
        # getting frame dimonsions
        max_width = self.winfo_width() * MARGIN_PERCENTAGE_IMAGE
        max_height = self.winfo_height() * MARGIN_PERCENTAGE_IMAGE

        # calculating the scale factor
        scale = min(max_width / orig_width, max_height / orig_height)
        new_width = int(orig_width * scale)
        new_height = int(orig_height * scale)

        return new_width, new_height

    # A function to check that the dimonsions match the image
    @repeat_every(DELAY_FOR_RESIZING)
    def delayed_resize(self):
        new_dim = (self.winfo_width(), self.winfo_height())
        if self.orig_image is not None and  new_dim != self.currentDim:
            pil_image = self.orig_image.resize(
                self.get_sizes(self.orig_image.size[0], self.orig_image.size[1])
            )
            tk_image = ImageTk.PhotoImage(pil_image)
            self.main_image_label.configure(image=tk_image)
            self.main_image_label.image = tk_image  # Keep a reference!
            self.currentDim = new_dim


if __name__ == "__main__":
    print("run")
    app = MainScreen()
    app.mainloop()
