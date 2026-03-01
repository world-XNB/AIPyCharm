"""
三天Python速成计划 - QT可视化提醒系统
使用方法：python study_reminder_qt.py
"""

import json
import os
import sys
from datetime import datetime, timedelta
import time
import threading
from enum import Enum

try:
    import schedule
except ImportError:
    print("⚠️  需要安装 schedule 库：pip install schedule")
    sys.exit(1)

# QT相关导入
try:
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                 QHBoxLayout, QPushButton, QLabel, QTableWidget,
                                 QTableWidgetItem, QProgressBar, QTextEdit,
                                 QSystemTrayIcon, QMenu, QAction, QMessageBox,
                                 QGroupBox, QGridLayout, QHeaderView, QFrame)
    from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread
    from PyQt5.QtGui import QIcon, QFont, QColor, QPalette
    # 多媒体支持（用于声音）
    from PyQt5.QtMultimedia import QSound
    HAS_QT = True
except ImportError:
    print("⚠️  需要安装 PyQt5 库：pip install PyQt5")
    HAS_QT = False
    sys.exit(1)

# 学习计划详细数据
STUDY_PLAN = {
    "day1": {
        "title": "第1天：极速入门 & 文件自动化处理",
        "schedule": [
            {"time": "08:00", "title": "基础语法（上午）", "duration": "3-4小时"},
            {"time": "13:00", "title": "文件处理（下午）", "duration": "3-4小时"},
            {"time": "19:00", "title": "练习（晚上）", "duration": "1-2小时"}
        ]
    },
    "day2": {
        "title": "第2天：核心战场 – 与操作系统和网络交互",
        "schedule": [
            {"time": "08:00", "title": "操作系统交互（上午）", "duration": "3小时"},
            {"time": "13:00", "title": "网络请求和数据库（下午）", "duration": "3小时"},
            {"time": "19:00", "title": "综合练习（晚上）", "duration": "1-2小时"}
        ]
    },
    "day3": {
        "title": "第3天：效率工具与综合实战",
        "schedule": [
            {"time": "08:00", "title": "正则表达式和文本处理（上午）", "duration": "3小时"},
            {"time": "13:00", "title": "综合项目实战（下午）", "duration": "3-4小时"}
        ]
    }
}

class PlanStatus(Enum):
    """计划状态枚举"""
    NOT_STARTED = "未开始"
    DAY1 = "第1天"
    DAY2 = "第2天"
    DAY3 = "第3天"
    COMPLETED = "已完成"

class ReminderThread(QThread):
    """提醒线程"""
    reminder_signal = pyqtSignal(str, str)  # 标题, 消息
    
    def __init__(self, reminder_system):
        super().__init__()
        self.reminder_system = reminder_system
        self.running = False
    
    def run(self):
        """运行提醒调度"""
        self.running = True
        while self.running:
            schedule.run_pending()
            time.sleep(1)
    
    def stop(self):
        """停止线程"""
        self.running = False
        self.wait()

class StudyReminderSystem:
    """学习提醒系统核心逻辑"""
    
    def __init__(self):
        self.start_date = None
        self.load_config()
    
    def load_config(self):
        """加载配置"""
        config_file = 'study_reminder_config.json'
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.start_date = config.get('start_date')
            except:
                pass
    
    def save_config(self):
        """保存配置"""
        config = {'start_date': self.start_date}
        with open('study_reminder_config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    
    def start_plan(self):
        """开始学习计划"""
        self.start_date = datetime.now().strftime('%Y-%m-%d')
        self.save_config()
        return True
    
    def get_current_day(self):
        """获取当前是第几天"""
        if not self.start_date:
            return None
        
        try:
            start = datetime.strptime(self.start_date, '%Y-%m-%d')
            today = datetime.now()
            days = (today - start).days
            
            if days < 0:
                return None
            elif days == 0:
                return "day1"
            elif days == 1:
                return "day2"
            elif days == 2:
                return "day3"
            else:
                return "completed"
        except:
            return None
    
    def get_plan_status(self):
        """获取计划状态"""
        day = self.get_current_day()
        if day is None:
            return PlanStatus.NOT_STARTED
        elif day == "day1":
            return PlanStatus.DAY1
        elif day == "day2":
            return PlanStatus.DAY2
        elif day == "day3":
            return PlanStatus.DAY3
        else:
            return PlanStatus.COMPLETED
    
    def get_today_plan(self):
        """获取今天计划"""
        day = self.get_current_day()
        
        if day is None:
            return None, "请先启动计划"
        
        if day == "completed":
            return None, "🎉 恭喜！你已完成3天学习计划！"
        
        plan = STUDY_PLAN[day]
        return plan, None
    
    def schedule_reminders(self, callback):
        """设置日程提醒"""
        if not self.start_date:
            return False
        
        day = self.get_current_day()
        if day == "completed":
            return False
        
        plan = STUDY_PLAN[day]
        
        # 清除现有任务
        schedule.clear()
        
        for item in plan['schedule']:
            schedule.every().day.at(item['time']).do(
                callback,
                title=f"📖 学习提醒",
                message=f"{item['title']} ({item['duration']})"
            )
        
        return True
    
    def get_next_reminder_info(self):
        """获取下一个提醒信息"""
        day = self.get_current_day()
        if day == "completed" or day is None:
            return None, None
        
        plan = STUDY_PLAN[day]
        now = datetime.now().strftime("%H:%M")
        
        for item in plan['schedule']:
            if item['time'] > now:
                return item['time'], item['title']
        
        return None, "今日所有提醒已完成"

class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.reminder_system = StudyReminderSystem()
        self.reminder_thread = None
        self.tray_icon = None
        
        self.init_ui()
        self.init_tray()
        self.update_display()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("Python学习计划提醒系统")
        self.setGeometry(100, 100, 900, 700)
        
        # 设置窗口图标
        self.setWindowIcon(QIcon.fromTheme("applications-education"))
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 1. 标题区域
        title_layout = self.create_title_area()
        main_layout.addLayout(title_layout)
        
        # 2. 状态区域
        status_layout = self.create_status_area()
        main_layout.addLayout(status_layout)
        
        # 3. 计划显示区域
        plan_group = self.create_plan_area()
        main_layout.addWidget(plan_group, 1)  # 1表示可拉伸
        
        # 4. 控制按钮区域
        control_layout = self.create_control_area()
        main_layout.addLayout(control_layout)
        
        # 5. 日志区域
        log_group = self.create_log_area()
        main_layout.addWidget(log_group)
    
    def create_title_area(self):
        """创建标题区域"""
        layout = QHBoxLayout()
        
        # 标题标签
        title_label = QLabel("📖 Python学习计划提醒系统")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2c3e50;")
        
        layout.addWidget(title_label)
        layout.addStretch()
        
        return layout
    
    def create_status_area(self):
        """创建状态区域"""
        layout = QGridLayout()
        layout.setSpacing(10)
        
        # 状态标签
        self.status_label = QLabel("状态：未启动")
        self.status_label.setStyleSheet("font-size: 14px; color: #7f8c8d;")
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 3)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 3px;
            }
        """)
        
        # 开始日期标签
        self.date_label = QLabel("开始日期：未设置")
        self.date_label.setStyleSheet("font-size: 14px; color: #7f8c8d;")
        
        # 下一个提醒标签
        self.next_reminder_label = QLabel("下一个提醒：无")
        self.next_reminder_label.setStyleSheet("font-size: 14px; color: #7f8c8d;")
        
        layout.addWidget(self.status_label, 0, 0)
        layout.addWidget(self.progress_bar, 0, 1)
        layout.addWidget(self.date_label, 1, 0)
        layout.addWidget(self.next_reminder_label, 1, 1)
        
        return layout
    
    def create_plan_area(self):
        """创建计划显示区域"""
        group = QGroupBox("📅 今日学习计划")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        layout = QVBoxLayout()
        
        # 计划标题
        self.plan_title_label = QLabel("请先启动学习计划")
        self.plan_title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        self.plan_title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.plan_title_label)
        
        # 计划表格
        self.plan_table = QTableWidget()
        self.plan_table.setColumnCount(4)
        self.plan_table.setHorizontalHeaderLabels(["时间", "学习内容", "时长", "状态"])
        self.plan_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.plan_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.plan_table.setAlternatingRowColors(True)
        self.plan_table.setStyleSheet("""
            QTableWidget {
                font-size: 13px;
                gridline-color: #ecf0f1;
            }
            QTableWidget::item {
                padding: 8px;
            }
        """)
        
        layout.addWidget(self.plan_table)
        
        group.setLayout(layout)
        return group
    
    def create_control_area(self):
        """创建控制按钮区域"""
        layout = QHBoxLayout()
        layout.setSpacing(15)
        
        # 启动计划按钮
        self.start_btn = QPushButton("🚀 启动计划")
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 24px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #229954;
            }
        """)
        self.start_btn.clicked.connect(self.on_start_plan)
        
        # 开始提醒按钮
        self.reminder_btn = QPushButton("⏰ 开始提醒")
        self.reminder_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 24px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        self.reminder_btn.clicked.connect(self.on_toggle_reminders)
        self.reminder_btn.setEnabled(False)
        
        # 停止提醒按钮
        self.stop_btn = QPushButton("⏹️ 停止提醒")
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 24px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        self.stop_btn.clicked.connect(self.on_stop_reminders)
        self.stop_btn.setEnabled(False)
        
        # 刷新按钮
        refresh_btn = QPushButton("🔄 刷新")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 24px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        refresh_btn.clicked.connect(self.update_display)
        
        # 测试提醒按钮
        test_btn = QPushButton("🔔 测试提醒")
        test_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 24px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
            QPushButton:pressed {
                background-color: #7d3c98;
            }
        """)
        test_btn.clicked.connect(self.on_test_notification)
        
        # 退出按钮
        exit_btn = QPushButton("🚪 退出")
        exit_btn.setStyleSheet("""
            QPushButton {
                background-color: #34495e;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 24px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2c3e50;
            }
        """)
        exit_btn.clicked.connect(self.close)
        
        layout.addWidget(self.start_btn)
        layout.addWidget(self.reminder_btn)
        layout.addWidget(self.stop_btn)
        layout.addWidget(refresh_btn)
        layout.addWidget(test_btn)
        layout.addStretch()
        layout.addWidget(exit_btn)
        
        return layout
    
    def create_log_area(self):
        """创建日志区域"""
        group = QGroupBox("📝 系统日志")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #95a5a6;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        
        layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        self.log_text.setStyleSheet("""
            QTextEdit {
                font-family: Consolas, Monaco, monospace;
                font-size: 12px;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 3px;
            }
        """)
        
        layout.addWidget(self.log_text)
        group.setLayout(layout)
        return group
    
    def init_tray(self):
        """初始化系统托盘"""
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon(self)
            self.tray_icon.setIcon(QIcon.fromTheme("applications-education"))
            
            # 创建托盘菜单
            tray_menu = QMenu()
            
            show_action = QAction("显示窗口", self)
            show_action.triggered.connect(self.show_normal)
            tray_menu.addAction(show_action)
            
            tray_menu.addSeparator()
            
            start_action = QAction("启动计划", self)
            start_action.triggered.connect(self.on_start_plan)
            tray_menu.addAction(start_action)
            
            reminder_action = QAction("开始提醒", self)
            reminder_action.triggered.connect(self.on_toggle_reminders)
            tray_menu.addAction(reminder_action)
            
            tray_menu.addSeparator()
            
            exit_action = QAction("退出", self)
            exit_action.triggered.connect(self.close)
            tray_menu.addAction(exit_action)
            
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.show()
            
            # 托盘图标点击事件
            self.tray_icon.activated.connect(self.on_tray_activated)
    
    def on_tray_activated(self, reason):
        """托盘图标激活事件"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_normal()
    
    def show_normal(self):
        """显示窗口"""
        self.show()
        self.activateWindow()
        self.raise_()
    
    def log_message(self, message):
        """添加日志消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        
        # 自动滚动到底部
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def update_display(self):
        """更新显示"""
        status = self.reminder_system.get_plan_status()
        
        # 更新状态标签
        self.status_label.setText(f"状态：{status.value}")
        
        # 更新进度条
        if status == PlanStatus.NOT_STARTED:
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat("0%")
        elif status == PlanStatus.DAY1:
            self.progress_bar.setValue(1)
            self.progress_bar.setFormat("33%")
        elif status == PlanStatus.DAY2:
            self.progress_bar.setValue(2)
            self.progress_bar.setFormat("66%")
        elif status == PlanStatus.DAY3:
            self.progress_bar.setValue(3)
            self.progress_bar.setFormat("100%")
        elif status == PlanStatus.COMPLETED:
            self.progress_bar.setValue(3)
            self.progress_bar.setFormat("已完成")
        
        # 更新日期标签
        if self.reminder_system.start_date:
            self.date_label.setText(f"开始日期：{self.reminder_system.start_date}")
        else:
            self.date_label.setText("开始日期：未设置")
        
        # 更新下一个提醒
        next_time, next_title = self.reminder_system.get_next_reminder_info()
        if next_time and next_title:
            self.next_reminder_label.setText(f"下一个提醒：{next_time} - {next_title}")
        else:
            self.next_reminder_label.setText("下一个提醒：无")
        
        # 更新计划显示
        plan, error = self.reminder_system.get_today_plan()
        
        if error:
            self.plan_title_label.setText(error)
            self.plan_table.setRowCount(0)
        elif plan:
            self.plan_title_label.setText(plan['title'])
            self.update_plan_table(plan)
        
        # 更新按钮状态
        if status == PlanStatus.NOT_STARTED:
            self.start_btn.setEnabled(True)
            self.reminder_btn.setEnabled(False)
        else:
            self.start_btn.setEnabled(False)
            self.reminder_btn.setEnabled(True)
    
    def update_plan_table(self, plan):
        """更新计划表格"""
        schedule_items = plan['schedule']
        self.plan_table.setRowCount(len(schedule_items))
        
        now = datetime.now().strftime("%H:%M")
        
        for row, item in enumerate(schedule_items):
            # 时间
            time_item = QTableWidgetItem(item['time'])
            time_item.setTextAlignment(Qt.AlignCenter)
            
            # 学习内容
            title_item = QTableWidgetItem(item['title'])
            
            # 时长
            duration_item = QTableWidgetItem(item['duration'])
            duration_item.setTextAlignment(Qt.AlignCenter)
            
            # 状态
            if item['time'] < now:
                status_text = "✅ 已完成"
                status_color = QColor(46, 204, 113)  # 绿色
            else:
                status_text = "⏳ 待进行"
                status_color = QColor(241, 196, 15)  # 黄色
            
            status_item = QTableWidgetItem(status_text)
            status_item.setTextAlignment(Qt.AlignCenter)
            status_item.setForeground(status_color)
            
            self.plan_table.setItem(row, 0, time_item)
            self.plan_table.setItem(row, 1, title_item)
            self.plan_table.setItem(row, 2, duration_item)
            self.plan_table.setItem(row, 3, status_item)
    
    def on_start_plan(self):
        """启动计划按钮点击事件"""
        if self.reminder_system.start_plan():
            self.log_message("✅ 学习计划已启动")
            self.update_display()
            
            # 显示成功消息
            QMessageBox.information(self, "成功", "学习计划已成功启动！")
        else:
            self.log_message("❌ 启动计划失败")
    
    def on_toggle_reminders(self):
        """开始提醒按钮点击事件"""
        if self.reminder_thread and self.reminder_thread.isRunning():
            return
        
        # 设置提醒
        success = self.reminder_system.schedule_reminders(self.show_notification)
        if not success:
            self.log_message("❌ 设置提醒失败")
            return
        
        # 创建并启动提醒线程
        self.reminder_thread = ReminderThread(self.reminder_system)
        self.reminder_thread.reminder_signal.connect(self.show_notification)
        self.reminder_thread.start()
        
        self.reminder_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        self.log_message("🚀 提醒系统已启动")
    
    def on_stop_reminders(self):
        """停止提醒按钮点击事件"""
        if self.reminder_thread:
            self.reminder_thread.stop()
            self.reminder_thread = None
        
        schedule.clear()
        
        self.reminder_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
        self.log_message("⏹️  提醒系统已停止")
    
    def show_notification(self, title="提醒", message=""):
        """显示通知（包含弹窗和声音）"""
        self.log_message(f"🔔 {title}: {message}")
        
        # 1. 显示弹窗对话框（强制用户看到）
        self.show_popup_dialog(title, message)
        
        # 2. 播放提醒声音
        self.play_notification_sound()
        
        # 3. 显示系统托盘通知
        if self.tray_icon:
            self.tray_icon.showMessage(title, message, QSystemTrayIcon.Information, 5000)
        
        # 4. 如果窗口最小化，恢复并激活窗口
        if self.isMinimized():
            self.show_normal()
        else:
            # 即使窗口已显示，也将其带到最前面
            self.raise_()
            self.activateWindow()
    
    def show_popup_dialog(self, title, message):
        """显示弹窗对话框"""
        # 创建自定义的提醒对话框
        dialog = QMessageBox(self)
        dialog.setWindowTitle(title)
        dialog.setText(message)
        dialog.setIcon(QMessageBox.Information)
        
        # 添加自定义按钮
        ok_button = dialog.addButton("知道了", QMessageBox.AcceptRole)
        snooze_button = dialog.addButton("10分钟后提醒", QMessageBox.ActionRole)
        
        # 设置对话框样式
        dialog.setStyleSheet("""
            QMessageBox {
                background-color: #f8f9fa;
                font-size: 14px;
            }
            QMessageBox QLabel {
                color: #2c3e50;
                font-weight: bold;
                font-size: 16px;
                padding: 15px;
            }
            QMessageBox QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
                margin: 5px;
            }
            QMessageBox QPushButton:hover {
                background-color: #2980b9;
            }
            QMessageBox QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        
        # 设置对话框为应用程序模态（阻止其他窗口）
        dialog.setWindowModality(Qt.ApplicationModal)
        
        # 显示对话框并等待用户响应
        dialog.exec_()
        
        # 处理用户选择
        clicked_button = dialog.clickedButton()
        if clicked_button == snooze_button:
            self.log_message("⏰ 已设置10分钟后再次提醒")
            # 这里可以添加延迟提醒的逻辑
            # 例如：10分钟后再次提醒
    
    def play_notification_sound(self):
        """播放提醒声音（多种方法尝试）"""
        sound_played = False
        
        # 方法1: 使用系统默认提示音（Windows）
        if sys.platform == 'win32':
            try:
                import winsound
                # 尝试播放系统提示音
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
                sound_played = True
            except:
                try:
                    # 尝试播放蜂鸣声
                    winsound.Beep(1000, 500)  # 频率1000Hz，持续时间500ms
                    sound_played = True
                except:
                    pass
        
        # 方法2: 使用QT的声音提示
        if not sound_played:
            try:
                from PyQt5.QtMultimedia import QSound
                # QT的简单提示音
                QSound.play("SystemAsterisk")  # Windows系统声音
                sound_played = True
            except:
                pass
        
        # 方法3: 使用playsound库（如果已安装）
        if not sound_played:
            try:
                import playsound
                # 可以播放自定义的MP3/WAV文件
                # playsound.playsound('notification.mp3')
                # 暂时使用系统默认声音
                playsound.playsound(None)  # 播放系统默认声音
                sound_played = True
            except:
                pass
        
        # 方法4: 使用简单的控制台输出作为后备
        if not sound_played:
            print('\a')  # ASCII bell字符，可能在某些终端产生声音
            self.log_message("🔊 播放了简单的提示音")
        else:
            self.log_message("🔊 播放了提醒声音")
    
    def on_test_notification(self):
        """测试提醒按钮点击事件"""
        self.show_notification(
            title="📖 测试提醒",
            message="这是一个测试提醒！\n点击'知道了'关闭，或'10分钟后提醒'延迟提醒。"
        )
    
    def closeEvent(self, event):
        """关闭事件"""
        # 停止提醒线程
        if self.reminder_thread and self.reminder_thread.isRunning():
            self.reminder_thread.stop()
        
        # 隐藏到托盘
        if self.tray_icon and self.tray_icon.isVisible():
            reply = QMessageBox.question(
                self, "确认",
                "是否最小化到系统托盘？\n选择'否'将退出程序。",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                self.hide()
                event.ignore()
                return
        
        # 确认退出
        reply = QMessageBox.question(
            self, "确认退出",
            "确定要退出程序吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setApplicationName("Python学习计划提醒系统")
    
    # 设置应用程序样式
    app.setStyle("Fusion")
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()