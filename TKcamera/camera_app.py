import os
import time
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk
import cv2
import numpy as np
from PIL import Image, ImageTk


class MinimalCameraApp:

    def __init__(self, window):
        self.window = window
        self.window.title("🎀 Pinky Auto-Camera & Props 🎀")
        self.window.geometry("950x650")
        self.window.configure(bg="#FFF0F5")  # LavenderBlush (ชมพูอ่อนมาก)

        # --- การตั้งค่าสไตล์ UI (Pink Theme) ---
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # ปรับแต่งสไตล์ขององค์ประกอบสีชมพู
        self.style.configure("TLabel", background="#FFF0F5", foreground="#4A1525")
        self.style.configure(
            "TRadiobutton",
            background="#FFF0F5",
            foreground="#691B31",
            font=("Arial", 10),
        )
        self.style.configure(
            "TCheckbutton",
            background="#FFF0F5",
            foreground="#691B31",
            font=("Arial", 10),
        )

        # --- ตัวแปรควบคุม ---
        self.current_filter = tk.StringVar(value="Normal")
        self.timestamp_on = tk.BooleanVar(value=True)
        self.auto_snap_on = tk.BooleanVar(value=False)
        self.glasses_prop_on = tk.BooleanVar(value=False)  # เปิด/ปิด แว่นตา พร็อพ

        # --- ตัวแปรสำหรับระบบนับถอยหลัง ---
        self.timer_started_time = None
        self.countdown_duration = 3
        self.has_snapped = False

        # --- โหลดโมเดลตรวจจับใบหน้า ---
        self.face_cascade = None
        local_cascade = "haarcascade_frontalface_default.xml"

        if os.path.exists(local_cascade):
            try:
                cascade = cv2.CascadeClassifier(local_cascade)
                if not cascade.empty():
                    self.face_cascade = cascade
            except Exception:
                self.face_cascade = None

        if self.face_cascade is None:
            print(
                "ระบบแจ้งเตือน: ไม่พบไฟล์ตรวจจับใบหน้า (แว่นตาและ Auto-Snap จะใช้ไม่ได้ชั่วคราว ปุ่มถ่ายรูปปกติทำงานได้)"
            )

        # --- จัดวางโครงสร้างหน้าจอ ---
        self.create_layout()

        # เริ่มทำงานกล้อง
        self.cap = cv2.VideoCapture(0)
        self.update_frame()

    def create_layout(self):
        """จัดระเบียบโครงสร้างหน้าต่างโปรแกรมแยกสัดส่วนชัดเจน"""

        # ---------------- ฝั่งซ้าย: พื้นที่แสดงกล้อง ----------------
        self.video_container = tk.Frame(
            self.window, bg="#FFE4E1", bd=2, relief="ridge"
        )  # MistyRose
        self.video_container.pack(
            side="left", expand=True, fill="both", padx=20, pady=20
        )

        self.video_label = tk.Label(self.video_container, bg="#FFF0F5", bd=0)
        self.video_label.pack(expand=True, fill="both", padx=5, pady=5)

        # ---------------- ฝั่งขวา: แผงควบคุมสไตล์ชมพูหวาน ----------------
        self.side_panel = tk.Frame(self.window, bg="#FFF0F5", width=250)
        self.side_panel.pack(side="right", fill="y", padx=(0, 20), pady=20)
        self.side_panel.pack_propagate(False)

        # ส่วนหัวข้อใหญ่
        lbl_title = tk.Label(
            self.side_panel,
            text="🌸 PINKY CAM 🌸",
            font=("Arial", 16, "bold"),
            bg="#FFF0F5",
            fg="#FF1493",  # DeepPink
        )
        lbl_title.pack(anchor="center", pady=(10, 15))

        # --- บล็อกที่ 1: ปุ่มสั่งการหลัก (Action Buttons) ---
        btn_frame = tk.LabelFrame(
            self.side_panel,
            text=" ACTIONS ",
            font=("Arial", 9, "bold"),
            bg="#FFF0F5",
            fg="#FF69B4",
        )
        btn_frame.pack(fill="x", pady=5, ipady=5)

        self.btn_snap = tk.Button(
            btn_frame,
            text="📸 TAKE PHOTO",
            command=self.take_snapshot,
            bg="#FF1493",
            fg="white",
            font=("Arial", 11, "bold"),
            bd=0,
            relief="flat",
            cursor="hand2",
            activebackground="#FF69B4",
            activeforeground="white",
        )
        self.btn_snap.pack(fill="x", padx=10, pady=5, ipady=8)

        self.btn_timer = tk.Button(
            btn_frame,
            text="⏳ TIMER SNAP (3s)",
            command=self.start_timer_snap,
            bg="#FF69B4",
            fg="white",
            font=("Arial", 10, "bold"),
            bd=0,
            relief="flat",
            cursor="hand2",
            activebackground="#FFB6C1",
            activeforeground="#4A1525",
        )
        self.btn_timer.pack(fill="x", padx=10, pady=5, ipady=6)

        # --- บล็อกที่ 2: เมนูเปลี่ยนฟิลเตอร์ (Filters) ---
        filter_frame = tk.LabelFrame(
            self.side_panel,
            text=" FILTERS ",
            font=("Arial", 9, "bold"),
            bg="#FFF0F5",
            fg="#FF69B4",
        )
        filter_frame.pack(fill="x", pady=5, ipady=5)

        filters = [
            "Normal",
            "Grayscale",
            "Sepia ✨",
            "Canny Edge",
            "Blur",
            "Invert 🎞️",
        ]
        for f in filters:
            r_btn = ttk.Radiobutton(
                filter_frame,
                text=f,
                variable=self.current_filter,
                value=f.replace(" ✨", "").replace(" 🎞️", ""),
            )
            r_btn.pack(anchor="w", pady=3, padx=15)

        # --- บล็อกที่ 3: พร็อพแต่งรูป & ฟังก์ชันเสริม (Props & Options) ---
        opt_frame = tk.LabelFrame(
            self.side_panel,
            text=" PROPS & OPTIONS ",
            font=("Arial", 9, "bold"),
            bg="#FFF0F5",
            fg="#FF69B4",
        )
        opt_frame.pack(fill="x", pady=5, ipady=5)

        # ปุ่มเปิด/ปิดแว่นตาพิกเซลสุดคูล
        chk_glasses = ttk.Checkbutton(
            opt_frame, text="👓 Thug Glasses Prop", variable=self.glasses_prop_on
        )
        chk_glasses.pack(anchor="w", pady=3, padx=15)

        # ปุ่มระบบถ่ายรูปอัตโนมัติด้วยใบหน้า
        if self.face_cascade is not None:
            chk_auto = ttk.Checkbutton(
                opt_frame, text="📷 Auto-Snap (Face)", variable=self.auto_snap_on
            )
            chk_auto.pack(anchor="w", pady=3, padx=15)

        chk_time = ttk.Checkbutton(
            opt_frame, text="🎀 CCTV Timestamp", variable=self.timestamp_on
        )
        chk_time.pack(anchor="w", pady=3, padx=15)

        # ปุ่มปิดโปรแกรม (อยู่ด้านล่างสุด แยกสีเทา-ชมพูเข้มชัดเจน)
        btn_exit = tk.Button(
            self.side_panel,
            text="CLOSE APP",
            command=self.quit_app,
            bg="#DB7093",  # PaleVioletRed
            fg="white",
            font=("Arial", 10, "bold"),
            bd=0,
            relief="flat",
            cursor="hand2",
            activebackground="#C71585",
        )
        btn_exit.pack(side="bottom", fill="x", ipady=6)

    def start_timer_snap(self):
        """เริ่มนับถอยหลัง"""
        self.has_snapped = False
        self.timer_started_time = time.time()

    def draw_glasses(self, frame, x, y, w, h):
        """ฟังก์ชันสำหรับวาดแว่นตาแฟชั่นลงบนใบหน้าคน"""
        # คำนวณตำแหน่งแว่นตาให้อยู่กึ่งกลางตาโดยประมาณ
        gw = int(w * 0.75)
        gh = int(h * 0.15)
        gx = x + int(w * 0.125)
        gy = y + int(h * 0.35)

        # วาดตัวแว่นตาสีดำหนาๆ
        cv2.rectangle(frame, (gx, gy), (gx + gw, gy + gh), (10, 10, 10), -1)

        # วาดเลนส์แว่นซ้าย-ขวาเว้นตรงกลาง
        bridge_w = int(gw * 0.15)
        lens_w = (gw - bridge_w) // 2

        # แถบสะท้อนแสงสีขาวบนแว่นตาเพิ่มความชิค
        cv2.rectangle(
            frame,
            (gx + 5, gy + 3),
            (gx + 15, gy + gh - 3),
            (255, 255, 255),
            -1,
        )
        cv2.rectangle(
            frame,
            (gx + lens_w + bridge_w + 5, gy + 3),
            (gx + lens_w + bridge_w + 15, gy + gh - 3),
            (255, 255, 255),
            -1,
        )

    def process_image(self, frame):
        """จัดการประมวลผลภาพรวม ใส่พร็อพ และฟิลเตอร์"""
        face_in_frame = False
        fh_shape, fw_shape, _ = frame.shape

        # 1. ระบบตรวจจับใบหน้า และ ใส่พร็อพแว่นตา
        if self.face_cascade is not None:
            try:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(
                    gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60)
                )
                if len(faces) > 0:
                    face_in_frame = True
                    for x, y, fw, fh in faces:
                        # วาดกล่องกรอบหน้าสีชมพูหวาน
                        cv2.rectangle(
                            frame,
                            (x, y),
                            (x + fw, y + fh),
                            (180, 105, 255),
                            2,
                        )

                        # ถ้าเปิดโหมดพร็อพ -> วาดแว่นตา Thug Life
                        if self.glasses_prop_on.get():
                            self.draw_glasses(frame, x, y, fw, fh)
            except Exception:
                face_in_frame = False

        # 2. กลไกการนับถอยหลังถ่ายภาพ
        is_countdown_active = False
        trigger_time = None

        if self.auto_snap_on.get() and face_in_frame:
            if self.timer_started_time is None and not self.has_snapped:
                self.timer_started_time = time.time()
            is_countdown_active = True
            trigger_time = self.timer_started_time
        elif self.timer_started_time is not None:
            is_countdown_active = True
            trigger_time = self.timer_started_time
        else:
            if not face_in_frame:
                self.has_snapped = False

        # แสดงข้อความนับถอยหลังสีชมพูขาวสุดหวานบนจอภาพ
        if is_countdown_active and trigger_time is not None and not self.has_snapped:
            elapsed_time = time.time() - trigger_time
            remaining_time = max(
                0, int(self.countdown_duration - elapsed_time) + 1
            )

            if remaining_time > 0:
                text = f"SMILE! Snap in {remaining_time}..."
                # ขอบตัวหนังสือสีเข้ม
                cv2.putText(
                    frame,
                    text,
                    (fw_shape // 2 - 160, 60),
                    cv2.FONT_HERSHEY_ROUNDED_RECT_ONLY
                    if hasattr(cv2, "FONT_HERSHEY_ROUNDED_RECT_ONLY")
                    else cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    (100, 20, 150),
                    4,
                    cv2.LINE_AA,
                )
                # ตัวหนังสือสีชมพูสว่างข้างใน
                cv2.putText(
                    frame,
                    text,
                    (fw_shape // 2 - 160, 60),
                    cv2.FONT_HERSHEY_ROUNDED_RECT_ONLY
                    if hasattr(cv2, "FONT_HERSHEY_ROUNDED_RECT_ONLY")
                    else cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    (180, 105, 255),
                    2,
                    cv2.LINE_AA,
                )
            else:
                self.has_snapped = True
                self.timer_started_time = None
                self.window.after(10, self.take_snapshot)

        # 3. ใส่ลายน้ำเวลา CCTV เก๋ๆ
        if self.timestamp_on.get():
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(
                frame,
                f"🎀 {now}",
                (20, fh_shape - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 192, 203),
                1,
                cv2.LINE_AA,
            )

        # 4. ระบบฟิลเตอร์ภาพเสริม (รวมที่มีอยู่เดิมและฟิลเตอร์ใหม่)
        mode = self.current_filter.get()
        if mode == "Grayscale":
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            return cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)

        elif mode == "Sepia":
            # ฟิลเตอร์โทนสีน้ำตาลคลาสสิกสไตล์วินเทจ
            kernel = np.array(
                [
                    [0.272, 0.534, 0.131],
                    [0.349, 0.686, 0.168],
                    [0.393, 0.769, 0.189],
                ]
            )
            frame = cv2.transform(frame, kernel)
            frame = np.clip(frame, 0, 255).astype(np.uint8)

        elif mode == "Canny Edge":
            frame = cv2.Canny(frame, 60, 120)
            return cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)

        elif mode == "Blur":
            frame = cv2.GaussianBlur(frame, (25, 25), 0)

        elif mode == "Invert":
            # ฟิลเตอร์สลับสีภาพสไตล์ฟิล์มเนกาทีฟ
            frame = cv2.bitwise_not(frame)

        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def update_frame(self):
        """ดึงภาพจากกล้องมาแสดงต่อเนื่อง"""
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            self.latest_frame = frame.copy()

            processed_rgb = self.process_image(frame)

            pil_image = Image.fromarray(processed_rgb)
            imgtk = ImageTk.PhotoImage(image=pil_image)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

        self.window.after(16, self.update_frame)

    def take_snapshot(self):
        """ถ่ายรูปและบันทึกไฟล์ภาพดิบ"""
        if hasattr(self, "latest_frame"):
            filename = datetime.now().strftime("PINKY_%Y%m%d_%H%M%S.png")
            cv2.imwrite(filename, self.latest_frame)
            messagebox.showinfo(
                "Saved!", f"🎀 บันทึกรูปภาพแสนสวยสำเร็จ: {filename}"
            )

    def quit_app(self):
        """ปิดโปรแกรมและคืนค่ากล้อง"""
        if self.cap.isOpened():
            self.cap.release()
        self.window.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = MinimalCameraApp(root)
    root.protocol("WM_DELETE_WINDOW", app.quit_app)
    root.mainloop()