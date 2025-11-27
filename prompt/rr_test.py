import math
import pandas as pd
from typing import List, Dict
from scipy.stats import norm

def compute_effects(data: List[Dict], method="RR", correction=0.5, conf_level=0.95):
    """
    计算每个研究的 RR 或 OR 及其 95% CI

    参数:
        data: List[Dict]，每个研究的数据，格式示例:
            {
                'study': 'Sayani FA 2005',
                'events_experimental': 0,
                'n_experimental': 8,
                'events_control': 1,
                'n_control': 8
            }
        method: "RR" 或 "OR"
        correction: 连续性校正 (默认 0.5, Haldane-Anscombe)
        conf_level: 置信水平 (默认 0.95)

    返回:
        pandas.DataFrame, 每行是一个研究，包括效应量和 95% CI
    """
    results = []
    z = norm.ppf((1 + conf_level) / 2)

    for study in data:
        a = study["events_experimental"]
        n1 = study["n_experimental"]
        c = study["events_control"]
        n2 = study["n_control"]

        b = n1 - a
        d = n2 - c

        # 应用连续性校正
        a_c, b_c, c_c, d_c = a + correction, b + correction, c + correction, d + correction

        if method == "RR":
            log_eff = math.log((a_c / (a_c + b_c)) / (c_c / (c_c + d_c)))
            var = 1.0/a_c - 1.0/(a_c + b_c) + 1.0/c_c - 1.0/(c_c + d_c)
        elif method == "OR":
            log_eff = math.log((a_c * d_c) / (b_c * c_c))
            var = 1.0/a_c + 1.0/b_c + 1.0/c_c + 1.0/d_c
        else:
            raise ValueError("method must be 'RR' or 'OR'")

        se = math.sqrt(var)
        ci_low = math.exp(log_eff - z*se)
        ci_up = math.exp(log_eff + z*se)
        eff_value = math.exp(log_eff)

        results.append({
            "study": study["study"],
            "method": method,
            "value": eff_value,
            "ci_lower": ci_low,
            "ci_upper": ci_up,
            "log_value": log_eff,
            "se_log": se,
            "events_exp": a,
            "n_exp": n1,
            "events_ctrl": c,
            "n_ctrl": n2
        })

    return pd.DataFrame(results)


# 示例数据
data = [
    {
        'study': 'Sayani FA 2005',
        'events_experimental': 0,
        'n_experimental': 8,
        'events_control': 1,
        'n_control': 8
    },
    {
        'study': 'Another Study',
        'events_experimental': 2,
        'n_experimental': 50,
        'events_control': 5,
        'n_control': 50
    }
]

# 运行
df_rr = compute_effects(data, method="RR")
df_or = compute_effects(data, method="OR")

print("Risk Ratio results:")
print(df_rr, "\n")

print("Odds Ratio results:")
print(df_or)
