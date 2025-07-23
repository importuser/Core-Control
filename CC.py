# copywrite (c) CC
# 
# Licence: just keep these few lines for credit, yeh./
# uhm, do pip install xyz, zyz being the thing u wanna install, idot.

import sys
import psutil
import time
import subprocess
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton, QTabWidget,
    QFileDialog, QPlainTextEdit, QFormLayout, QDialogButtonBox,
    QGroupBox, QToolButton, QMessageBox, QTextBrowser
)
from PySide6.QtGui import QFont, QKeyEvent
from PySide6.QtCore import Qt, QTimer
import pyqtgraph as pg

class TerminalTab(QWidget):
    used_numbers = set()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setStyleSheet("color: white; background-color: #000;")
        self.output.setFont(QFont("Courier New", 11))

        self.input = QLineEdit()
        self.input.setStyleSheet("color: white; background-color: #111; border: 1px solid #333;")
        self.input.setFont(QFont("Courier New", 11))
        self.input.returnPressed.connect(self.execute_command)

        layout.addWidget(self.output)
        layout.addWidget(self.input)

        self.number = self._get_available_tab_number()
        TerminalTab.used_numbers.add(self.number)
        self.name = f"Terminal {self.number}"

    def _get_available_tab_number(self):
        n = 1
        while n in TerminalTab.used_numbers:
            n += 1
        return n

    def cleanup(self):
        TerminalTab.used_numbers.discard(self.number)

    def execute_command(self):
        command = self.input.text()
        if not command.strip():
            self.input.clear()
            return
        self.output.append(f"> {command}")
        try:
            shell = True
            platform_shell = "/bin/bash" if sys.platform != "win32" else None
            process = subprocess.Popen(command, shell=shell,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE,
                                       stdin=subprocess.PIPE,
                                       executable=platform_shell)
            stdout, stderr = process.communicate()

            if stdout:
                self.output.append(stdout.decode(errors="ignore"))
            if stderr:
                self.output.append(f"[stderr]: {stderr.decode(errors='ignore')}")
        except Exception as e:
            self.output.append(f"[Exception]: {e}")
        self.input.clear()

class RunScriptTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.script_edit = QPlainTextEdit()
        self.script_edit.setPlaceholderText("# Write your Python script here...")
        layout.addWidget(self.script_edit)

        self.run_button = QPushButton("Run Script")
        self.run_button.clicked.connect(self.run_script)
        layout.addWidget(self.run_button)

        self.output = QTextBrowser()
        self.output.setStyleSheet("background-color: #111; color: #eee; font-family: Consolas, monospace; font-size: 12px;")
        layout.addWidget(self.output)

    def run_script(self):
        code = self.script_edit.toPlainText()
        self.output.clear()
        try:
            # Redirect stdout and stderr to capture output
            import io
            import contextlib

            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
                exec(code, {})

            self.output.append(buffer.getvalue())
        except Exception as e:
            self.output.append(f"# Error: {e}")

class OpenFileTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.file_path_label = QLabel("No file selected")
        self.file_path_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.file_path_label)

        self.open_btn = QPushButton("Select File")
        self.open_btn.setStyleSheet("padding: 6px; font-size: 13px;")
        self.open_btn.clicked.connect(self.select_file)
        layout.addWidget(self.open_btn)

        self.file_content = QPlainTextEdit()
        self.file_content.setReadOnly(True)
        self.file_content.setStyleSheet(
            "background-color: #111; color: #eee; font-family: Consolas, monospace; font-size: 12px;"
        )
        layout.addWidget(self.file_content)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*)")
        if file_path:
            self.file_path_label.setText(f"File: {file_path}")
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.file_content.setPlainText(content)
            except Exception as e:
                self.file_content.setPlainText(f"Error reading file: {e}")

class FetchURLTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter URL here...")
        self.url_input.setStyleSheet("font-size: 13px; padding: 5px;")
        layout.addWidget(self.url_input)

        self.fetch_btn = QPushButton("Fetch")
        self.fetch_btn.setStyleSheet("padding: 6px; font-size: 13px;")
        self.fetch_btn.clicked.connect(self.fetch_url)
        layout.addWidget(self.fetch_btn)

        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setStyleSheet(
            "background-color: #111; color: #eee; font-family: Consolas, monospace; font-size: 12px;"
        )
        layout.addWidget(self.output)

    def fetch_url(self):
        import urllib.request

        url = self.url_input.text().strip()
        if not url:
            self.output.setPlainText("Please enter a valid URL")
            return
        try:
            with urllib.request.urlopen(url) as response:
                content = response.read(1024 * 10).decode("utf-8", errors="ignore")
            self.output.setPlainText(content)
        except Exception as e:
            self.output.setPlainText(f"Failed to fetch URL: {e}")

class SettingsTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QFormLayout()
        self.setLayout(layout)

        self.font_size_input = QLineEdit("11")
        self.theme_input = QLineEdit("Dark")

        layout.addRow("Font Size:", self.font_size_input)
        layout.addRow("Theme:", self.theme_input)

        self.apply_btn = QPushButton("Apply")
        layout.addWidget(self.apply_btn)

class SystemInfoTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        info = (
            f"CPU Cores: {psutil.cpu_count(logical=False)}\n"
            f"Logical CPUs: {psutil.cpu_count(logical=True)}\n"
            f"Total Memory: {psutil.virtual_memory().total / (1024 ** 3):.2f} GB\n"
            f"Disk Partitions: {len(psutil.disk_partitions())}\n"
            f"Platform: {sys.platform}"
        )
        self.label = QLabel(info)
        self.label.setFont(QFont("Consolas", 11))
        layout.addWidget(self.label)


class ProcessViewerTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.process_list = QPlainTextEdit()
        self.process_list.setReadOnly(True)
        layout.addWidget(self.process_list)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.update_processes)
        layout.addWidget(refresh_btn)

        self.update_processes()

    def update_processes(self):
        procs = []
        for proc in psutil.process_iter(["pid", "name", "username"]):
            try:
                procs.append(f"{proc.info['pid']:5} {proc.info['name'][:30]:30} {proc.info['username']}")
            except psutil.NoSuchProcess:
                pass
        self.process_list.setPlainText("\n".join(procs))

class CC(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Core Control")
        self.resize(1200, 700)
        self.setStyleSheet("background-color: black; color: white;")

        main = QWidget()
        main_layout = QHBoxLayout()
        main.setLayout(main_layout)

        # Left panel: system info & stats
        left_panel = QVBoxLayout()
        self.uptime_label = QLabel("Uptime: 0s")
        self.uptime_label.setFont(QFont("Consolas", 12))

        # CPU group box
        cpu_group = QGroupBox("CPU Usage")
        cpu_group.setStyleSheet("QGroupBox { color: lightgreen; font-weight: bold; }")
        cpu_layout = QVBoxLayout()
        self.cpu_plot = pg.PlotWidget()
        self.cpu_plot.setYRange(0, 100)
        self.cpu_plot.setBackground("black")
        self.cpu_curve = self.cpu_plot.plot(pen=pg.mkPen("g", width=2))
        self.cpu_data = []
        self.cpu_usage_label = QLabel("0%")
        self.cpu_usage_label.setFont(QFont("Consolas", 11))
        self.cpu_usage_label.setAlignment(Qt.AlignCenter)
        cpu_layout.addWidget(self.cpu_plot)
        cpu_layout.addWidget(self.cpu_usage_label)
        cpu_group.setLayout(cpu_layout)

        # Memory group box
        mem_group = QGroupBox("Memory Usage")
        mem_group.setStyleSheet("QGroupBox { color: cyan; font-weight: bold; }")
        mem_layout = QVBoxLayout()
        self.mem_plot = pg.PlotWidget()
        self.mem_plot.setYRange(0, 100)
        self.mem_plot.setBackground("black")
        self.mem_curve = self.mem_plot.plot(pen=pg.mkPen("c", width=2))
        self.mem_data = []
        self.mem_usage_label = QLabel("0%")
        self.mem_usage_label.setFont(QFont("Consolas", 11))
        self.mem_usage_label.setAlignment(Qt.AlignCenter)
        mem_layout.addWidget(self.mem_plot)
        mem_layout.addWidget(self.mem_usage_label)
        mem_group.setLayout(mem_layout)

        self.entropy_label = QLabel("Entropy [dev/random]")
        self.entropy_label.setFont(QFont("Consolas", 10))
        self.entropy_label.setStyleSheet("color: gray;")

        self.disk_label = QLabel("Disk Usage: N/A")
        self.disk_label.setFont(QFont("Consolas", 11))
        self.net_label = QLabel("Network: N/A")
        self.net_label.setFont(QFont("Consolas", 11))

        left_panel.addWidget(self.uptime_label)
        left_panel.addWidget(cpu_group)
        left_panel.addWidget(mem_group)
        left_panel.addWidget(self.entropy_label)
        left_panel.addWidget(self.disk_label)
        left_panel.addWidget(self.net_label)
        left_panel.addStretch()

        # Center panel: time, tabs, keyboard display
        center_panel = QVBoxLayout()
        self.time_label = QLabel("Time: --:--:--")
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setFont(QFont("Consolas", 14))

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)

        # Add initial two terminal tabs
        self.add_new_terminal_tab()
        self.add_new_terminal_tab()

        # Add "+" button for new tabs
        self.add_tab_button = QToolButton()
        self.add_tab_button.setText("+")
        self.add_tab_button.setFont(QFont("Arial", 16))
        self.add_tab_button.setStyleSheet(
            "QToolButton { color: white; background-color: #222; border: none; }"
            "QToolButton:hover { background-color: #444; }"
        )
        self.add_tab_button.clicked.connect(self.add_new_terminal_tab)
        self.tabs.setCornerWidget(self.add_tab_button, Qt.TopRightCorner)

        self.keyboard_display = QLabel("Last Key: None")
        self.keyboard_display.setAlignment(Qt.AlignCenter)
        self.keyboard_display.setFont(QFont("Courier New", 12))
        self.keyboard_display.setStyleSheet("color: #999;")

        center_panel.addWidget(self.time_label)
        center_panel.addWidget(self.tabs, stretch=1)
        center_panel.addWidget(self.keyboard_display)

        # Right panel: Toolbox buttons (open tools as tabs)
        right_panel = QVBoxLayout()
        tool_label = QLabel("Toolbox")
        tool_label.setAlignment(Qt.AlignCenter)
        tool_label.setFont(QFont("Arial", 12, QFont.Bold))
        right_panel.addWidget(tool_label)

        # Mapping tool names to tab widget classes
        self.tool_classes = {
            "Run Script": RunScriptTab,
            "Open File": OpenFileTab,
            "Fetch URL": FetchURLTab,
            "Settings": SettingsTab,
            "System Info": SystemInfoTab,
            "Process Viewer": ProcessViewerTab,
        }

        for tool_name in self.tool_classes:
            btn = QPushButton(tool_name)
            btn.setStyleSheet(
                "background-color: #111; color: white; border: 1px solid #444; padding: 8px; font-size: 13px;"
            )
            btn.clicked.connect(self.open_tool_tab)
            right_panel.addWidget(btn)

        right_panel.addStretch()

        # Compose main layout
        main_layout.addLayout(left_panel, 2)
        main_layout.addLayout(center_panel, 6)
        main_layout.addLayout(right_panel, 2)
        self.setCentralWidget(main)

        # Timers for updates
        self.start_time = time.time()
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_info)
        self.update_timer.start(1000)

        # For network speed calculation
        self.net_io_old = psutil.net_io_counters()

    # Add new terminal tab
    def add_new_terminal_tab(self):
        tab = TerminalTab()
        self.tabs.addTab(tab, tab.name)
        self.tabs.setCurrentWidget(tab)

    # Open a toolbox tool as a new tab (reuse if already opened)
    def open_tool_tab(self):
        sender = self.sender()
        tool_name = sender.text()

        # Check if already open
        for i in range(self.tabs.count()):
            if self.tabs.tabText(i) == tool_name:
                self.tabs.setCurrentIndex(i)
                return

        # Instantiate tab widget for tool
        cls = self.tool_classes[tool_name]
        tab = cls()
        self.tabs.addTab(tab, tool_name)
        self.tabs.setCurrentWidget(tab)

    # Handle tab closing with cleanup and disallow last tab close
    def close_tab(self, index):
        if self.tabs.count() <= 1:
            QMessageBox.warning(self, "Warning", "Cannot close the last tab.")
            return

        widget = self.tabs.widget(index)

        # Cleanup if terminal tab
        if isinstance(widget, TerminalTab):
            widget.cleanup()

        self.tabs.removeTab(index)
        widget.deleteLater()

    # Periodic updates of CPU, mem, network, uptime
    def update_info(self):
        uptime = int(time.time() - self.start_time)
        self.uptime_label.setText(f"Uptime: {uptime}s")

        current_time = time.strftime("%H:%M:%S")
        self.time_label.setText(f"Time: {current_time}")

        cpu = psutil.cpu_percent()
        self.cpu_data.append(cpu)
        if len(self.cpu_data) > 60:
            self.cpu_data.pop(0)
        self.cpu_curve.setData(self.cpu_data)
        self.cpu_usage_label.setText(f"{cpu:.1f}%")

        mem = psutil.virtual_memory()
        mem_percent = mem.percent
        self.mem_data.append(mem_percent)
        if len(self.mem_data) > 60:
            self.mem_data.pop(0)
        self.mem_curve.setData(self.mem_data)
        self.mem_usage_label.setText(f"{mem_percent:.1f}%")

        disk = psutil.disk_usage("/")
        self.disk_label.setText(f"Disk Usage: {disk.percent}%")

        net_io_new = psutil.net_io_counters()
        sent = net_io_new.bytes_sent - self.net_io_old.bytes_sent
        recv = net_io_new.bytes_recv - self.net_io_old.bytes_recv
        self.net_io_old = net_io_new
        self.net_label.setText(f"Network: ↑{sent / 1024:.1f} KB/s ↓{recv / 1024:.1f} KB/s")

    # Keyboard event show last key pressed
    def keyPressEvent(self, event: QKeyEvent):
        key_text = event.text()
        self.keyboard_display.setText(f"Last Key: {key_text if key_text.strip() else event.key()}")

    # Confirm before closing
    def closeEvent(self, event):
        if QMessageBox.question(self, 'Exit', 'Close the terminal?', QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CC()
    window.show()
    sys.exit(app.exec())

