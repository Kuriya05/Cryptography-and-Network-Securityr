import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os

class ImageVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("โปรแกรมดูรูปภาพ (Image Viewer)")
        self.root.geometry("800x600")
        self.root.configure(bg="#2b2b2b")

        # แก้ไขจุดนี้: เปลี่ยน padding เป็น padx และ pady แทน
        self.top_frame = tk.Frame(root, bg="#1e1e1e", padx=10, pady=10)
        self.top_frame.pack(fill=tk.X)

        self.btn_open = tk.Button(
            self.top_frame, 
            text="เปิดไฟล์รูปภาพ", 
            command=self.open_image,
            bg="#007acc", 
            fg="white", 
            font=("Helvetica", 12, "bold"),
            padx=10, 
            pady=5,
            relief=tk.FLAT
        )
        self.btn_open.pack(side=tk.LEFT, padx=10)

        self.lbl_path = tk.Label(
            self.top_frame, 
            text="ยังไม่ได้เลือกไฟล์", 
            fg="#aaaaaa", 
            bg="#1e1e1e",
            font=("Helvetica", 10)
        )
        self.lbl_path.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True, anchor=tk.W)

        # ส่วนแสดงรูปภาพ
        self.image_label = tk.Label(root, bg="#2b2b2b")
        self.image_label.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # ตัวแปรเก็บอ้างอิงรูปภาพ
        self.tk_image = None

    def open_image(self):
        file_types = [
            ("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.webp *.tiff *.PNG *.JPG"),
            ("All files", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="เลือกรูปภาพที่ต้องการเปิด",
            filetypes=file_types
        )
        
        if file_path:
            try:
                self.lbl_path.config(text=os.path.basename(file_path))
                
                pil_image = Image.open(file_path)
                
                window_width = self.image_label.winfo_width()
                window_height = self.image_label.winfo_height()
                
                if window_width <= 1 or window_height <= 1:
                    window_width, window_height = 760, 500 

                pil_image.thumbnail((window_width, window_height), Image.Resampling.LANCZOS)
                
                self.tk_image = ImageTk.PhotoImage(pil_image)
                self.image_label.config(image=self.tk_image)
                
            except Exception as e:
                messagebox.showerror("เกิดข้อผิดพลาด", f"ไม่สามารถเปิดไฟล์รูปภาพได้:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageVisualizer(root)
    root.mainloop()