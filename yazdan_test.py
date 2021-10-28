# TODO: bayad beshe az table khasi az data base backup begire v to folder haye moshakhas berize v bayad data archive ro tike tike konim

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QHeaderView, QAbstractItemView, QPushButton, QTableWidget, \
    QTableWidgetItem, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt


class TableWidget(QTableWidget):
    def __init__(self):
        super().__init__(1, 5)
        self.setHorizontalHeaderLabels(list('ABCDE'))
        self.verticalHeader().setDefaultSectionSize(50)
        self.horizontalHeader().setDefaultSectionSize(250)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)

    def _addRow(self):
        rowCount = self.rowCount()
        self.insertRow(rowCount)

    def _removeRow(self):
        if self.rowCount() > 0:
            self.removeRow(self.rowCount() - 1)

    def _copyRow(self):
        self.insertRow(self.rowCount())
        rowCount = self.rowCount()
        columnCount = self.columnCount()

        for j in range(columnCount):
            if not self.item(rowCount - 2, j) is None:
                self.setItem(rowCount - 1, j, QTableWidgetItem(self.item(rowCount - 2, j).text()))


class AppDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(1600, 600)

        mainLayout = QHBoxLayout()
        table = TableWidget()
        mainLayout.addWidget(table)
        buttonLayout = QVBoxLayout()

        button_new = QPushButton('New')
        button_new.clicked.connect(table._addRow)
        buttonLayout.addWidget(button_new)

        button_copy = QPushButton('Copy')
        button_copy.clicked.connect(table._copyRow)
        buttonLayout.addWidget(button_copy)

        button_remove = QPushButton('Remove')
        button_remove.clicked.connect(table._removeRow)
        buttonLayout.addWidget(button_remove, alignment=Qt.AlignTop)

        mainLayout.addLayout(buttonLayout)
        self.setLayout(mainLayout)


app = QApplication(sys.argv)
app.setStyleSheet('QPushButton{font-size: 20px; width: 200px; height: 50px}')
demo = AppDemo()
demo.show()
sys.exit(app.exec_())
