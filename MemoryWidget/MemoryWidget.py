#!/usr/bin/env python3
import sys
import psutil
import math
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer, Qt, QPoint

class SystemUsageWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('System Usage')
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background-color: black; border-radius: 10px;")
        self.setWindowOpacity(0.8)
        
        main_layout = QVBoxLayout()
        
        self.memory_label = QLabel('Memory Usage: ', self)
        self.cpu_label = QLabel('CPU Usage: ', self)
        self.temperature_label = QLabel('CPU Temperature: ', self)
        
        self.memory_label.setStyleSheet("color: white; font-size: 14px;")
        self.cpu_label.setStyleSheet("color: white; font-size: 14px;")
        self.temperature_label.setStyleSheet("color: white; font-size: 14px;")
        
        main_layout.addWidget(self.memory_label)
        main_layout.addWidget(self.cpu_label)
        main_layout.addWidget(self.temperature_label)
        
        self.setLayout(main_layout)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_system_usage)
        self.timer.start(1000)
        
        self.update_system_usage()
        self.oldPos = self.pos()
        
    def update_system_usage(self):
        memory_info = psutil.virtual_memory()
        cpu_usage = psutil.cpu_percent()
        
        # CPU temperature retrieval - specific to Linux, may need additional configuration
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temperature = f.readline().strip()
                temperature = int(temperature) / 1000 
        except FileNotFoundError:
            temperature = 'N/A'
        
        memory_text = (
            f"Memory:\n"
            f"Total: {self.convert_size(memory_info.total)}\n"
            f"Available: {self.convert_size(memory_info.available)}\n"
            f"Used: {self.convert_size(memory_info.used)}\n"
            f"Percentage: {memory_info.percent}%"
        )
        
        cpu_text = f"CPU Usage: {cpu_usage}%"
        temperature_text = f"CPU Temperature: {temperature}°C"
        
        self.memory_label.setText(memory_text)
        self.cpu_label.setText(cpu_text)
        self.temperature_label.setText(temperature_text)
        
    def convert_size(self, size_bytes):
        if size_bytes == 0:
            return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_name[i]}"

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.oldPos = event.globalPos()
        elif event.button() == Qt.RightButton:
            self.showContextMenu(event.globalPos())
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            delta = QPoint(event.globalPos() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()
    
    def showContextMenu(self, pos):
        menu = QMenu(self)
        close_action = menu.addAction("Close")
        close_action.triggered.connect(self.close)
        
        toggle_top_action = menu.addAction("Toggle Always On Top")
        toggle_top_action.setCheckable(True)
        toggle_top_action.setChecked(self.windowFlags() & Qt.WindowStaysOnTopHint)
        toggle_top_action.triggered.connect(self.toggle_always_on_top)
        
        menu.setStyleSheet("""
            QMenu { 
                background-color: black; 
            }
            QMenu::item { 
                color: grey; 
            }
            QMenu::item:selected { 
                color: white; 
                background-color: #555555; 
            }
        """)
        
        menu.exec_(pos)
        
    def toggle_always_on_top(self):
        if self.windowFlags() & Qt.WindowStaysOnTopHint:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.show()
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    ex = SystemUsageWidget()
    ex.show()
    sys.exit(app.exec_())

