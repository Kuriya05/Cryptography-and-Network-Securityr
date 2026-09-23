import sys
import random
import math
import numpy as np
from PyQt6.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, 
                             QHBoxLayout, QSlider, QLabel, QComboBox, QGroupBox, QLineEdit)
from PyQt6.QtCore import QTimer, Qt, QThread
from PyQt6.QtGui import QPainter, QColor, QFont

# ดึง Windows API มาใช้เพื่อสั่งฝนตกบนวอลเปเปอร์ (ใช้ได้บน Windows เท่านั้น)
if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes
else:
    ctypes = None

try:
    import pygame
    pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
except ImportError:
    pygame = None

class SciFiSoundWorker(QThread):
    def __init__(self):
        super().__init__()
        self.is_playing = False
        self.volume_level = 30  

    def run(self):
        self.is_playing = True
        sample_rate = 22050
        while self.is_playing:
            if pygame and pygame.mixer.get_init():
                duration = 0.08  
                num_samples = int(sample_rate * duration)
                noise = np.random.uniform(-0.15, 0.15, num_samples)
                t = np.linspace(0, duration, num_samples, endpoint=False)
                freq = random.uniform(70, 140)
                drone = 0.45 * np.sin(2 * np.pi * freq * t)
                click_mask = np.random.choice([0, 1], size=num_samples, p=[0.993, 0.007])
                clicks = click_mask * np.sin(2 * np.pi * 800 * t) * 0.4
                combined = noise + drone + clicks
                vol_factor = (self.volume_level / 100.0) * 0.35
                combined = combined * vol_factor
                combined = np.clip(combined, -1.0, 1.0)
                audio_buffer = (combined * 32767).astype(np.int16)
                sound = pygame.mixer.Sound(buffer=audio_buffer)
                sound.play()
                self.msleep(int(duration * 1000) - 5)
            else:
                self.msleep(100)

    def stop(self):
        self.is_playing = False
        self.wait()

class MatrixChar:
    def __init__(self, char):
        self.char = char

class MatrixColumn:
    def __init__(self, x, font_size, window_height, speed_mult=1.0):
        self.x = x
        self.font_size = font_size
        self.window_height = window_height
        self.speed_mult = speed_mult
        self.reset()
        
    def reset(self):
        self.y = random.randint(-800, 0)
        self.speed = random.randint(3, 7) * self.speed_mult
        self.chars = []
        self.length = random.randint(10, 35)
        
        char_pool = [chr(i) for i in range(12449, 12539)] + [chr(i) for i in range(48, 58)] + [chr(i) for i in range(65, 91)]
        self.col_rainbow_color = QColor(random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
        
        for _ in range(self.length):
            self.chars.append(MatrixChar(random.choice(char_pool)))
            
    def update(self, custom_text=""):
        self.y += self.speed
        
        # ถ้้ามีการพิมพ์คำบอกรักแฟน ระบบจะแอบแทรกคำนั้นลงไปในสายฝนแบบเนียนๆ 
        if custom_text and random.random() < 0.25:
            idx = random.randint(0, self.length - 1)
            self.chars[idx].char = random.choice(list(custom_text))
        elif random.random() < 0.05:
            char_pool = [chr(i) for i in range(12449, 12539)] + [chr(i) for i in range(48, 58)] + [chr(i) for i in range(65, 91)]
            idx = random.randint(0, self.length - 1)
            self.chars[idx].char = random.choice(char_pool)
            
        if self.y - (self.length * self.font_size) > self.window_height:
            self.reset()

class MatrixRainWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        self.font_size = 18
        self.fps = 60
        self.bg_opacity = 45 
        self.speed_multiplier = 1.0
        self.current_theme = "Classic Green"
        self.current_font_family = "MS Gothic"
        self.custom_love_text = "" # ข้อความบอกรักเริ่มต้น
        self.is_wallpaper = False  # สถานะโหมดวอลเปเปอร์
        
        self.themes = [
            "Classic Green", "Gold Monarch ✨", "Sunset Orange 🌅", 
            "Pink / White / Blue", "Rainbow Spectrum", "Cyberpunk Blue", 
            "Neon Red", "Sci-Fi Purple"
        ]
        
        self.available_fonts = ["MS Gothic", "Consolas", "Courier New", "Lucida Console"]
        self.columns = []
        self.sound_enabled = False
        self.panel_visible = True  
        
        self.sound_thread = SciFiSoundWorker()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Matrix Wallpaper - Love Edition")
        self.resize(1100, 750)
        self.setStyleSheet("background-color: black;")
        
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.addStretch(1)
        
        # --- CONTROL PANEL ---
        self.control_panel = QGroupBox("SYSTEM CONTROLS")
        self.control_panel.setFixedWidth(260)
        self.control_panel.setStyleSheet("""
            QGroupBox {
                background-color: rgba(10, 10, 10, 230); color: #00FF00;
                border: 2px solid #005500; border-radius: 8px;
                padding-top: 15px; font-family: 'Courier New'; font-weight: bold;
            }
            QLabel { color: #AAA; font-family: 'Courier New'; font-size: 11px; }
        """)
        panel_layout = QVBoxLayout(self.control_panel)
        
        # 🌟 ฟังก์ชันใหม่: ช่องพิมพ์คำบอกรักแฟน
        panel_layout.addWidget(QLabel("💬 LOVE MESSAGE TO FAN:"))
        self.love_input = QLineEdit(self)
        self.love_input.setPlaceholderText("พิมพ์คำบอกรักตรงนี้...")
        self.love_input.setStyleSheet("background-color: #000; color: #FFF; border: 1px solid #00FF00; padding: 4px; font-family: 'Courier New';")
        self.love_input.textChanged.connect(self.update_love_text)
        panel_layout.addWidget(self.love_input)
        
        panel_layout.addSpacing(5)
        
        # 🌟 ฟังก์ชันใหม่: ปุ่มสลับโหมด Wallpaper เต็มจอฝังลึก
        self.wp_btn = QPushButton("🖥️ SET AS WALLPAPER", self)
        self.wp_btn.setStyleSheet("background-color: #002244; color: #00FFFF; border: 2px solid #00FFFF; border-radius: 5px; font-family: 'Courier New'; font-weight: bold; padding: 6px;")
        self.wp_btn.clicked.connect(self.toggle_wallpaper_mode)
        panel_layout.addWidget(self.wp_btn)
        
        panel_layout.addSpacing(5)
        
        # ปุ่มเปิด/ปิดเสียง
        self.audio_btn = QPushButton("🔊 REAL SFX: OFF", self)
        self.audio_btn.setStyleSheet(self.get_btn_style(False))
        self.audio_btn.clicked.connect(self.toggle_sound)
        panel_layout.addWidget(self.audio_btn)
        
        # ปรับระดับเสียง
        panel_layout.addWidget(QLabel("VOLUME LEVEL:"))
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(30)
        self.volume_slider.valueChanged.connect(self.change_volume)
        panel_layout.addWidget(self.volume_slider)
        
        # เลือกสี
        panel_layout.addWidget(QLabel("THEME COLOR:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(self.themes)
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        self.theme_combo.setStyleSheet(self.get_combo_style())
        panel_layout.addWidget(self.theme_combo)
        
        # เลือกฟอนต์
        panel_layout.addWidget(QLabel("MATRIX FONT STYLE:"))
        self.font_combo = QComboBox()
        self.font_combo.addItems(self.available_fonts)
        self.font_combo.currentTextChanged.connect(self.change_font_family)
        self.font_combo.setStyleSheet(self.get_combo_style())
        panel_layout.addWidget(self.font_combo)
        
        # ขนาดฟอนต์ และ ความเร็ว
        panel_layout.addWidget(QLabel("FONT SIZE:"))
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(10, 36)
        self.size_slider.setValue(self.font_size)
        self.size_slider.valueChanged.connect(self.change_font_size)
        panel_layout.addWidget(self.size_slider)
        
        panel_layout.addWidget(QLabel("RAIN SPEED:"))
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(5, 20)
        self.speed_slider.setValue(10)
        self.speed_slider.valueChanged.connect(self.change_speed)
        panel_layout.addWidget(self.speed_slider)
        
        self.main_layout.addWidget(self.control_panel)
        
        # ปุ่ม OPTIONS
        self.toggle_panel_btn = QPushButton("⚙️ OPTIONS", self)
        self.toggle_panel_btn.setFixedWidth(110)
        self.toggle_panel_btn.setStyleSheet("QPushButton { background-color: rgba(0, 20, 0, 180); color: #00FF00; border: 1px solid #00FF00; border-radius: 4px; font-family: 'Courier New'; font-size: 11px; font-weight: bold; padding: 4px; } QPushButton:hover { background-color: #004400; color: #FFF; }")
        self.toggle_panel_btn.clicked.connect(self.toggle_panel_visibility)
        self.toggle_panel_btn.setParent(self)
        self.update_toggle_btn_position()
        
        self.update_font_object()
        self.setup_matrix()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_matrix)
        self.timer.start(1000 // self.fps)
        
    def get_btn_style(self, enabled):
        if enabled: return "QPushButton { background-color: #003300; color: #FFF; border: 2px solid #00FF00; border-radius: 5px; font-family: 'Courier New'; font-weight: bold; padding: 6px; }"
        return "QPushButton { background-color: #110000; color: #FF3333; border: 2px solid #FF3333; border-radius: 5px; font-family: 'Courier New'; font-weight: bold; padding: 6px; }"

    def get_combo_style(self):
        return "QComboBox { background-color: #000; color: #00FF00; border: 1px solid #00FF00; padding: 4px; font-family: 'Courier New'; } QComboBox QAbstractItemView { background-color: #111; color: #00FF00; }"

    def update_love_text(self, text):
        self.custom_love_text = text

    def toggle_wallpaper_mode(self):
        """สั่งเจาะระบบหน้าจอ Windows เพื่อฝังตัวโปรแกรมลงไปด้านหลังสุดแบบ Live Wallpaper"""
        if not ctypes or sys.platform != "win32":
            return
            
        if not self.is_wallpaper:
            # 1. ค้นหาหน้าต่างเบื้องหลังระบบพิกัดจัดการ Wallpaper ของ Windows (Progman)
            progman = ctypes.windll.user32.FindWindowW("Progman", None)
            # ยิงข้อความคำสั่งลับให้ Windows แยก Layer พื้นหลัง (สร้างหน้าต่าง WorkerW ออกมา)
            ctypes.windll.user32.SendMessageTimeoutW(progman, 0x052C, 0, 0, 0x0002, 1000, None)
            
            # 2. ค้นหาหน้าต่าง WorkerW ที่พึ่งถูกสร้างแยกออกมา
            def foreach_window(hwnd, lParam):
                shell_dll = ctypes.windll.user32.FindWindowExW(hwnd, 0, "SHELLDLL_DefView", None)
                if shell_dll:
                    # หน้าต่าง WorkerW ที่อยู่ถัดไปคือหน้าต่างที่เราต้องการใช้ฝัง
                    lParam[0] = ctypes.windll.user32.FindWindowExW(0, hwnd, "WorkerW", None)
                return True
                
            workerw = [0]
            WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
            ctypes.windll.user32.EnumWindows(WNDENUMPROC(foreach_window), ctypes.byref(wintypes.LPARAM(id(workerw))))
            
            target_hwnd = workerw[0] if workerw[0] else progman
            
            # 3. จับหน้าต่างโปรแกรมเรายัดลงไปเป็นลูกของหน้าต่างระบบ Wallpaper ของ Windows
            my_hwnd = int(self.winId())
            ctypes.windll.user32.SetParent(my_hwnd, target_hwnd)
            
            # 4. ขยายขนาดให้เต็มขนาดจอภาพหลักของคุณทันที
            screen = QApplication.primaryScreen().geometry()
            self.setGeometry(screen)
            self.setWindowFlags(Qt.WindowFlags.FramelessWindowHint)
            self.showFullScreen()
            
            self.wp_btn.setText("🪟 RETURN TO WINDOW")
            self.wp_btn.setStyleSheet("background-color: #440000; color: #FF0000; border: 2px solid #FF0000; border-radius: 5px; font-family: 'Courier New'; font-weight: bold; padding: 6px;")
            self.is_wallpaper = True
        else:
            # คืนค่าสลับกลับเป็นหน้าต่างแบบปกติเพื่อยกเลิกการฝังตัว
            my_hwnd = int(self.winId())
            ctypes.windll.user32.SetParent(my_hwnd, 0)
            self.setWindowFlags(Qt.WindowType.Widget)
            self.showNormal()
            self.resize(1100, 750)
            self.wp_btn.setText("🖥️ SET AS WALLPAPER")
            self.wp_btn.setStyleSheet("background-color: #002244; color: #00FFFF; border: 2px solid #00FFFF; border-radius: 5px; font-family: 'Courier New'; font-weight: bold; padding: 6px;")
            self.is_wallpaper = False
            
        self.setup_matrix()

    def update_font_object(self):
        self.matrix_font = QFont(self.current_font_family, self.font_size)
        self.matrix_font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)

    def setup_matrix(self):
        self.columns.clear()
        num_columns = self.width() // max(6, (self.font_size - 2))
        for i in range(num_columns):
            x = i * (self.font_size - 2)
            self.columns.append(MatrixColumn(x, self.font_size, self.height(), self.speed_multiplier))
            
    def update_toggle_btn_position(self):
        margin = 15
        btn_width = self.toggle_panel_btn.width()
        if self.panel_visible:
            self.toggle_panel_btn.move(self.width() - 260 - margin, margin)
        else:
            self.toggle_panel_btn.move(self.width() - btn_width - margin, margin)

    def resizeEvent(self, event):
        self.setup_matrix()
        self.update_toggle_btn_position()
        super().resizeEvent(event)
        
    def update_matrix(self):
        for col in self.columns:
            col.update(self.custom_love_text)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setFont(self.matrix_font)
        painter.fillRect(self.rect(), QColor(0, 0, 0, self.bg_opacity))
        
        for col in self.columns:
            for i in range(col.length):
                char_y = col.y - (i * col.font_size)
                if char_y < -col.font_size or char_y > self.height() + col.font_size:
                    continue
                
                if i == 0:
                    color = QColor(255, 255, 255) 
                else:
                    alpha = max(10, int(255 * (1.0 - (i / col.length))))
                    
                    if self.current_theme == "Classic Green": color = QColor(0, 200, 50, alpha)
                    elif self.current_theme == "Cyberpunk Blue": color = QColor(0, 150, 255, alpha)
                    elif self.current_theme == "Neon Red": color = QColor(255, 30, 30, alpha)
                    elif self.current_theme == "Sci-Fi Purple": color = QColor(180, 30, 255, alpha)
                    elif self.current_theme == "Gold Monarch ✨": color = QColor(255, 215, 0, alpha)
                    elif self.current_theme == "Sunset Orange 🌅": color = QColor(255, 90, 0, alpha)
                    elif self.current_theme == "Pink / White / Blue":
                        rem = i % 3
                        color = QColor(255, 105, 180, alpha) if rem == 0 else (QColor(240, 240, 240, alpha) if rem == 1 else QColor(91, 206, 250, alpha))
                    elif self.current_theme == "Rainbow Spectrum":
                        color = QColor(col.col_rainbow_color.red(), col.col_rainbow_color.green(), col.col_rainbow_color.blue(), alpha)
                
                painter.setPen(color)
                painter.drawText(col.x, int(char_y), col.chars[i].char)

    def toggle_panel_visibility(self):
        if self.panel_visible:
            self.control_panel.hide()
            self.panel_visible = False
            self.toggle_panel_btn.setText("⚙️ OPTIONS")
        else:
            self.control_panel.show()
            self.panel_visible = True
            self.toggle_panel_btn.setText("❌ CLOSE")
        self.update_toggle_btn_position()
        self.setup_matrix()

    def toggle_sound(self):
        if not self.sound_enabled:
            self.sound_thread = SciFiSoundWorker()
            self.sound_thread.volume_level = self.volume_slider.value()
            self.sound_thread.start()
            self.audio_btn.setText("🔊 REAL SFX: ON")
            self.audio_btn.setStyleSheet(self.get_btn_style(True))
            self.sound_enabled = True
        else:
            self.sound_thread.stop()
            self.audio_btn.setText("🔊 REAL SFX: OFF")
            self.audio_btn.setStyleSheet(self.get_btn_style(False))
            self.sound_enabled = False

    def change_volume(self, value): self.sound_thread.volume_level = value
    def change_theme(self, text): self.current_theme = text
    def change_font_family(self, text):
        self.current_font_family = text
        self.update_font_object()
        self.setup_matrix()
    def change_font_size(self, value):
        self.font_size = value
        self.update_font_object()
        self.setup_matrix()
    def change_speed(self, value):
        self.speed_multiplier = value / 10.0
        for col in self.columns: col.speed = random.randint(3, 7) * self.speed_multiplier

    def closeEvent(self, event):
        self.sound_thread.stop()
        if pygame: pygame.mixer.quit()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    matrix = MatrixRainWidget()
    matrix.show()
    sys.exit(app.exec())