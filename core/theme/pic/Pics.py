from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon

from MainCode import path

checkMark = QPixmap(path + "core/theme/Marker/checkMark.png")
MinusMark = QPixmap(path + "core/theme/Marker/MinusMark.png")
deleteMark = QPixmap(path + "core/theme/Marker/deleteMark.png")
UserICO = QPixmap(path + "core/theme/pic/pic/User.png")
passwordICO = QPixmap(path + "core/theme/pic/pic/password.png")
Logo = QPixmap(path + "core/theme/pic/pic/MERSAD_Logo.png")
ON = QIcon(QPixmap(path + "core/theme/pic/pic/ON.png"))
OFF = QIcon(QPixmap(path + "core/theme/pic/pic/OFF.png"))
checkMark = checkMark.scaled(30, 30, Qt.KeepAspectRatio)
deleteMark = deleteMark.scaled(30, 30, Qt.KeepAspectRatio)
MinusMark = MinusMark.scaled(25, 13)
