import sys
import random
import math
import numpy as np
from PyQt6.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, 
                             QHBoxLayout, QSlider, QLabel, QComboBox, QGroupBox)
from PyQt6.QtCore import QTimer, Qt, QThread, QDateTime
from PyQt6.QtGui import QPainter, QColor, QFont, QKeyEvent

# ใช้ pygame สำหรับการสังเคราะห์เสียงแบบ Stream ดิจิทัลคุณภาพสูง
try:
    import pygame
    pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
    PYGAME_AVAILABLE = True
except ImportError:
    pygame = None
    PYGAME_AVAILABLE = False

class SciFiSoundWorker(QThread):
    """คลาสสังเคราะห์เอฟเฟกต์เสียงฝนดิจิทัลแบบสมจริง (Matrix Sci-Fi Digital Rain Sound)"""
    def __init__(self):
        super().__init__()
        self.is_playing = False
        self.volume_level = 50  # ปรับค่าเริ่มต้นเพิ่มเป็น 50%

    def run(self):
        self.is_playing = True
        sample_rate = 22050
        
        while self.is_playing:
            if pygame and pygame.mixer.get_init():
                duration = 0.08  
                num_samples = int(sample_rate * duration)
                
                # 1. สร้างเสียง White Noise (เสียงซู่ซ่าของฝนดิจิทัล)
                noise = np.random.uniform(-0.25, 0.25, num_samples)
                
                # 2. สร้างคลื่นความถี่ต่ำลึกขยับไปมา (Sci-Fi Deep Drone)
                t = np.linspace(0, duration, num_samples, endpoint=False)
                freq = random.uniform(80, 160)
                drone = 0.55 * np.sin(2 * np.pi * freq * t)
                
                # 3. สร้างคลื่นคลิกสั้นๆ (เสียงโมเด็ม/ตัวอักษรเปลี่ยน)
                click_mask = np.random.choice([0, 1], size=num_samples, p=[0.985, 0.015])
                clicks = click_mask * np.sin(2 * np.pi * 900 * t) * 0.5
                
                # ผสมสัญญาณทั้งหมดเข้าด้วยกัน
                combined = noise + drone + clicks
                
                # [BOOST] ขยายกำลังสัญญาณตรงนี้ให้เสียงดังขึ้นอย่างชัดเจน
                vol_factor = (self.volume_level / 100.0) * 0.85
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
        self.speed = random.randint(4, 9) * self.speed_mult
        self.chars = []
        self.length = random.randint(12, 40)
        
        char_pool = [chr(i) for i in range(12449, 12539)] + [chr(i) for i in range(48, 58)] + [chr(i) for i in range(65, 91)]
        self.col_rainbow_color = QColor(random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
        
        for _ in range(self.length):
            self.chars.append(MatrixChar(random.choice(char_pool)))
            
    def update(self):
        self.y += self.speed
        if random.random() < 0.07:
            char_pool = [chr(i) for i in range(12449, 12539)] + [chr(i) for i in range(48, 58)] + [chr(i) for i in range(65, 91)]
            idx = random.randint(0, self.length - 1)
            self.chars[idx].char = random.choice(char_pool)
            
        if self.y - (self.length * self.font_size) > self.window_height:
            self.reset()

class MatrixRainWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        self.font_size = 16
        self.fps = 60
        self.bg_opacity = 35  
        self.speed_multiplier = 1.2
        self.current_theme = "Classic Green"
        self.current_font_family = "MS Gothic"
        
        # ระบบ Logs แฮกเกอร์
        self.hacker_logs = ["INITIALIZING OVERRIDE ROUTINE..."]
        if not PYGAME_AVAILABLE:
            self.hacker_logs.append("[AUDIO ERROR: PYGAME MIXER NOT FOUND]")
            
        self.hacker_pool = [
            "CONNECTING TO PROXY CENTRAL...", "BYPASSING FIREWALL STACK...", 
            "INJECTING CORE PAYLOAD...", "EXTRACTING ENCRYPTED TOKENS...", 
            "DECRYPTING SHA-256 SALT...", "ACCESS GRANTED TO NODE #83B9",
            "OVERCLOCKING CPU MAINFRAME...", "CLEARING SYSTEM LOGS...", 
            "DOWNLOAD RATE: 42.8 GB/S", "WARNING: TRACE DETECTED - REROUTING"
        ]
        self.glitch_active = False
        self.glitch_timer = 0
        
        self.themes = [
            "Classic Green", "Cyberpunk Blue", "Neon Red", "Sci-Fi Purple",
            "Gold Monarch ✨", "Sunset Orange 🌅", "Pink / White / Blue", "Rainbow Spectrum"
        ]
        
        self.available_fonts = ["MS Gothic", "Consolas", "Courier New", "Lucida Console"]
        self.columns = []
        self.sound_enabled = False
        self.panel_visible = False  
        
        self.sound_thread = SciFiSoundWorker()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("⚡ STEALTH MATRIX CORE - PRESS [F2] FOR OPTIONS ⚡")
        self.resize(1200, 800)
        self.setStyleSheet("background-color: black;")
        
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.addStretch(1)
        
        # --- แผงควบคุมดีไซน์ Cyberpunk (เรียกใช้งานผ่าน F2) ---
        self.control_panel = QGroupBox("CORE CONTROLS [F2]")
        self.control_panel.setFixedWidth(280)
        self.control_panel.setStyleSheet("""
            QGroupBox {
                background-color: rgba(5, 15, 5, 220);
                color: #00FF66;
                border: 2px solid #00FF66;
                border-radius: 12px;
                padding-top: 25px;
                font-family: 'Consolas';
                font-weight: bold;
                font-size: 13px;
            }
            QLabel {
                color: #88FF88;
                font-family: 'Consolas';
                font-size: 11px;
                margin-top: 5px;
            }
        """)
        panel_layout = QVBoxLayout(self.control_panel)
        
        # 1. ปุ่มเปิด/ปิดเสียง
        self.audio_btn = QPushButton("🔊 REAL SFX: OFF", self)
        self.audio_btn.setStyleSheet(self.get_btn_style(False))
        self.audio_btn.clicked.connect(self.toggle_sound)
        panel_layout.addWidget(self.audio_btn)
        
        # 2. แถบปรับระดับเสียง
        panel_layout.addWidget(QLabel("SYS_VOLUME GENERATOR:"))
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)  # เริ่มที่ 50
        self.volume_slider.valueChanged.connect(self.change_volume)
        self.volume_slider.setStyleSheet(self.get_slider_style())
        panel_layout.addWidget(self.volume_slider)
        
        panel_layout.addSpacing(10)
        
        # 3. เลือกธีมสี
        panel_layout.addWidget(QLabel("MATRIX SPECTRUM THEME:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(self.themes)
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        self.theme_combo.setStyleSheet(self.get_combo_style())
        panel_layout.addWidget(self.theme_combo)
        
        panel_layout.addSpacing(10)
        
        # 4. เลือกฟอนต์
        panel_layout.addWidget(QLabel("KERNEL FONT TYPEFACE:"))
        self.font_combo = QComboBox()
        self.font_combo.addItems(self.available_fonts)
        self.font_combo.currentTextChanged.connect(self.change_font_family)
        self.font_combo.setStyleSheet(self.get_combo_style())
        panel_layout.addWidget(self.font_combo)
        
        panel_layout.addSpacing(10)
        
        # 5. ปรับขนาดฟอนต์
        panel_layout.addWidget(QLabel("MATRIX STREAM SIZE:"))
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(10, 36)
        self.size_slider.setValue(self.font_size)
        self.size_slider.valueChanged.connect(self.change_font_size)
        self.size_slider.setStyleSheet(self.get_slider_style())
        panel_layout.addWidget(self.size_slider)
        
        # 6. ปรับความเร็ว
        panel_layout.addWidget(QLabel("VELOCITY SECTOR SPEED:"))
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(5, 25)
        self.speed_slider.setValue(12)
        self.speed_slider.valueChanged.connect(self.change_speed)
        self.speed_slider.setStyleSheet(self.get_slider_style())
        panel_layout.addWidget(self.speed_slider)
        
        self.main_layout.addWidget(self.control_panel)
        self.control_panel.hide() 
        
        self.update_font_object()
        self.setup_matrix()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_system)
        self.timer.start(1000 // self.fps)
        
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_F2:
            self.trigger_glitch_effect()
            self.toggle_panel_visibility()
        else:
            super().keyPressEvent(event)

    def trigger_glitch_effect(self):
        self.glitch_active = True
        self.glitch_timer = 6  

    def get_btn_style(self, enabled):
        if enabled:
            return "QPushButton { background-color: #004411; color: #FFF; border: 2px solid #00FF66; border-radius: 6px; font-family: 'Consolas'; font-weight: bold; padding: 8px; }"
        return "QPushButton { background-color: #220000; color: #FF3333; border: 2px solid #FF3333; border-radius: 6px; font-family: 'Consolas'; font-weight: bold; padding: 8px; }"

    def get_combo_style(self):
        return "QComboBox { background-color: #000; color: #00FF66; border: 1px solid #00FF66; padding: 5px; border-radius: 4px; font-family: 'Consolas'; } QComboBox QAbstractItemView { background-color: #050505; color: #00FF66; selection-background-color: #004411; }"

    def get_slider_style(self):
        return "QSlider::groove:horizontal { border: 1px solid #004411; height: 6px; background: #000; border-radius: 3px; } QSlider::handle:horizontal { background: #00FF66; width: 14px; margin: -4px 0; border-radius: 7px; }"

    def update_font_object(self):
        self.matrix_font = QFont(self.current_font_family, self.font_size)
        self.matrix_font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)

    def setup_matrix(self):
        self.columns.clear()
        num_columns = self.width() // max(6, (self.font_size - 2))
        for i in range(num_columns):
            x = i * (self.font_size - 2)
            self.columns.append(MatrixColumn(x, self.font_size, self.height(), self.speed_multiplier))
            
    def resizeEvent(self, event):
        self.setup_matrix()
        super().resizeEvent(event)
        
    def update_system(self):
        for col in self.columns:
            col.update()
            
        if random.random() < 0.03:
            self.hacker_logs.append(f"[{QDateTime.currentDateTime().toString('hh:mm:ss')}] {random.choice(self.hacker_pool)}")
            if len(self.hacker_logs) > 6:
                self.hacker_logs.pop(0)
                
        if self.glitch_active:
            self.glitch_timer -= 1
            if self.glitch_timer <= 0:
                self.glitch_active = False
        elif random.random() < 0.003: 
            self.trigger_glitch_effect()
            
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setFont(self.matrix_font)
        
        if self.glitch_active and random.random() < 0.5:
            painter.fillRect(self.rect(), QColor(0, 40, 10, 80))
        else:
            painter.fillRect(self.rect(), QColor(0, 0, 0, self.bg_opacity))
        
        for col in self.columns:
            glitch_offset = random.randint(-20, 20) if (self.glitch_active and random.random() < 0.4) else 0
            
            for i in range(col.length):
                char_y = col.y - (i * col.font_size)
                
                if char_y < -col.font_size or char_y > self.height() + col.font_size:
                    continue
                
                if i == 0:
                    color = QColor(255, 255, 255) 
                else:
                    alpha = int(255 * (1.0 - (i / col.length)))
                    alpha = max(15, alpha)
                    
                    if self.current_theme == "Classic Green":
                        color = QColor(0, 255, 102, alpha)
                    elif self.current_theme == "Cyberpunk Blue":
                        color = QColor(0, 180, 255, alpha)
                    elif self.current_theme == "Neon Red":
                        color = QColor(255, 40, 40, alpha)
                    elif self.current_theme == "Sci-Fi Purple":
                        color = QColor(200, 50, 255, alpha)
                    elif self.current_theme == "Gold Monarch ✨":
                        color = QColor(255, 215, 0, alpha)
                    elif self.current_theme == "Sunset Orange 🌅":
                        color = QColor(255, 95, 0, alpha)
                    elif self.current_theme == "Pink / White / Blue":
                        rem = i % 3
                        if rem == 0: color = QColor(255, 105, 180, alpha) 
                        elif rem == 1: color = QColor(240, 240, 240, alpha) 
                        else: color = QColor(91, 206, 250, alpha)  
                    elif self.current_theme == "Rainbow Spectrum":
                        color = QColor(col.col_rainbow_color.red(), col.col_rainbow_color.green(), col.col_rainbow_color.blue(), alpha)
                
                painter.setPen(color)
                painter.drawText(col.x + glitch_offset, int(char_y), col.chars[i].char)

        if self.panel_visible:
            painter.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
            
            # วาด Fake Terminal Logs
            rect_width, rect_height = 380, 140
            painter.fillRect(20, self.height() - rect_height - 20, rect_width, rect_height, QColor(0, 10, 0, 190))
            painter.setPen(QColor(0, 255, 102, 220))
            painter.drawRect(20, self.height() - rect_height - 20, rect_width, rect_height)
            
            painter.drawText(35, self.height() - rect_height - 5, "⚡ LIVE BREACH CONSOLE LOG ⚡")
            for idx, log in enumerate(self.hacker_logs):
                if "WARNING" in log or "ERROR" in log:
                    painter.setPen(QColor(255, 40, 40))
                else:
                    painter.setPen(QColor(0, 230, 90))
                painter.drawText(30, self.height() - rect_height + 25 + (idx * 18), log)

            # วาดนาฬิกา HUD
            time_str = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss.zzz")
            cpu_fake = random.randint(70, 92) if random.random() < 0.1 else 78
            ram_fake = random.randint(54, 57)
            
            hud_text = f"SYS_TIME: {time_str}\nCPU_LOAD: {cpu_fake}%  |  RAM_UTIL: {ram_fake}%  |  OVERRIDE: ACTIVE"
            painter.setPen(QColor(0, 255, 102, 240))
            
            text_x = self.width() - 480
            painter.drawText(int(text_x), 35, hud_text)

    def toggle_panel_visibility(self):
        if self.panel_visible:
            self.control_panel.hide()
            self.panel_visible = False
        else:
            self.control_panel.show()
            self.panel_visible = True
            
        self.setup_matrix()

    def toggle_sound(self):
        if not self.sound_enabled:
            if PYGAME_AVAILABLE:
                self.sound_thread = SciFiSoundWorker()
                self.sound_thread.volume_level = self.volume_slider.value()
                self.sound_thread.start()
                self.audio_btn.setText("🔊 REAL SFX: ON")
                self.audio_btn.setStyleSheet(self.get_btn_style(True))
                self.sound_enabled = True
            else:
                self.audio_btn.setText("❌ NO AUDIO LIB")
        else:
            self.sound_thread.stop()
            self.audio_btn.setText("🔊 REAL SFX: OFF")
            self.audio_btn.setStyleSheet(self.get_btn_style(False))
            self.sound_enabled = False

    def change_volume(self, value):
        self.sound_thread.volume_level = value

    def change_theme(self, text):
        self.current_theme = text
        self.trigger_glitch_effect()
        
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
        for col in self.columns:
            col.speed = random.randint(4, 9) * self.speed_multiplier

    def closeEvent(self, event):
        self.sound_thread.stop()
        if pygame:
            pygame.mixer.quit()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    matrix = MatrixRainWidget()
    matrix.show()
    sys.exit(app.exec())