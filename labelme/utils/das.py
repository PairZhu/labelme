import numpy as np


def color_convert(
    data: np.ndarray,
    abs: bool = True,
    log10: bool = True,
    heatmap: bool = True,
    min_value: float = -1,
    max_value: float = 1,
) -> np.ndarray:
    dtype = data.dtype
    # 防止上溢
    data = data.astype(np.float32)
    # 获取类型的最大值
    if np.issubdtype(dtype, np.integer):
        type_max = max(np.iinfo(dtype).max, -np.iinfo(dtype).min)
    else:
        type_max = 1
    max_value = max_value * type_max
    # 如果类型为无符号整数，最小值为0
    if np.issubdtype(dtype, np.unsignedinteger):
        min_value = 0
    else:
        min_value = min_value * type_max
    # 截断
    data = np.clip(data, min_value, max_value)
    # 取绝对值
    if abs:
        data = np.abs(data)
        min_value = 0
    # 取对数
    MIN_LOG = 1
    if log10:
        data[data >= 0] = np.log10(data[data >= 0] + MIN_LOG)
        data[data < 0] = -np.log10(-data[data < 0] + MIN_LOG)
        max_value = np.log10(max_value + MIN_LOG)
        min_value = -np.log10(-min_value + MIN_LOG)

    # 归一化到0~1
    data = (data - min_value) / (max_value - min_value)
    if heatmap:
        cdict = {
            "red": (
                (0.00, 0, 0),
                (0.35, 0, 0),
                (0.66, 1, 1),
                (0.89, 1, 1),
                (1.00, 0.5, 0.5),
            ),
            "green": (
                (0.000, 0, 0),
                (0.125, 0, 0),
                (0.375, 1, 1),
                (0.640, 1, 1),
                (0.910, 0, 0),
                (1.000, 0, 0),
            ),
            "blue": (
                (0.00, 0.5, 0.5),
                (0.11, 1, 1),
                (0.34, 1, 1),
                (0.65, 0, 0),
                (1.00, 0, 0),
            ),
        }
    else:
        cdict = {
            "red": [(0.0, 1.0, 1.0), (1.0, 0.0, 0.0)],
            "green": [(0.0, 1.0, 1.0), (1.0, 0.0, 0.0)],
            "blue": [(0.0, 1.0, 1.0), (1.0, 0.0, 0.0)],
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
