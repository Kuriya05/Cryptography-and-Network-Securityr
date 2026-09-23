import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import font as tkfont
import pyperclip  # สำหรับช่วยกดคัดลอกข้อความ
from PIL import Image, ImageTk
import os

class ModernImageViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("✨ PhotoFlux - Pink Minimal Studio")
        self.root.geometry("1100x800") # ขยายหน้าต่างเล็กน้อยเพื่อรองรับแถบที่อยู่ไฟล์
        self.root.configure(bg="#FAFAFA") 

        # ตั้งค่าฟอนต์
        self.title_font = tkfont.Font(family="Segoe UI", size=14, weight="bold")
        self.btn_font = tkfont.Font(family="Segoe UI", size=10, weight="bold")
        self.status_font = tkfont.Font(family="Segoe UI", size=9, weight="bold")
        self.path_font = tkfont.Font(family="Consolas", size=9) # ฟอนต์สไตล์ Code สำหรับแสดงพาธไฟล์

        # --- 1. เลเยอร์แถบเครื่องมือด้านบน (Top Bar Layer) ---
        self.top_frame = tk.Frame(root, bg="#FFE4E8", height=65) 
        self.top_frame.pack(fill=tk.X, side=tk.TOP, padx=15, pady=(15, 5))
        self.top_frame.pack_propagate(False)

        self.lbl_logo = tk.Label(
            self.top_frame, text="PHOTOFLUX .", fg="#DE6B7B", bg="#FFE4E8",
            font=self.title_font, padx=15
        )
        self.lbl_logo.pack(side=tk.LEFT, anchor="center")

        self.btn_open = tk.Button(
            self.top_frame, text="📂 Open Image", command=self.open_image,
            bg="#FFFFFF", fg="#DE6B7B", font=self.btn_font,
            activebackground="#DE6B7B", activeforeground="#FFFFFF",
            relief=tk.FLAT, bd=0, padx=20, pady=8, cursor="hand2"
        )
        self.btn_open.pack(side=tk.RIGHT, padx=15, anchor="center")

        # --- 2. เลเยอร์แถบควบคุมด้านขวา (Control Panel Layer) ---
        self.side_frame = tk.Frame(root, bg="#FFF0F2", width=220) 
        self.side_frame.pack(fill=tk.Y, side=tk.RIGHT, padx=(5, 15), pady=(5, 5))
        self.side_frame.pack_propagate(False)

        tk.Label(
            self.side_frame, text="TRANSFORM TOOLS", fg="#4A4A4A", bg="#FFF0F2",
            font=self.btn_font
        ).pack(anchor=tk.W, padx=20, pady=(25, 15))

        def create_side_button(text, command):
            btn = tk.Button(
                self.side_frame, text=text, command=command,
                bg="#FFFFFF", fg="#4A4A4A", font=self.btn_font,
                activebackground="#FFE4E8", activeforeground="#DE6B7B",
                relief=tk.FLAT, bd=0, height=2, width=20, cursor="hand2"
            )
            btn.pack(pady=6, padx=20, anchor=tk.W)
            btn.bind("<Enter>", lambda e: btn.config(bg="#FFE4E8", fg="#DE6B7B"))
            btn.bind("<Leave>", lambda e: btn.config(bg="#FFFFFF", fg="#4A4A4A"))
            return btn

        self.btn_rot_left = create_side_button("↩  Rotate Left", lambda: self.rotate_image(90))
        self.btn_rot_right = create_side_button("↪  Rotate Right", lambda: self.rotate_image(-90))
        self.btn_flip_hor = create_side_button("↔  Flip Horizontal", lambda: self.rotate_image("FLIP_HOR"))
        self.btn_flip_ver = create_side_button("↕  Flip Vertical", lambda: self.rotate_image("FLIP_VER"))

        # --- 3. เลเยอร์แสดงตำแหน่งที่อยู่ไฟล์แบบเต็ม (File Path Location Bar) ---
        self.path_frame = tk.Frame(root, bg="#FFF0F2", height=45) # แถบชมพูพาสเทลด้านล่าง
        self.path_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=15, pady=(5, 15))
        self.path_frame.pack_propagate(False)

        # ช่องแสดงตำแหน่งไฟล์ (สร้างเป็น Entry เพื่อให้คลีนและก๊อปปี้ง่าย)
        self.entry_path = tk.Entry(
            self.path_frame, fg="#555555", bg="#FFFFFF", font=self.path_font,
            relief=tk.FLAT, bd=0
        )
        self.entry_path.insert(0, " Location: No image selected")
        self.entry_path.config(state="readonly") # ล็อกไม่ให้ผู้ใช้พิมพ์เล่นเอง
        self.entry_path.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 5), pady=8)

        # ปุ่มกด Copy ลิงก์ที่อยู่ไฟล์
        self.btn_copy = tk.Button(
            self.path_frame, text="📋 Copy Path", command=self.copy_path,
            bg="#DE6B7B", fg="#FFFFFF", font=self.status_font,
            activebackground="#C25A68", activeforeground="#FFFFFF",
            relief=tk.FLAT, bd=0, padx=12, cursor="hand2"
        )
        self.btn_copy.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=8)

        # --- 4. เลเยอร์แถบแสดงชื่อไฟล์สั้น ๆ (Status Bar บนสุดของด้านล่าง) ---
        self.bottom_frame = tk.Frame(root, bg="#FAFAFA")
        self.bottom_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(5, 0))
        
        self.lbl_path = tk.Label(
            self.bottom_frame, text="STATUS // Ready to load image", 
            fg="#888888", bg="#FAFAFA", font=self.status_font, padx=20
        )
        self.lbl_path.pack(side=tk.LEFT)

        # --- 5. เลเยอร์พื้นที่แสดงรูปภาพหลัก (Main Workspace) ---
        self.image_container = tk.Frame(root, bg="#FFFFFF", highlightbackground="#FFE4E8", highlightthickness=1)
        self.image_container.pack(fill=tk.BOTH, expand=True, padx=(15, 5), pady=5)

        self.image_label = tk.Label(self.image_container, bg="#FFFFFF")
        self.image_label.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # ตัวแปรเก็บข้อมูล
        self.current_file_path = "" # เก็บพิกัดไฟล์เต็ม
        self.pil_original = None
        self.tk_image = None

    def open_image(self):
        file_types = [
            ("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.webp *.tiff *.PNG *.JPG"),
            ("All files", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(title="Select An Image", filetypes=file_types)
        
        if file_path:
            try:
                # บันทึกตำแหน่งพาธเต็ม
                self.current_file_path = os.path.normpath(file_path)
                filename = os.path.basename(file_path)
                self.lbl_path.config(text=f"LOADED // {filename}", fg="#DE6B7B") 
                
                # แสดงพาธไฟล์ลงในกล่องข้อความด้านล่าง
                self.entry_path.config(state="normal")
                self.entry_path.delete(0, tk.END)
                self.entry_path.insert(0, f" {self.current_file_path}")
                self.entry_path.config(state="readonly")

                self.pil_original = Image.open(file_path)
                self.display_image()
            except Exception as e:
                self.lbl_path.config(text="ERROR // Failed to load file", fg="#FF4444")
                messagebox.showerror("Error", f"Cannot open image:\n{str(e)}")

    def copy_path(self):
        if self.current_file_path:
            try:
                pyperclip.copy(self.current_file_path)
                messagebox.showinfo("Success", "คัดลอกตำแหน่งรูปภาพลง Clipboard เรียบร้อยแล้วครับ! 💕")
            except Exception:
                # กรณีเครื่องผู้ใช้ยังไม่ได้ลงโมดูล pyperclip จะดึงข้อมูลจาก entry โดยตรงแทน
                self.root.clipboard_clear()
                self.root.clipboard_append(self.current_file_path)
                messagebox.showinfo("Success", "คัดลอกตำแหน่งรูปภาพเรียบร้อยแล้วครับ! 💕")
        else:
            messagebox.showwarning("Warning", "กรุณาเปิดรูปภาพก่อนกดคัดลอกครับ!")

    def rotate_image(self, action):
        if self.pil_original is None:
            self.lbl_path.config(text="NOTICE // Please open an image first", fg="#DE6B7B")
            return
        
        if action == 90:
            self.pil_original = self.pil_original.rotate(90, expand=True)
        elif action == -90:
            self.pil_original = self.pil_original.rotate(-90, expand=True)
        elif action == "FLIP_HOR":
            self.pil_original = self.pil_original.transpose(Image.FLIP_LEFT_RIGHT)
        elif action == "FLIP_VER":
            self.pil_original = self.pil_original.transpose(Image.FLIP_TOP_BOTTOM)
            
        self.display_image()

    def display_image(self):
        if self.pil_original:
            render_img = self.pil_original.copy()
            
            self.root.update_idletasks()
            window_width = self.image_label.winfo_width()
            window_height = self.image_label.winfo_height()
            
            if window_width <= 1 or window_height <= 1:
                window_width, window_height = 750, 550

            render_img.thumbnail((window_width, window_height), Image.Resampling.LANCZOS)
            
            self.tk_image = ImageTk.PhotoImage(render_img)
            self.image_label.config(image=self.tk_image)

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernImageViewer(root)
    root.mainloop()