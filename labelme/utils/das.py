import numpy as np


def color_convert(
    data: np.ndarray,
    log10: bool = True,
    heatmap: bool = True,
    min_value: float = 0,
    max_value: float = 1,
) -> np.ndarray:
    dtype = data.dtype
    # 防止abs时上溢
    data = np.abs(data.astype(np.float32))
    # 获取类型的最大值
    type_max = max(np.iinfo(dtype).max, -np.iinfo(dtype).min)
    max_value = max_value * type_max
    min_value = min_value * type_max
    # 截断
    data = np.clip(data, min_value, max_value)
    # 获取
    if log10:
        data = np.log10(data + 1e-5)
        max_value = np.log10(max_value + 1e-5)
        min_value = np.log10(min_value + 1e-5)
    # 归一化到0~1
    data = (data - min_value) / (max_value - min_value)
    if heatmap:
        cdict = {
            "red": [
                (0.0, 0.0),
                (0.35, 0.0),
                (0.66, 1.0),
                (0.89, 1.0),
                (1.0, 0.5),
            ],
            "green": [
                (0.0, 0.0),
                (0.125, 0.0),
                (0.375, 1.0),
                (0.64, 1.0),
                (0.91, 0.0),
                (1.0, 0.0),
            ],
            "blue": [
                (0.0, 0.5),
                (0.11, 1.0),
                (0.34, 1.0),
                (0.65, 0.0),
                (1.0, 0.0),
            ],
        }
    else:
        cdict = {
            "red": [(0.0, 1.0), (1.0, 0.0)],
            "green": [(0.0, 1.0), (1.0, 0.0)],
            "blue": [(0.0, 1.0), (1.0, 0.0)],
        }
    r = (
        np.interp(data, [x[0] for x in cdict["red"]], [x[1] for x in cdict["red"]])
        * 255
    )
    g = (
        np.interp(data, [x[0] for x in cdict["green"]], [x[1] for x in cdict["green"]])
        * 255
    )
    b = (
        np.interp(data, [x[0] for x in cdict["blue"]], [x[1] for x in cdict["blue"]])
        * 255
    )
    return np.stack([r, g, b], axis=-1).astype(np.uint8)
