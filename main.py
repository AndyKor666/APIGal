import tkinter as tk
from tkinter import ttk
import requests
from PIL import Image, ImageTk
from io import BytesIO

API_KEY = "55722683-12dae700a6f246e13e5aba587"

class GalleryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SHUSHA")
        self.root.geometry("600x600")
        self.root.configure(bg="#c0c0c0")
        self.page = 1
        self.images = []

        top_frame = tk.Frame(root, bg="#c0c0c0", bd=2, relief="raised")
        top_frame.pack(fill="x", padx=5, pady=5)

        self.search_var = tk.StringVar(value="city")

        tk.Label(top_frame, text="Search:", bg="#c0c0c0").pack(side="left", padx=5)

        tk.Entry(top_frame, textvariable=self.search_var, width=30, relief="sunken", bd=2)\
            .pack(side="left", padx=5)

        tk.Button(top_frame, text="GO", width=6, relief="raised", command=self.search)\
            .pack(side="left", padx=3)

        tk.Button(top_frame, text="<<", width=5, relief="raised", command=self.prev_page)\
            .pack(side="left", padx=3)

        tk.Button(top_frame, text=">>", width=5, relief="raised", command=self.next_page)\
            .pack(side="left", padx=3)

        self.page_label = tk.Label(top_frame, text=f"Page: {self.page}", bg="#c0c0c0")
        self.page_label.pack(side="right", padx=10)

        frame = tk.Frame(root, bd=2, relief="sunken")
        frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.canvas = tk.Canvas(frame, bg="#808080")
        self.scrollbar = tk.Scrollbar(frame, orient="vertical", command=self.canvas.yview)

        self.scroll_frame = tk.Frame(self.canvas, bg="#808080")

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.load_images()

    def fetch_data(self):
        url = "https://pixabay.com/api/"
        params = {
            "key": API_KEY,
            "q": self.search_var.get(),
            "image_type": "photo",
            "per_page": 8,
            "page": self.page
        }
        return requests.get(url, params=params).json()

    def load_images(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        self.images.clear()
        self.page_label.config(text=f"Page: {self.page}")
        data = self.fetch_data()

        for i, hit in enumerate(data["hits"]):
            try:
                response = requests.get(hit["webformatURL"])
                img = Image.open(BytesIO(response.content))
                img = img.resize((260, 180))

                tk_img = ImageTk.PhotoImage(img)
                self.images.append(tk_img)
                box = tk.Frame(
                    self.scroll_frame,
                    bd=1,
                    relief="solid",
                    bg="#c0c0c0"
                )
                box.grid(row=i // 2, column=i % 2, padx=8, pady=8)
                lbl = tk.Label(box, image=tk_img, bg="#c0c0c0")
                lbl.pack()
            except:
                continue

    def search(self):
        self.page = 1
        self.load_images()

    def next_page(self):
        self.page += 1
        self.load_images()

    def prev_page(self):
        if self.page > 1:
            self.page -= 1
            self.load_images()

if __name__ == "__main__":
    root = tk.Tk()
    app = GalleryApp(root)
    root.mainloop()