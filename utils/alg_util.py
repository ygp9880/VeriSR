import math

def check_value_error(calc_value: float, ref_value: float,
                      percent: float = None, abs_tol: float = None) -> bool:
    """
    检查计算值与参考值是否在允许误差范围内，可以同时检查相对误差和绝对误差。

    参数:
        calc_value (float): 计算值
        ref_value (float): 文献或参考值
        percent (float, optional): 允许相对误差百分比 (例如 0.05 表示 ±5%)
        abs_tol (float, optional): 允许绝对误差 (例如 0.01 表示 ±0.01)

    返回:
        bool: 如果在误差范围内返回 True，否则返回 False
    """
    if ( calc_value is None or
            ref_value is None or
            math.isinf(calc_value) or
            math.isinf(ref_value) or
            math.isnan(calc_value) or
            math.isnan(ref_value)
    ):
        return False

    relative_ok = True
    absolute_ok = True

    # 相对误差检查
    if percent is not None:
        if ref_value == 0:
            # 如果参考值为0，则用绝对误差判断
            relative_ok = abs(calc_value) <= percent
        else:
            relative_error = abs(calc_value - ref_value) / abs(ref_value)
            relative_ok = relative_error <= percent

    # 绝对误差检查
    if abs_tol is not None:
        absolute_error = abs(calc_value - ref_value)
        absolute_ok = absolute_error <= abs_tol

    return relative_ok or absolute_ok