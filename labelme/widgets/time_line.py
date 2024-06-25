from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets
from datetime import datetime

import math


class TimeLine(QtWidgets.QWidget):
    INIT_POINT_NUM = 5

    def __init__(self, *args, **kwargs):
        super(TimeLine, self).__init__(*args, **kwargs)
        self._painter = QtGui.QPainter()
        self.setMinimumHeight(20)
        self.scale = 1
        self.offset = 0
        self.begin_time = None
        self.end_time = None
        self.area_width = None

    def paintEvent(self, event):
        if self.begin_time is None or self.end_time is None:
            return

        p = self._painter
        p.begin(self)
        p.setPen(QtCore.Qt.black)

        scale = self.scale
        time_len = self.end_time - self.begin_time
        offset_time = time_len * self.offset
        area_width = self.area_width

        point_num = self.INIT_POINT_NUM
        last_factor = 1
        while point_num <= self.INIT_POINT_NUM * scale:
            if last_factor == 2:
                last_factor = 5
            else:
                last_factor = 2
            point_num *= last_factor
        point_num = int(point_num / last_factor)

        point_per_time = time_len / point_num
        scaled_pixel_per_time = area_width / time_len * scale
        if scale >= 1:
            begin_point = math.ceil(offset_time / point_per_time)
            begin_pixel = scaled_pixel_per_time * (
                point_per_time * begin_point - offset_time
            )
            end_pixel = self.width()
        else:
            begin_pixel = -scaled_pixel_per_time * offset_time
            end_pixel = begin_pixel + point_num * point_per_time * scaled_pixel_per_time
        current_pixel = begin_pixel
        while int(current_pixel) <= end_pixel:
            p.drawLine(int(current_pixel), 15, int(current_pixel), 20)
            current_time_stamp = (
                int(
                    current_pixel / scaled_pixel_per_time
                    + offset_time
                    + self.begin_time
                )
                / 1000
            )
            # 根据时长的不同，显示不同的时间格式
            if point_per_time < 1000:
                current_time = datetime.fromtimestamp(current_time_stamp).strftime(
                    "%H:%M:%S.%f"
                )[:-3]
            elif point_per_time < 60 * 1000:
                current_time = datetime.fromtimestamp(current_time_stamp).strftime(
                    "%H:%M:%S"
                )
            else:
                current_time = datetime.fromtimestamp(current_time_stamp).strftime(
                    "%Y-%m-%d %H:%M"
                )

            pos = int(current_pixel - p.fontMetrics().width(current_time) // 2)
            # 限制时间显示在区域内
            pos = max(0, min(self.width() - p.fontMetrics().width(current_time), pos))
            p.drawText(pos, 12, current_time)
            current_pixel += scaled_pixel_per_time * point_per_time

        p.end()
