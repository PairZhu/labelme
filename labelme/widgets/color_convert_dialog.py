from qtpy import QtWidgets
from qtpy.QtCore import Qt
from qtpy.QtGui import QImage

from labelme import utils


class ColorConvertDialog(QtWidgets.QDialog):
    MAX_VALUE = 10000

    def __init__(self, img, callback, parent=None):
        super(ColorConvertDialog, self).__init__(parent)
        self.setModal(True)
        self.setWindowTitle("Color Convert")

        # checkbox
        check_abs = QtWidgets.QCheckBox()
        check_abs.setChecked(True)

        check_log10 = QtWidgets.QCheckBox()
        check_log10.setChecked(True)

        check_heatmap = QtWidgets.QCheckBox()
        check_heatmap.setChecked(True)

        slider_max, widget_max = self._create_slider(
            (1, self.MAX_VALUE), self.MAX_VALUE
        )
        slider_min, widget_min = self._create_slider(
            (-self.MAX_VALUE, 0), -self.MAX_VALUE
        )

        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow("绝对值", check_abs)
        form_layout.addRow("对数变换", check_log10)
        form_layout.addRow("热力图", check_heatmap)
        form_layout.addRow("最大值", widget_max)
        form_layout.addRow("最小值", widget_min)
        self.setLayout(form_layout)

        check_abs.stateChanged.connect(self.onNewValue)
        check_log10.stateChanged.connect(self.onNewValue)
        check_heatmap.stateChanged.connect(self.onNewValue)
        slider_max.valueChanged.connect(self.onNewValue)
        slider_min.valueChanged.connect(self.onNewValue)

        self.img = img
        self.callback = callback
        self.abs_checkbox = check_abs
        self.log10_checkbox = check_log10
        self.heatmap_checkbox = check_heatmap
        self.slider_max = slider_max
        self.slider_min = slider_min

    def onNewValue(self, _):

        image = utils.color_convert(
            self.img,
            abs=self.abs_checkbox.isChecked(),
            log10=self.log10_checkbox.isChecked(),
            heatmap=self.heatmap_checkbox.isChecked(),
            min_value=self.slider_min.value() / self.MAX_VALUE,
            max_value=self.slider_max.value() / self.MAX_VALUE,
        )
        image = QImage(
            image.tobytes(),
            image.shape[1],
            image.shape[0],
            image.shape[1] * 3,
            QImage.Format_RGB888,
        )
        self.callback(image)

    def _create_slider(self, value_range, value):
        slider = QtWidgets.QSlider(Qt.Horizontal)
        slider.setRange(*value_range)
        slider.setValue(value)
        slider.valueChanged.connect(self.onNewValue)
        value_label = QtWidgets.QLabel(f"{value/self.MAX_VALUE*100:.2f}%")
        value_label.setFixedWidth(60)
        value_label.setAlignment(Qt.AlignRight)
        slider.valueChanged.connect(
            lambda v: value_label.setText(f"{v/self.MAX_VALUE*100:.2f}%")
        )
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(slider)
        layout.addWidget(value_label)
        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        return slider, widget

    def getFormValue(self):
        return {
            "abs": self.log10_checkbox.isChecked(),
            "log10": self.log10_checkbox.isChecked(),
            "heatmap": self.heatmap_checkbox.isChecked(),
            "min_value": self.slider_min.value(),
            "max_value": self.slider_max.value(),
        }

    def setFormValue(self, value):
        self.log10_checkbox.setChecked(value["log10"])
        self.heatmap_checkbox.setChecked(value["heatmap"])
        self.slider_min.setValue(value["min_value"])
        self.slider_max.setValue(value["max_value"])
        self.onNewValue(None)
