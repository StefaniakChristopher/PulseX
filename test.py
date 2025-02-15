import sys
from PySide6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QGraphicsBlurEffect
from PySide6.QtGui import QFont

app = QApplication(sys.argv)

window = QWidget()
layout = QVBoxLayout()

label = QLabel("This text is blurred")
font = QFont()
font.setPointSize(20)
label.setFont(font)

# Create a blur effect
blur_effect = QGraphicsBlurEffect()
blur_effect.setBlurRadius(1)  # Set the blur radius

# Apply the blur effect to the label
label.setGraphicsEffect(blur_effect)

layout.addWidget(label)
window.setLayout(layout)

window.show()
sys.exit(app.exec())
