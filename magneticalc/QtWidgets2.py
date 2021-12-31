from magneticalc.Theme import Theme
from typing import Callable, Union, Optional
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QLayout, QHBoxLayout, QSpinBox, QLabel, QSizePolicy, QPushButton


def QSpinBox2(minimum: int, maximum: int, value: int, value_changed: Callable) -> QSpinBox:
    spin_box = QSpinBox()
    spin_box.setMinimum(minimum)
    spin_box.setMaximum(maximum)
    spin_box.setValue(value)
    # noinspection PyUnresolvedReferences
    spin_box.valueChanged.connect(value_changed)
    return spin_box


def QLabel2(string: str, bold=False, italic=False, color=None, fixed=False) -> QLabel:
    label = QLabel(string)
    if fixed:
        label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
    stylesheet_map = {
        "font-weight: bold": bold,
        "font-weight: italic": italic,
        f"color: {color}": color
    }
    label.setStyleSheet(";".join([string for string, condition in stylesheet_map.items() if condition]))
    return label


def QHBoxLayout2(*elements: Union[QWidget, QLayout]) -> QHBoxLayout:
    layout = QHBoxLayout()
    for element in elements:
        if isinstance(element, QWidget):
            layout.addWidget(element, alignment=Qt.AlignVCenter)
        elif isinstance(element, QLayout):
            layout.addLayout(element)
    return layout


def QPushButton2(parent: QWidget, icon: Optional[str], text: str, clicked: Callable) -> QPushButton:
    button = QPushButton(text)
    if icon:
        Theme.get_icon(parent, icon),
    # noinspection PyUnresolvedReferences
    button.clicked.connect(clicked)
    return button
