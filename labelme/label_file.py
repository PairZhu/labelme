import contextlib
import io
import json
import os.path as osp

import numpy as np
import PIL.Image

from labelme import PY2
from labelme import __version__
from labelme import utils
from labelme.logger import logger

PIL.Image.MAX_IMAGE_PIXELS = None


@contextlib.contextmanager
def open(name, mode):
    assert mode in ["r", "w"]
    if PY2:
        mode += "b"
        encoding = None
    else:
        encoding = "utf-8"
    yield io.open(name, mode, encoding=encoding)
    return


class LabelFileError(Exception):
    pass


class LabelFile(object):
    basename = "labels"
    suffix = ".json"

    def __init__(self, filename=None):
        self.shapes = []
        self.imagePath = None
        self.imageData = None
        self.beginTime = None
        self.endTime = None
        self.filename = filename

    @staticmethod
    def load_image_file(filename):
        try:
            img_data = np.fromfile(filename, dtype="<i2")
            file_name_without_ext = osp.splitext(osp.basename(filename))[0]
            begin_time = int(file_name_without_ext.split("_")[0])
            end_time = int(file_name_without_ext.split("_")[1])
            point_len = int(file_name_without_ext.split("_")[2])
            img_data = img_data.reshape(-1, point_len).T
        except IOError:
            logger.error("Failed opening data file: {}".format(filename))
            return

        return img_data, begin_time, end_time

    def load(self, filename, imagePath):
        keys = [
            "version",
            "imageDir",
            "shapes",  # polygonal annotations
            "flags",  # image level flags
            "imageHeight",
            "imageWidth",
        ]
        shape_keys = [
            "label",
            "points",
            "group_id",
            "shape_type",
            "flags",
            "description",
            "mask",
        ]
        try:
            with open(filename, "r") as f:
                data = json.load(f)

            # relative path from label file to relative path from cwd
            imageData, beginTime, endTime = self.load_image_file(imagePath)
            flags = data.get("flags") or {}
            self._check_image_height_and_width(
                imageData,
                data.get("imageHeight"),
                data.get("imageWidth"),
            )
            shapes = [
                dict(
                    label=s["label"],
                    points=s["points"],
                    shape_type=s.get("shape_type", "polygon"),
                    flags=s.get("flags", {}),
                    description=s.get("description"),
                    group_id=s.get("group_id"),
                    mask=utils.img_b64_to_arr(s["mask"]) if s.get("mask") else None,
                    other_data={k: v for k, v in s.items() if k not in shape_keys},
                )
                for s in data["shapes"]
            ]
        except Exception as e:
            raise LabelFileError(e)

        otherData = {}
        for key, value in data.items():
            if key not in keys:
                otherData[key] = value

        # Only replace data after everything is loaded.
        self.flags = flags
        self.shapes = shapes
        self.imageData = imageData
        self.beginTime = beginTime
        self.endTime = endTime
        self.filename = filename
        self.otherData = otherData

    @staticmethod
    def _check_image_height_and_width(imageData, imageHeight, imageWidth):
        if imageHeight is not None and imageData.shape[0] != imageHeight:
            logger.error(
                "imageHeight does not match with imageData or imagePath, "
                "so getting imageHeight from actual image."
            )
            imageHeight = imageData.shape[0]
        if imageWidth is not None and imageData.shape[1] != imageWidth:
            logger.error(
                "imageWidth does not match with imageData or imagePath, "
                "so getting imageWidth from actual image."
            )
            imageWidth = imageData.shape[1]
        return imageHeight, imageWidth

    def save(
        self,
        filename,
        shapes,
        imagePath,
        imageHeight,
        imageWidth,
        otherData=None,
        flags=None,
    ):
        if otherData is None:
            otherData = {}
        if flags is None:
            flags = {}
        imageDir = osp.dirname(imagePath)
        data = dict(
            version=__version__,
            flags=flags,
            shapes=shapes,
            imageDir=imageDir,
            imageHeight=imageHeight,
            imageWidth=imageWidth,
        )
        for key, value in otherData.items():
            assert key not in data
            data[key] = value
        try:
            with open(filename, "w") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.filename = filename
        except Exception as e:
            raise LabelFileError(e)

    @staticmethod
    def is_label_file(filename):
        return osp.splitext(filename)[1].lower() == LabelFile.suffix
