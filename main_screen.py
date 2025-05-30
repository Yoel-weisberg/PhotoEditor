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
        file_menu.add_command(label="Open File", command=self.load_image)
        file_menu.add_command(label="Save", command=self.save_image)

        # creating exit button
        menu_bar.add_cascade(label="File", menu=file_menu)

        menu_bar.add_command(label="Exit", command=self.quit)

        # configuig the menu as the menu
        self.config(menu=menu_bar)

        # creating the main frame (image display area)
        self.photo_display_frame = tk.Frame(self, bg="lightblue")
        self.photo_display_frame.pack(side=tk.LEFT, fill="both", expand=True)

        # creating the image canvas (fills the frame)
        self.main_image_canvas = tk.Canvas(self.photo_display_frame, bg="lightblue", highlightthickness=0)
        self.main_image_canvas.pack(expand=True, fill="both")

        # Editing controls frame (vertical, on the right)
        self.controls_frame = tk.Frame(self, bg="lightblue")
        self.controls_frame.pack(side=tk.RIGHT, fill="y")

        # Contrast slider
        self.contrast_var = tk.DoubleVar(value=1.0)
        self.contrast_slider = tk.Scale(self.controls_frame, from_=0.5, to=2.0, resolution=0.01, orient=tk.VERTICAL, label="Contrast", variable=self.contrast_var, command=self.update_image)
        self.contrast_slider.pack(pady=5)

        # Brightness slider
        self.brightness_var = tk.DoubleVar(value=1.0)
        self.brightness_slider = tk.Scale(self.controls_frame, from_=0.5, to=2.0, resolution=0.01, orient=tk.VERTICAL, label="Brightness", variable=self.brightness_var, command=self.update_image)
        self.brightness_slider.pack(pady=5)

        # Saturation slider
        self.saturation_var = tk.DoubleVar(value=1.0)
        self.saturation_slider = tk.Scale(self.controls_frame, from_=0.0, to=2.0, resolution=0.01, orient=tk.VERTICAL, label="Saturation", variable=self.saturation_var, command=self.update_image)
        self.saturation_slider.pack(pady=5)

        # Crop button
        self.crop_button = tk.Button(self.controls_frame, text="Crop", command=self.start_crop_mode)
        self.crop_button.pack(pady=10)

        # Load Image button (put in controls frame for better layout)
        self.add_image_button = tk.Button(self.controls_frame, text="Load Image", command=self.load_image)
        self.add_image_button.pack(pady=10)

        # creating the image state 
        self.orig_image = None
        self.crop_mode = False
        self.crop_rect = None
        self.start_x = None
        self.start_y = None
        self.rect_id = None

        # FLAGS 
        self.resize_pending = False
        self.currentDim = tuple()

        # Bind resize event to update image
        self.photo_display_frame.bind("<Configure>", self.on_frame_resize)
        self.main_image_canvas.bind('<Button-1>', self.on_crop_start)
        self.main_image_canvas.bind('<B1-Motion>', self.on_crop_drag)
        self.main_image_canvas.bind('<ButtonRelease-1>', self.on_crop_end)
        self.main_image_canvas.bind('<Motion>', self.on_mouse_motion)
        self.crop_handle_size = 8
        self.crop_dragging = False
        self.crop_resizing = False
        self.crop_resize_dir = None

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
                self.contrast_var.set(1.0)
                self.brightness_var.set(1.0)
                self.saturation_var.set(1.0)
                
                # initial resizing
                self.delayed_resize()
                self.add_image_button.pack_forget()
                self.update_image()
            else:
                print("Failed to load image.")

    def get_sizes(self, orig_width, orig_height):
        self.photo_display_frame.update_idletasks()
        max_width = self.photo_display_frame.winfo_width() * 0.95
        max_height = self.photo_display_frame.winfo_height() * 0.95
        scale = min(max_width / orig_width, max_height / orig_height)
        new_width = int(orig_width * scale)
        new_height = int(orig_height * scale)
        return new_width, new_height

    # A function to check that the dimonsions match the image
    @repeat_every(DELAY_FOR_RESIZING)
    def delayed_resize(self):
        new_dim = (self.winfo_width(), self.winfo_height())
        if self.orig_image is not None and  new_dim != self.currentDim:
            self.update_image()
            self.currentDim = new_dim

    def save_image(self):
        if self.orig_image is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg;*.jpeg")])
            if file_path:
                edited_image = self.get_edited_image()
                edited_image.save(file_path)
                print(f"Image saved to {file_path}")

    def get_edited_image(self):
        # Apply contrast, brightness, and saturation to the original image
        if self.orig_image is None:
            return None
        image = self.orig_image.copy()
        # Apply brightness and contrast
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(self.contrast_var.get())
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(self.brightness_var.get())
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(self.saturation_var.get())
        return image

    def update_image(self, event=None):
        if self.orig_image is not None:
            pil_image = self.get_edited_image().resize(self.get_sizes(self.orig_image.size[0], self.orig_image.size[1]))
            self.tk_image = ImageTk.PhotoImage(pil_image)
            self.main_image_canvas.delete("all")
            self.main_image_canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
            # Draw crop rectangle if in crop mode
            if self.crop_mode and self.crop_rect:
                self.draw_crop_rectangle()

    def start_crop_mode(self):
        self.crop_mode = True
        self.crop_rect = None
        self.start_x = None
        self.start_y = None
        self.rect_id = None
        self.crop_dragging = False
        self.crop_resizing = False
        self.crop_resize_dir = None
        print("Crop mode started. Click and drag on the image to select a region.")

    def on_crop_start(self, event):
        if not self.crop_mode or self.orig_image is None:
            return
        x, y = event.x, event.y
        if self.crop_rect and self.is_on_handle(x, y):
            self.crop_resizing = True
            self.crop_resize_dir = self.get_handle_dir(x, y)
        elif self.crop_rect and self.is_inside_rect(x, y):
            self.crop_dragging = True
            self.drag_offset = (x - self.crop_rect[0], y - self.crop_rect[1])
        else:
            self.start_x = x
            self.start_y = y
            self.crop_rect = (x, y, x, y)
            self.rect_id = None
        self.update_image()

    def on_crop_drag(self, event):
        if not self.crop_mode or self.orig_image is None:
            return
        x, y = event.x, event.y
        if self.crop_resizing and self.crop_rect:
            self.crop_rect = self.resize_rect(self.crop_rect, self.crop_resize_dir, x, y)
        elif self.crop_dragging and self.crop_rect:
            # Move the rectangle by dragging
            w = self.crop_rect[2] - self.crop_rect[0]
            h = self.crop_rect[3] - self.crop_rect[1]
            new_x0 = x - self.drag_offset[0]
            new_y0 = y - self.drag_offset[1]
            self.crop_rect = (new_x0, new_y0, new_x0 + w, new_y0 + h)
        elif self.start_x is not None and self.start_y is not None:
            self.crop_rect = (self.start_x, self.start_y, x, y)
        self.update_image()

    def on_crop_end(self, event):
        if not self.crop_mode or self.orig_image is None:
            return
        self.crop_dragging = False
        self.crop_resizing = False
        self.crop_resize_dir = None
        if self.crop_rect:
            # Optionally, snap rect to image bounds
            self.crop_rect = self.clamp_rect_to_image(self.crop_rect)
        self.update_image()

    def on_mouse_motion(self, event):
        if not self.crop_mode or self.orig_image is None or not self.crop_rect:
            self.main_image_canvas.config(cursor="arrow")
            return
        x, y = event.x, event.y
        if self.is_on_handle(x, y):
            self.main_image_canvas.config(cursor="tcross")
        elif self.is_inside_rect(x, y):
            self.main_image_canvas.config(cursor="fleur")
        else:
            self.main_image_canvas.config(cursor="arrow")

    def draw_crop_rectangle(self):
        if not self.crop_rect:
            return
        x0, y0, x1, y1 = self.crop_rect
        self.main_image_canvas.create_rectangle(x0, y0, x1, y1, outline="red", width=2)
        # Draw handles
        for hx, hy in self.get_handle_coords(x0, y0, x1, y1):
            self.main_image_canvas.create_rectangle(hx - self.crop_handle_size, hy - self.crop_handle_size, hx + self.crop_handle_size, hy + self.crop_handle_size, outline="black", fill="white")

    def is_inside_rect(self, x, y):
        if not self.crop_rect:
            return False
        x0, y0, x1, y1 = self.crop_rect
        return min(x0, x1) < x < max(x0, x1) and min(y0, y1) < y < max(y0, y1)

    def get_handle_coords(self, x0, y0, x1, y1):
        # 8 handles: corners and midpoints
        return [
            (x0, y0), (x1, y0), (x0, y1), (x1, y1),
            ((x0 + x1) // 2, y0), ((x0 + x1) // 2, y1),
            (x0, (y0 + y1) // 2), (x1, (y0 + y1) // 2)
        ]

    def is_on_handle(self, x, y):
        if not self.crop_rect:
            return False
        for hx, hy in self.get_handle_coords(*self.crop_rect):
            if abs(x - hx) <= self.crop_handle_size and abs(y - hy) <= self.crop_handle_size:
                return True
        return False

    def get_handle_dir(self, x, y):
        # Returns which handle is being dragged (corner or side)
        coords = self.get_handle_coords(*self.crop_rect)
        for idx, (hx, hy) in enumerate(coords):
            if abs(x - hx) <= self.crop_handle_size and abs(y - hy) <= self.crop_handle_size:
                return idx
        return None

    def resize_rect(self, rect, handle_dir, x, y):
        x0, y0, x1, y1 = rect
        if handle_dir == 0:  # top-left
            return (x, y, x1, y1)
        elif handle_dir == 1:  # top-right
            return (x0, y, x, y1)
        elif handle_dir == 2:  # bottom-left
            return (x, y0, x1, y)
        elif handle_dir == 3:  # bottom-right
            return (x0, y0, x, y)
        elif handle_dir == 4:  # top-mid
            return (x0, y, x1, y1)
        elif handle_dir == 5:  # bottom-mid
            return (x0, y0, x1, y)
        elif handle_dir == 6:  # left-mid
            return (x, y0, x1, y1)
        elif handle_dir == 7:  # right-mid
            return (x0, y0, x, y1)
        return rect

    def clamp_rect_to_image(self, rect):
        x0, y0, x1, y1 = rect
        width = self.main_image_canvas.winfo_width()
        height = self.main_image_canvas.winfo_height()
        x0 = max(0, min(width, x0))
        x1 = max(0, min(width, x1))
        y0 = max(0, min(height, y0))
        y1 = max(0, min(height, y1))
        return (x0, y0, x1, y1)

    def confirm_crop(self):
        if not self.crop_rect or self.orig_image is None:
            return
        # Convert canvas coordinates to image coordinates
        pil_image = self.get_edited_image().resize(self.get_sizes(self.orig_image.size[0], self.orig_image.size[1]))
        canvas_width = self.main_image_canvas.winfo_width()
        canvas_height = self.main_image_canvas.winfo_height()
        img_width, img_height = pil_image.size
        scale_x = img_width / canvas_width
        scale_y = img_height / canvas_height
        x0, y0, x1, y1 = [int(v) for v in self.crop_rect]
        crop_x0 = int(min(x0, x1) * scale_x)
        crop_y0 = int(min(y0, y1) * scale_y)
        crop_x1 = int(max(x0, x1) * scale_x)
        crop_y1 = int(max(y0, y1) * scale_y)
        cropped = self.orig_image.crop((crop_x0, crop_y0, crop_x1, crop_y1))
        self.orig_image = cropped
        self.crop_mode = False
        self.crop_rect = None
        self.update_image()
        print(f"Cropped to: ({crop_x0}, {crop_y0}, {crop_x1}, {crop_y1})")

    def on_frame_resize(self, event):
        # Update the displayed image and crop rectangle when the frame is resized
        if self.orig_image is not None:
            self.update_image()
        # Optionally, you could also clamp the crop rectangle to the new canvas size
        if self.crop_rect:
            self.crop_rect = self.clamp_rect_to_image(self.crop_rect)
            self.update_image()

if __name__ == "__main__":
    print("run")
    app = MainScreen()
    app.mainloop()
