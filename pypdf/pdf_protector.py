import tkinter as tk
from tkinter import filedialog, messagebox
from pypdf import PdfReader, PdfWriter
import os

# --- สีและสไตล์ (Theme - โทนชมพูสว่าง) ---
COLOR_BG = "#FFF0F5"         # สีพื้นหลังหลัก (Lavender Blush - ชมพูอ่อนละมุน)
COLOR_CARD = "#FFFFFF"       # สีพื้นหลังส่วนเนื้อหา (ขาวสะอาด)
COLOR_TEXT_MAIN = "#4A2E35"  # สีตัวอักษรหลัก (น้ำตาลเข้มอมม่วง อ่านง่าย ไม่มืดทึบ)
COLOR_PINK_PRIMARY = "#FF69B4" # สีชมพูหลักสำหรับปุ่ม (Hot Pink)
COLOR_PINK_HOVER = "#FF85C2"   # สีชมพูเมื่อเอาเมาส์ชี้
COLOR_BORDER = "#FFC0CB"     # สีเส้นขอบ (ชมพูพาสเทล)

# --- ขนาดฟอนต์ตามบรีฟ (18-20) ---
FONT_TITLE = ("Segoe UI", 20, "bold")  # หัวข้อใหญ่ขนาด 20
FONT_LABEL = ("Segoe UI", 18, "bold")  # ตัวหนังสืออธิบายขนาด 18
FONT_INPUT = ("Segoe UI", 16)          # ช่องกรอกขนาด 16 (เพื่อให้สมดุลกับหัวข้อ)

# --- ฟังก์ชันการทำงาน ---
def select_file():
    file_path = filedialog.askopenfilename(
        filetypes=[("PDF Files", "*.pdf")]
    )
    if file_path:
        entry_file_path.delete(0, tk.END)
        entry_file_path.insert(0, file_path)

def encrypt_pdf():
    input_path = entry_file_path.get()
    password = entry_password.get()
    
    if not input_path:
        messagebox.showerror("Error", "กรุณาเลือกไฟล์ PDF ก่อนครับ")
        return
    if not password:
        messagebox.showerror("Error", "กรุณาตั้งรหัสผ่านด้วยครับ")
        return
        
    try:
        dir_name, file_name = os.path.split(input_path)
        name, ext = os.path.splitext(file_name)
        output_path = filedialog.asksaveasfilename(
            initialdir=dir_name,
            initialfile=f"{name}_protected{ext}",
            filetypes=[("PDF Files", "*.pdf")]
        )
        
        if not output_path:
            return 
            
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        for page in reader.pages:
            writer.add_page(page)
            
        writer.encrypt(password)
        
        with open(output_path, "wb") as f:
            writer.write(f)
            
        messagebox.showinfo("Success", "ล็อกไฟล์ PDF เรียบร้อยแล้ว!")
        
    except Exception as e:
        messagebox.showerror("Error", f"เกิดข้อผิดพลาด: {str(e)}")

# --- ลูกเล่นปุ่ม (Hover Effect) ---
def on_enter(e):
    e.widget['background'] = COLOR_PINK_HOVER

def on_leave(e):
    e.widget['background'] = COLOR_PINK_PRIMARY

# --- สร้างหน้าต่าง GUI ---
root = tk.Tk()
root.title("PDF Lock • Pink Style")
root.geometry("600x480")      # ขยายหน้าต่างเล็กน้อยเพื่อให้รองรับฟอนต์ขนาดใหญ่
root.configure(bg=COLOR_BG)

# จัดหน้าต่างให้อยู่กึ่งกลางหน้าจอ
root.update_idletasks()
width = root.winfo_width()
height = root.winfo_height()
x = (root.winfo_screenwidth() // 2) - (width // 2)
y = (root.winfo_screenheight() // 2) - (height // 2)
root.geometry('{}x{}+{}+{}'.format(width, height, x, y))

# ส่วนหัวโปรแกรม (ขนาด 20)
title_label = tk.Label(root, text="🌸 PDF Password Protector 🌸", font=FONT_TITLE, fg=COLOR_PINK_PRIMARY, bg=COLOR_BG)
title_label.pack(pady=(35, 20))

# การ์ดส่วนเนื้อหา (สีขาวสะอาด ขอบชมพู)
card_frame = tk.Frame(root, bg=COLOR_CARD, padx=30, pady=30, bd=0, highlightthickness=2, highlightbackground=COLOR_BORDER)
card_frame.pack(fill="both", expand=True, padx=40, pady=(0, 35))

# --- ส่วนของไฟล์ ---
label_file = tk.Label(card_frame, text="เลือกไฟล์ PDF:", font=FONT_LABEL, fg=COLOR_TEXT_MAIN, bg=COLOR_CARD)
label_file.pack(anchor="w", pady=(0, 8))

frame_file = tk.Frame(card_frame, bg=COLOR_CARD)
frame_file.pack(fill="x")

entry_file_path = tk.Entry(frame_file, font=FONT_INPUT, bg="#FAFAFA", fg=COLOR_TEXT_MAIN, bd=0, highlightthickness=1, highlightbackground=COLOR_BORDER)
entry_file_path.pack(side="left", ipady=6, expand=True, fill="x", padx=(0, 10))

btn_browse = tk.Button(frame_file, text="Browse...", command=select_file, font=("Segoe UI", 14, "bold"), bg=COLOR_PINK_PRIMARY, fg="white", bd=0, padx=15, pady=3, cursor="hand2")
btn_browse.pack(side="right")
btn_browse.bind("<Enter>", on_enter)
btn_browse.bind("<Leave>", on_leave)

# --- ส่วนของรหัสผ่าน ---
label_password = tk.Label(card_frame, text="ตั้งรหัสผ่านป้องกัน:", font=FONT_LABEL, fg=COLOR_TEXT_MAIN, bg=COLOR_CARD)
label_password.pack(anchor="w", pady=(20, 8))

entry_password = tk.Entry(card_frame, font=FONT_INPUT, show="*", bg="#FAFAFA", fg=COLOR_TEXT_MAIN, bd=0, highlightthickness=1, highlightbackground=COLOR_BORDER)
entry_password.pack(fill="x", ipady=6)

# --- ปุ่มกดล็อกไฟล์ (ขนาดใหญ่ เด่นชัด) ---
btn_encrypt = tk.Button(
    card_frame, 
    text="ใส่รหัสป้องกัน PDF", 
    command=encrypt_pdf, 
    bg=COLOR_PINK_PRIMARY,
    fg="white", 
    font=("Segoe UI", 18, "bold"), # ปุ่มกดขนาดใหญ่ 18 ตามต้องการ
    bd=0,
    pady=10,
    cursor="hand2"
)
btn_encrypt.pack(fill="x", pady=(30, 0))
btn_encrypt.bind("<Enter>", on_enter)
btn_encrypt.bind("<Leave>", on_leave)

root.mainloop()