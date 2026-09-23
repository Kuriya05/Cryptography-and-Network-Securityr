import tkinter as tk
from tkinter import messagebox


def calculate_check_digit():
    citizen_id = entry_id.get().strip()

    if not citizen_id.isdigit() or len(citizen_id) != 12:
        messagebox.showerror(
            "ข้อผิดพลาด", "กรุณากรอกเฉพาะตัวเลขให้ครบ 12 หลัก"
        )
        return

    digits = [int(d) for d in citizen_id]
    multipliers = [13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2]
    step1_details = []
    total_sum = 0

    for i in range(12):
        prod = digits[i] * multipliers[i]
        total_sum += prod
        step1_details.append(f"({digits[i]} × {multipliers[i]})")

    step1_text = " + ".join(step1_details) + f"\n= {total_sum}"

    remainder = total_sum % 11
    step2_text = f"{total_sum} ÷ 11  เหลือเศษ  {remainder}"

    sub_result = 11 - remainder
    step3_text = f"11 - {remainder} = {sub_result}"

    check_digit = (11 - remainder) % 10
    if sub_result == 11:
        step4_text = "เศษเป็น 11 ให้ปัดตัวเลขหลักสุดท้ายเป็น ➔ 0"
    elif sub_result == 10:
        step4_text = "เศษเป็น 10 ให้ปัดตัวเลขหลักสุดท้ายเป็น ➔ 1"
    else:
        step4_text = f"ดึงตัวเลขหลักหน่วยมาใช้งานโดยตรง ➔ {check_digit}"

    global final_formatted_id
    full_id = citizen_id + str(check_digit)
    final_formatted_id = f"{full_id[0]}-{full_id[1:5]}-{full_id[5:10]}-{full_id[10:12]}-{full_id[12]}"

    result_text.config(state=tk.NORMAL)
    result_text.delete("1.0", tk.END)

    output = f"✨ ผลการคำนวณและวิธีทำอย่างละเอียด ✨\n"
    output += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    output += f"▸ ขั้นตอนที่ 1: คูณเลขประจำหลักแล้วนำมารวมกัน\n  {step1_text}\n\n"
    output += f"▸ ขั้นตอนที่ 2: นำผลรวมมาหารเอาเศษด้วย 11\n  {step2_text}\n\n"
    output += f"▸ ขั้นตอนที่ 3: นำเลข 11 ไปลบกับเศษที่เหลือ\n  {step3_text}\n\n"
    output += f"▸ ขั้นตอนที่ 4: ตรวจสอบเงื่อนไขหลักสุดท้าย\n  {step4_text}\n\n"
    output += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    output += f"🎉 เลขบัตรประชาชน 13 หลักเต็ม: {final_formatted_id}"

    result_text.insert(tk.END, output)
    result_text.config(state=tk.DISABLED)
    btn_copy.config(state=tk.NORMAL)


def copy_to_clipboard():
    if "final_formatted_id" in globals() and final_formatted_id:
        root.clipboard_clear()
        root.clipboard_append(final_formatted_id)
        messagebox.showinfo(
            "คัดลอกสำเร็จ", f"คัดลอก {final_formatted_id} ไปยังคลิปบอร์ดแล้ว"
        )


# --- ดีไซน์หน้าต่างโปรแกรม (Theme: Pastel Pink & Elegant Sarabun) ---
# ระบบจะเลือกใช้ TH Sarabun New หรือ TH Sarabun PSK ตามที่มีในเครื่องคอมพิวเตอร์ของคุณ
FONT_FAMILY = ("TH Sarabun New", "TH Sarabun PSK", "Arial")
FONT_MAIN = (FONT_FAMILY[0], 15)
FONT_BOLD = (FONT_FAMILY[0], 15, "bold")
FONT_TITLE = (FONT_FAMILY[0], 20, "bold")

COLOR_BG = "#FFF0F5"  # สีชมพูอ่อน Lavender Blush ดูนุ่มนวล สบายตา
COLOR_PRIMARY = "#D16B8D"  # สีชมพูกุหลาบเข้ม (Rose Pink) ดูเรียบหรู
COLOR_SECONDARY = "#A4B0BE"  # สีเทาซอฟต์ๆ สำหรับปุ่มรอง
COLOR_TEXT_BOX = "#FFFFFF"  # กล่องข้อความขาวสะอาด

root = tk.Tk()
root.title("Thai ID Check Digit Calculator")
root.geometry("580x660")
root.configure(bg=COLOR_BG)
root.resizable(False, False)

# ส่วนหัวโปรแกรม
frame_header = tk.Frame(root, bg=COLOR_BG)
frame_header.pack(pady=20)

label_title = tk.Label(
    frame_header,
    text="ระบบคำนวณเลขท้ายบัตรประชาชน",
    font=FONT_TITLE,
    bg=COLOR_BG,
    fg="#4A2834",  # สีน้ำตาลอมแดงเข้ม เข้ากับโทนชมพู
)
label_title.pack()

label_sub = tk.Label(
    frame_header,
    text="กรอกตัวเลข 12 หลักแรกเพื่อตรวจสอบ Check Digit ตัวสุดท้าย",
    font=FONT_MAIN,
    bg=COLOR_BG,
    fg="#8C6D79",
)
label_sub.pack(pady=2)

# ส่วนรับข้อมูลอินพุต
entry_id = tk.Entry(
    root,
    font=("Consolas", 16, "bold"),
    justify="center",
    width=18,
    bd=0,
    highlightthickness=1,
    highlightbackground="#E8C5D0",
    highlightcolor=COLOR_PRIMARY,
)
entry_id.pack(pady=5, ipady=8)
entry_id.focus()

# กลุ่มปุ่มกด
frame_buttons = tk.Frame(root, bg=COLOR_BG)
frame_buttons.pack(pady=15)

btn_calculate = tk.Button(
    frame_buttons,
    text="คำนวณและแสดงวิธีทำ",
    font=FONT_BOLD,
    bg=COLOR_PRIMARY,
    fg="white",
    bd=0,
    padx=15,
    pady=4,
    activebackground="#B55274",
    activeforeground="white",
    cursor="hand2",
    command=calculate_check_digit,
)
btn_calculate.pack(side=tk.LEFT, padx=5)

btn_copy = tk.Button(
    frame_buttons,
    text="📋 คัดลอกเลข 13 หลัก",
    font=FONT_MAIN,
    bg=COLOR_SECONDARY,
    fg="white",
    bd=0,
    padx=15,
    pady=4,
    activebackground="#8894A6",
    activeforeground="white",
    cursor="hand2",
    state=tk.DISABLED,
    command=copy_to_clipboard,
)
btn_copy.pack(side=tk.LEFT, padx=5)

# ส่วนการแสดงผลวิธีทำแบบละเอียด
# หมายเหตุ: ในกล่องข้อความวิธีทำสูตรคณิตศาสตร์ จำเป็นต้องใช้ฟอนต์ตัวพิมพ์ตรง (Consolas) เพื่อจัดช่องไฟเครื่องหมายบวกลบคูณหารให้ตรงกัน
result_text = tk.Text(
    root,
    font=("Consolas", 10),
    width=68,
    height=21,
    bg=COLOR_TEXT_BOX,
    fg="#4A2834",
    bd=0,
    highlightthickness=1,
    highlightbackground="#F2D6E0",
    wrap=tk.WORD,
    padx=15,
    pady=15,
)
result_text.pack(pady=10)
result_text.insert(tk.END, "💡 รอการกรอกข้อมูลและกดปุ่มคำนวณ...")
result_text.config(state=tk.DISABLED)

final_formatted_id = ""

root.mainloop()