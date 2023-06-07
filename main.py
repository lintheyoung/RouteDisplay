import sys
import json
import serial
from math import cos, sin, radians
from PyQt5.QtWidgets import (
    QApplication, QVBoxLayout, QWidget, QPushButton, QComboBox, QLineEdit, QHBoxLayout, QLabel, QTextEdit,
    QGridLayout, QCheckBox, QFileDialog
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from pyqtgraph import PlotWidget, ImageItem, ArrowItem, mkPen
from PyQt5.QtCore import QRectF
from serial.tools import list_ports
import cv2

class SerialThread(QThread):
    new_data = pyqtSignal(dict)

    def __init__(self, ser):
        super().__init__()
        self.ser = ser

    def run(self):
        while True:
            data = self.read_data()
            if data is not None:
                self.new_data.emit(data)

    def read_data(self):
        while self.ser.inWaiting():
            line = self.ser.readline().decode('utf-8', errors='ignore').strip()
            try:
                data = json.loads(line)
                return data
            except json.JSONDecodeError:
                pass

    def send_data(self, data):
        json_data = json.dumps(data)
        self.ser.write(json_data.encode('utf-8'))

class MyGraph(PlotWidget):
    def __init__(self, buffer_size=5, x_range=(0, 100), y_range=(0, 100), parent=None):
        super().__init__(parent)
        self.buffer_size = buffer_size
        self.x_range = x_range
        self.y_range = y_range
        self.positions = []
        self.path = self.plot([], [], pen=mkPen('r', width=10))
        self.arrow = ArrowItem(pos=(0, 0), angle=0, pen=mkPen('r', width=3), headLen=14, headWidth=14)
        self.addItem(self.arrow)
        self.setBackground('w')
        self.background = None
        self.set_background_image('map.png')
        self.setAspectLocked(True)

    def set_background_image(self, image_path):
        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.removeItem(self.background)
        self.background = ImageItem(image)
        self.addItem(self.background)
        self.background.setOpacity(0.5)
        self.background.setRect(QRectF(self.x_range[0], self.y_range[0], self.x_range[1] - self.x_range[0], self.y_range[1] - self.y_range[0]))
        self.update()

    def set_buffer_size(self, buffer_size):
        self.buffer_size = buffer_size

    def update_figure(self, x, y, head):
        self.positions.append((x, y))
        if len(self.positions) > self.buffer_size:
            self.positions.pop(0)
        path_x, path_y = zip(*self.positions)
        self.path.setData(path_x, path_y)
        self.arrow.setPos(x, y)
        head_transformed = (270 - head) % 360
        self.arrow.setRotation(-head_transformed)
        self.setXRange(*self.x_range)
        self.setYRange(*self.y_range)

    def clear_figure(self):
        self.clear()
        self.positions = []
        self.path = self.plot([], [], pen=mkPen('r', width=10))
        self.arrow = ArrowItem(pos=(0, 0), angle=0, pen=mkPen('r', width=3), headLen=14, headWidth=14)
        self.addItem(self.arrow)
        self.addItem(self.background)

    def toggle_grid(self, visible):
        self.showGrid(visible, visible)

class ApplicationWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.config_path = 'config.json'
        with open(self.config_path, 'r') as f:
            config = json.load(f)
        buffer_size_str = config.get('buffer_size', '1000')
        x_min_str = config.get('x_min', '0')
        x_max_str = config.get('x_max', '220')
        y_min_str = config.get('y_min', '0')
        y_max_str = config.get('y_max', '205')
        self.image_path = config.get('image_path', 'map.png')

        self.canvas = MyGraph(
            buffer_size=int(buffer_size_str),
            x_range=(float(x_min_str), float(x_max_str)),
            y_range=(float(y_min_str), float(y_max_str)),
            parent=self
        )

        self.plotting = False

        grid = QGridLayout(self)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 0)
        grid.setColumnStretch(2, 1)

        self.buffer_size_label = QLabel('轨迹保存长度:', self)
        self.buffer_size_edit = QLineEdit(buffer_size_str, self)
        self.xmin_label = QLabel('X Min:', self)
        self.xmin_edit = QLineEdit(x_min_str, self)
        self.xmax_label = QLabel('X Max:', self)
        self.xmax_edit = QLineEdit(x_max_str, self)
        self.ymin_label = QLabel('Y Min:', self)
        self.ymin_edit = QLineEdit(y_min_str, self)
        self.ymax_label = QLabel('Y Max:', self)
        self.ymax_edit = QLineEdit(y_max_str, self)

        self.port_label = QLabel('选择串口:', self)
        self.port_combo = QComboBox(self)
        ports = list_ports.comports()
        for port in ports:
            self.port_combo.addItem(port.device)

        self.grid_checkbox = QCheckBox('显示网格', self)
        self.grid_checkbox.stateChanged.connect(self.toggle_grid)

        self.text_edit = QTextEdit(self)
        grid.addWidget(self.text_edit, 0, 7, 11, 3)
        grid.addWidget(self.grid_checkbox, 8, 6)

        self.update_button = QPushButton('更新画布大小', self)
        self.update_button.clicked.connect(self.update_canvas_size)
        self.start_button = QPushButton('开始绘制', self)
        self.start_button.clicked.connect(self.start_plotting)

        grid.addWidget(self.canvas, 0, 0, 11, 5)
        grid.addWidget(self.buffer_size_label, 0, 5)
        grid.addWidget(self.buffer_size_edit, 0, 6)
        grid.addWidget(self.xmin_label, 1, 5)
        grid.addWidget(self.xmin_edit, 1, 6)
        grid.addWidget(self.xmax_label, 2, 5)
        grid.addWidget(self.xmax_edit, 2, 6)
        grid.addWidget(self.ymin_label, 3, 5)
        grid.addWidget(self.ymin_edit, 3, 6)
        grid.addWidget(self.ymax_label, 4, 5)
        grid.addWidget(self.ymax_edit, 4, 6)
        grid.addWidget(self.port_label, 5, 5)
        grid.addWidget(self.port_combo, 5, 6)
        grid.addWidget(self.update_button, 6, 5)
        grid.addWidget(self.start_button, 6, 6)

        self.input_label = QLabel('输入文本:', self)
        self.input_edit = QLineEdit(self)

        self.send_button = QPushButton('发送字符串', self)
        self.send_button.clicked.connect(self.send_data)

        grid.addWidget(self.input_edit, 7, 6)
        grid.addWidget(self.send_button, 7, 5)

        self.select_image_button = QPushButton('选择背景图', self)
        self.select_image_button.clicked.connect(self.select_image)
        grid.addWidget(self.select_image_button, 8, 5)

        self.setLayout(grid)

    def toggle_grid(self, state):
        self.canvas.toggle_grid(state)

    def send_data(self):
        data = self.input_edit.text()
        self.serial_thread.send_data({'text': data})

    def update_canvas_size(self):
        x_range = (float(self.xmin_edit.text()), float(self.xmax_edit.text()))
        y_range = (float(self.ymin_edit.text()), float(self.ymax_edit.text()))
        buffer_size = int(self.buffer_size_edit.text())

        config = {
            'buffer_size': self.buffer_size_edit.text(),
            'x_min': self.xmin_edit.text(),
            'x_max': self.xmax_edit.text(),
            'y_min': self.ymin_edit.text(),
            'y_max': self.ymax_edit.text(),
            'image_path': self.image_path
        }
        with open(self.config_path, 'w') as f:
            json.dump(config, f)

        self.canvas.x_range = x_range
        self.canvas.y_range = y_range
        self.canvas.set_buffer_size(buffer_size)

        self.canvas.clear_figure()
        if self.image_path:
            self.canvas.set_background_image(self.image_path)

    def display_data(self, data):
        self.text_edit.append(json.dumps(data))

    def start_plotting(self):
        if not self.plotting:
            selected_port = self.port_combo.currentText()
            self.ser = serial.Serial(selected_port, 115200)
            self.serial_thread = SerialThread(self.ser)
            self.serial_thread.new_data.connect(self.update_figure)
            self.serial_thread.new_data.connect(self.display_data)
            self.serial_thread.start()
            self.plotting = True
            self.start_button.setText('停止绘制')
        else:
            self.serial_thread.terminate()
            self.ser.close()
            self.plotting = False
            self.start_button.setText('开始绘制')

    def update_figure(self, data):
        self.canvas.update_figure(data['x'], data['y'], data['head'])

    def select_image(self):
        fname, _ = QFileDialog.getOpenFileName(self, '选择背景图', '.', "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif)")
        if fname:
            self.image_path = fname
            self.canvas.set_background_image(fname)
            config = {
                'buffer_size': self.buffer_size_edit.text(),
                'x_min': self.xmin_edit.text(),
                'x_max': self.xmax_edit.text(),
                'y_min': self.ymin_edit.text(),
                'y_max': self.ymax_edit.text(),
                'image_path': self.image_path
            }
            with open(self.config_path, 'w') as f:
                json.dump(config, f)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ApplicationWindow()
    window.setWindowTitle("小车轨迹绘制")
    window.show()
    sys.exit(app.exec_())
