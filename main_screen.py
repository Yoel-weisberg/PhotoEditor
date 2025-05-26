import tkinter as tk
from tkinter import filedialog

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

        # configinig the menu as the menu
        self.config(menu=menu_bar)

        # creating the main frame
        photo_display_frame = tk.Frame(self, bg="lightblue")
        photo_display_frame.pack()

        # creating a button
        add_image_button = tk.Button(
            photo_display_frame, text="Load Image", command=self.load_image
        )

        add_image_button.pack()

    def load_image(self):
        file_path = filedialog.askopenfilename(
            title="Select an image to be loaded",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")]
        )

        if file_path:
            print("Selected file:", file_path)


if __name__ == "__main__":
    app = MainScreen()
    app.mainloop()
