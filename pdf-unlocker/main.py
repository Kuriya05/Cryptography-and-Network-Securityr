import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from pypdf import PdfReader, PdfWriter
import threading
import time

# ตั้งค่าธีมและสีแบบ modern
ctk.set_appearance_mode("System")  # ปรับเป็น Dark หรือ Light ตาม Windows อัตโนมัติ
ctk.set_default_color_theme("blue") # ธีมสีหลัก

is_running = False

def select_input_file():
    file_path = filedialog.askopenfilename(
        title="เลือกไฟล์ PDF ที่ติดรหัสผ่าน",
        filetypes=[("PDF files", "*.pdf")]
    )
    if file_path:
        entry_input.delete(0, tk.END)
        entry_input.insert(0, file_path)

def select_output_file():
    file_path = filedialog.asksaveasfilename(
        title="เลือกที่เซฟไฟล์ที่ถอดรหัสแล้ว",
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")]
    )
    if file_path:
        entry_output.delete(0, tk.END)
        entry_output.insert(0, file_path)

def toggle_action():
    global is_running
    if not is_running:
        is_running = True
        btn_start.configure(text="หยุดทำงาน (Cancel)", fg_color="#E74C3C", hover_color="#C0392B")
        threading.Thread(target=brute_force_pdf, daemon=True).start()
    else:
        is_running = False
        label_status.configure(text="กำลังหยุด...", text_color="#E67E22")

def brute_force_pdf():
    global is_running
    input_path = entry_input.get()
    output_path = entry_output.get()
    
    try:
        max_digits = int(entry_digits.get())
        if max_digits <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("ข้อผิดพลาด", "กรุณาระบุจำนวนหลักเป็นตัวเลขที่มากกว่า 0")
        reset_ui_state()
        return

    if not input_path or not output_path:
        messagebox.showerror("ข้อผิดพลาด", "กรุณาเลือกไฟล์และระบุที่เซฟให้ครบถ้วน")
        reset_ui_state()
        return
    
    label_status.configure(text="กำลังวิเคราะห์โครงสร้างไฟล์...", text_color="#3498DB")
    root.update_idletasks()
    
    try:
        reader = PdfReader(input_path)
    except Exception as e:
        messagebox.showerror("ข้อผิดพลาด", f"ไม่สามารถเปิดไฟล์ได้: {str(e)}")
        reset_ui_state()
        return
    
    if not reader.is_encrypted:
        messagebox.showinfo("แจ้งเตือน", "ไฟล์นี้ไม่ได้ล็อกรหัสผ่านไว้ตั้งแต่แรก")
        reset_ui_state()
        return

    found = False
    correct_password = ""
    total_attempts = 10 ** max_digits
    
    label_status.configure(text="กำลังดำเนินการเดารหัสผ่าน...", text_color="#E67E22")
    start_time = time.time()
    
    for i in range(total_attempts):
        if not is_running:
            break
            
        password = str(i).zfill(max_digits)
        
        # UI Optimization: อัปเดตทุกๆ 200 รอบเพื่อความเร็วสูงสุด
        if i % 200 == 0 or i == total_attempts - 1:
            label_current.configure(text=f"กำลังทดสอบ: {password}")
            progress_bar.set(i / total_attempts)
            root.update_idletasks()
        
        try:
            if reader.decrypt(password) > 0:
                correct_password = password
                found = True
                break
        except Exception:
            continue

    elapsed_time = round(time.time() - start_time, 2)

    if found:
        try:
            label_status.configure(text="พบรหัสผ่าน! กำลังบันทึกไฟล์...", text_color="#2ECC71")
            root.update_idletasks()
            
            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)

            with open(output_path, "wb") as f:
                writer.write(f)

            progress_bar.set(1.0)
            label_status.configure(text="ถอดรหัสสำเร็จ!", text_color="#2ECC71")
            label_current.configure(text=f"รหัสผ่านคือ: {correct_password} ({elapsed_time} วินาที)")
            messagebox.showinfo("สำเร็จ", f"🔓 ถอดรหัสสำเร็จ!\nรหัสผ่านคือ: {correct_password}\nใช้เวลา: {elapsed_time} วินาที\n\nบันทึกไฟล์เรียบร้อยแล้ว!")
        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", f"ไม่สามารถบันทึกไฟล์ได้: {str(e)}")
    elif not is_running:
        label_status.configure(text="ถูกยกเลิกโดยผู้ใช้", text_color="#7F8C8D")
        label_current.configure(text="หยุดทำงานแล้ว")
    else:
        progress_bar.set(1.0)
        label_status.configure(text="ไม่พบรหัสผ่าน", text_color="#E74C3C")
        label_current.configure(text="")
        messagebox.showwarning("ล้มเหลว", f"ไม่พบรหัสผ่านในระยะ {max_digits} หลัก")

    reset_ui_state()

def reset_ui_state():
    global is_running
    is_running = False
    btn_start.configure(text="เริ่มถอดรหัสผ่าน", fg_color="#2E7D32", hover_color="#1B5E20")
    if label_status.cget("text") == "กำลังดำเนินการเดารหัสผ่าน...":
        label_status.configure(text="พร้อมทำงาน", text_color=("#2C3E50", "#FFFFFF"))

# --- เริ่มต้นสร้างหน้าต่างแอปพลิเคชันยุคใหม่ ---
root = ctk.CTk()
root.title("PDF Decryptor Studio Pro")
root.geometry("650x480")
root.resizable(False, False)

# ฟอนต์ที่อ่านง่าย สไตล์แอปโมเดิร์น
FONT_TITLE = ("Kanit", 20, "bold")
FONT_TEXT = ("Kanit", 13)
FONT_BOLD = ("Kanit", 13, "bold")

# ส่วนหัวแอปพลิเคชัน (Header Dashboard)
header_label = ctk.CTkLabel(root, text="🔓 PDF Password Decryptor", font=FONT_TITLE)
header_label.pack(pady=(25, 20))

# การ์ดหลัก (Main Workspace Container)
card_frame = ctk.CTkFrame(root, corner_radius=15)
card_frame.pack(fill="both", expand=True, padx=30, pady=(0, 20))

# Row 1: ไฟล์ต้นฉบับ
lbl_in = ctk.CTkLabel(card_frame, text="ไฟล์ PDF ที่ติดรหัส:", font=FONT_BOLD)
lbl_in.grid(row=0, column=0, padx=20, pady=(25, 10), sticky="w")

entry_input = ctk.CTkEntry(card_frame, width=280, font=FONT_TEXT, placeholder_text="ยังไม่ได้เลือกไฟล์...")
entry_input.grid(row=0, column=1, padx=10, pady=(25, 10))

btn_in = ctk.CTkButton(card_frame, text="เลือกไฟล์", font=FONT_BOLD, width=100, command=select_input_file)
btn_in.grid(row=0, column=2, padx=20, pady=(25, 10))

# Row 2: ไฟล์ปลายทาง
lbl_out = ctk.CTkLabel(card_frame, text="บันทึกไฟล์ปลายทาง:", font=FONT_BOLD)
lbl_out.grid(row=1, column=0, padx=20, pady=10, sticky="w")

entry_output = ctk.CTkEntry(card_frame, width=280, font=FONT_TEXT, placeholder_text="ระบุตำแหน่งจัดเก็บ...")
entry_output.grid(row=1, column=1, padx=10, pady=10)

btn_out = ctk.CTkButton(card_frame, text="ระบุที่เซฟ", font=FONT_BOLD, width=100, command=select_output_file)
btn_out.grid(row=1, column=2, padx=20, pady=10)

# Row 3: จำนวนหลัก
lbl_digits = ctk.CTkLabel(card_frame, text="จำนวนหลัก (ตัวเลข):", font=FONT_BOLD)
lbl_digits.grid(row=2, column=0, padx=20, pady=10, sticky="w")

entry_digits = ctk.CTkEntry(card_frame, width=80, font=FONT_TEXT, justify="center")
entry_digits.insert(0, "4")
entry_digits.grid(row=2, column=1, padx=10, pady=10, sticky="w")

# โซนแสดงผลลัพธ์/สถานะความคืบหน้า (Status Panel)
status_frame = ctk.CTkFrame(card_frame, fg_color=("#F0F2F5", "#1E293B"), corner_radius=10)
status_frame.grid(row=3, column=0, columnspan=3, padx=20, pady=20, sticky="nsew")
card_frame.grid_rowconfigure(3, weight=1)
card_frame.grid_columnconfigure(1, weight=1)

label_status = ctk.CTkLabel(status_frame, text="พร้อมทำงาน", font=FONT_BOLD)
label_status.pack(pady=(12, 2))

label_current = ctk.CTkLabel(status_frame, text="กรุณาเลือกไฟล์เพื่อเริ่มต้น", font=FONT_TEXT, text_color="#7F8C8D")
label_current.pack(pady=(0, 10))

progress_bar = ctk.CTkProgressBar(status_frame, width=450)
progress_bar.set(0.0)
progress_bar.pack(pady=(0, 15))

# ปุ่มกดเริ่มงานใหญ่ด้านล่าง
btn_start = ctk.CTkButton(
    root, 
    text="เริ่มถอดรหัสผ่าน", 
    font=("Kanit", 15, "bold"), 
    height=45, 
    width=200, 
    fg_color="#2E7D32", 
    hover_color="#1B5E20",
    command=toggle_action
)
btn_start.pack(pady=(0, 25))

root.mainloop()