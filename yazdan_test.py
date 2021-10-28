# TODO: bayad beshe az table khasi az data base backup begire v to folder haye moshakhas berize v bayad data archive ro tike tike konim

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QHeaderView, QAbstractItemView, QPushButton, QTableWidget, \
    QTableWidgetItem, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor


class TableWidget(QTableWidget):
    def __init__(self):
        super().__init__()
        # self.setHorizontalHeaderLabels(list('ABCDE'))
        self.verticalHeader().setDefaultSectionSize(50)
        self.horizontalHeader().setDefaultSectionSize(250)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)

    def add_row(self):
        row_count = self.rowCount()
        self.insertRow(row_count)

    def remove_row(self):
        if self.rowCount() > 0:
            self.removeRow(self.rowCount() - 1)

    def copy_row(self):
        self.insertRow(self.rowCount())
        row_count = self.rowCount()
        column_count = self.columnCount()

        for j in range(column_count):
            if not self.item(row_count - 2, j) is None:
                self.setItem(row_count - 1, j, QTableWidgetItem(self.item(row_count - 2, j).text()))


class AppDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(1600, 600)

        main_layout = QHBoxLayout()
        table = TableWidget()

        table.setRowCount(len(inputs))
        table.setColumnCount(len(inputs[0]))
        table.setHorizontalHeaderLabels(["Input", "State"])

        for i, (name, code) in enumerate(inputs):
            item_name = QTableWidgetItem(name)
            item_code = QTableWidgetItem(code)
            # item_color = QTableWidgetItem()
            # item_color.setBackground(get_rgb_from_hex(code))
            table.setItem(i, 0, item_name)
            table.setItem(i, 1, item_code)

        main_layout.addWidget(table)
        button_layout = QVBoxLayout()

        button_new = QPushButton('New')
        button_new.clicked.connect(table.add_row)
        button_layout.addWidget(button_new)

        button_copy = QPushButton('Copy')
        button_copy.clicked.connect(table.copy_row)
        button_layout.addWidget(button_copy)

        button_remove = QPushButton('Remove')
        button_remove.clicked.connect(table.remove_row)
        button_layout.addWidget(button_remove, alignment=Qt.AlignTop)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)


inputs = [("X0", "OFF"),
          ("X1", "OFF"),
          ("X2", "OFF"),
          ("X3", "OFF"),
          ("X4", "OFF"),
          ("X5", "OFF"),
          ("X6", "OFF"),
          ("X7", "OFF")]

app = QApplication(sys.argv)
app.setStyleSheet('QPushButton{font-size: 20px; width: 200px; height: 50px}')
demo = AppDemo()
demo.show()
sys.exit(app.exec_())
