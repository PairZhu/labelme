import numpy as np
from matplotlib import cm


def color_convert(
    data: np.ndarray,
    abs: bool = True,
    log: bool = True,
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
    np.clip(data, min_value, max_value, out=data)
    # 取绝对值
    if abs:
        np.abs(data, out=data)
        min_value = 0
    # 取对数
    if log:
        sign = np.sign(data)
        np.log1p(np.abs(data, out=data), out=data)
        data *= sign
        max_value = np.log1p(max_value)
        min_value = -np.log1p(-min_value)

    # 归一化到0~1
    scale = 1 / (max_value - min_value)
    data -= min_value
    data *= scale

    # 使用matplotlib的colormap
    if heatmap:
        cmap = cm.get_cmap("jet")
    else:
        cmap = cm.get_cmap("gray")
    data = cmap(data)[..., :3]
    data *= 255
    data = data.astype(np.uint8)

    return data
