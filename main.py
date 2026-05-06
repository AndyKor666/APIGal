import tkinter as tk
from tkinter import messagebox
import requests
from PIL import Image, ImageTk
from io import BytesIO

API_KEY = "aE368WNtnwaKHkj5zaRgFJYgOODCby7VwyxdEova"

ROVERS = {
    "curiosity": ["FHAZ", "RHAZ", "MAST", "CHEMCAM"],
    "opportunity": ["FHAZ", "RHAZ", "NAVCAM"],
    "spirit": ["FHAZ", "RHAZ", "NAVCAM"]
}

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("NASA")
        self.root.geometry("500x400")
        self.root.configure(bg="#c0c0c0")

        self.current_frame = None
        self.images = []
        self.index = 0

        self.show_main()

    def clear(self):
        if self.current_frame:
            self.current_frame.destroy()

    # ================= MAIN =================
    def show_main(self):
        self.clear()

        frame = tk.Frame(self.root, bg="#c0c0c0")
        frame.pack(expand=True)
        self.current_frame = frame

        tk.Label(frame, text="SELECT ROVER",
                 bg="#c0c0c0", font=("Arial", 16, "bold")).pack(pady=20)

        for rover in ROVERS:
            tk.Button(frame, text=rover.upper(), width=20,
                      command=lambda r=rover: self.show_cameras(r)
                      ).pack(pady=5)

    # ================= CAMERAS =================
    def show_cameras(self, rover):
        self.clear()

        frame = tk.Frame(self.root, bg="#c0c0c0")
        frame.pack(expand=True)
        self.current_frame = frame

        tk.Label(frame, text=f"{rover.upper()} CAMERAS",
                 bg="#c0c0c0", font=("Arial", 14, "bold")).pack(pady=20)

        for cam in ROVERS[rover]:
            tk.Button(frame, text=cam, width=20,
                      command=lambda c=cam: self.show_gallery(rover, c)
                      ).pack(pady=5)

        tk.Button(frame, text="<< BACK",
                  command=self.show_main).pack(pady=20)

    # ================= GALLERY =================
    def show_gallery(self, rover, camera):
        self.clear()

        frame = tk.Frame(self.root, bg="#c0c0c0")
        frame.pack(fill="both", expand=True)
        self.current_frame = frame

        top = tk.Frame(frame, bg="#c0c0c0")
        top.pack(pady=10)

        tk.Label(top, text="FROM:", bg="#c0c0c0").pack(side="left")
        self.year_from = tk.Entry(top, width=6)
        self.year_from.insert(0, "2019")
        self.year_from.pack(side="left", padx=5)

        tk.Label(top, text="TO:", bg="#c0c0c0").pack(side="left")
        self.year_to = tk.Entry(top, width=6)
        self.year_to.insert(0, "2020")
        self.year_to.pack(side="left", padx=5)

        tk.Button(top, text="SEARCH",
                  command=lambda: self.load_images(rover, camera)
                  ).pack(side="left", padx=10)

        tk.Button(top, text="<< BACK",
                  command=lambda: self.show_cameras(rover)
                  ).pack(side="left")

        self.img_label = tk.Label(frame,
                                 bg="#808080",
                                 width=800,
                                 height=500,
                                 relief="sunken",
                                 bd=2)
        self.img_label.pack(pady=10)

        nav = tk.Frame(frame, bg="#c0c0c0")
        nav.pack()

        tk.Button(nav, text="<", width=5, command=self.prev_img).pack(side="left", padx=5)
        tk.Button(nav, text=">", width=5, command=self.next_img).pack(side="left", padx=5)

    # ================= LOAD =================
    def load_images(self, rover, camera):
        try:
            rover = rover.strip().lower()
            camera = camera.strip().upper()

            y1 = int(self.year_from.get())
            y2 = int(self.year_to.get())

            url = f"https://api.nasa.gov/mars-photos/api/v1/rovers/{rover}/photos"

            self.root.config(cursor="watch")
            self.root.update()

            self.images = []
            found = False
            for year in range(y1, y2 + 1):
                for month in range(1, 13):
                    for day in [1, 10, 20]:
                        date = f"{year}-{month:02d}-{day:02d}"

                        params = {
                            "earth_date": date,
                            "api_key": API_KEY
                        }

                        try:
                            response = requests.get(url, params=params, timeout=10)
                        except:
                            continue

                        if response.status_code != 200:
                            continue

                        data = response.json()
                        photos = data.get("photos", [])

                        if not photos:
                            continue

                        filtered = [
                            p for p in photos
                            if p.get("camera", {}).get("name", "").upper() == camera
                        ]

                        if not filtered:
                            filtered = photos

                        for photo in filtered[:5]:
                            try:
                                img_url = photo["img_src"].replace("http://", "https://")
                                img_data = requests.get(img_url, timeout=10).content

                                image = Image.open(BytesIO(img_data)).resize((800, 500))
                                self.images.append(ImageTk.PhotoImage(image))
                            except:
                                continue

                        found = True
                        break

                    if found:
                        break
                if found:
                    break

            if not self.images:
                messagebox.showinfo("INFO", "No images found in this range :(")
                return

            self.index = 0
            self.show_image()

        except Exception as e:
            messagebox.showerror("ERROR", str(e))

        finally:
            self.root.config(cursor="")

    # ================= NAV =================
    def show_image(self):
        if self.images:
            self.img_label.config(image=self.images[self.index])

    def next_img(self):
        if self.images:
            self.index = (self.index + 1) % len(self.images)
            self.show_image()

    def prev_img(self):
        if self.images:
            self.index = (self.index - 1) % len(self.images)
            self.show_image()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()