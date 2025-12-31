import math
import numpy as np
from scipy.stats import norm, chi2
from utils.alg_util import check_value_error;
import json;
import traceback

def compute_effect(a, b, c, d, measure="RR", cc=0.5, cc_mode="zero-only",  conf_level=0.95):
    """
    计算单个研究的 log(RR) 或 log(OR) 及方差
    a: 实验组事件数
    b: 实验组非事件数
    c: 对照组事件数
    d: 对照组非事件数
    measure: "RR" 或 "OR"
    cc: 连续性校正
    cc_mode: "zero-only"（只在零事件时加cc）, "all"（所有格子加cc）, "none"（不加cc）
    """
    z = norm.ppf((1 + conf_level) / 2)
    if cc_mode == "all":
        a += cc; b += cc; c += cc; d += cc
    elif cc_mode == "zero-only":
        if a == 0 or b == 0 or c == 0 or d == 0:
            a += cc
            b += cc
            c += cc
            d += cc

    if measure == "RR":
        log_effect = math.log((a / (a + b)) / (c / (c + d)))
        var = 1/a - 1/(a+b) + 1/c - 1/(c+d)
    elif measure == "OR":
        log_effect = math.log((a*d) / (b*c))
        var = 1/a + 1/b + 1/c + 1/d
    else:
        raise ValueError("measure 必须是 'RR' 或 'OR'")

    se = math.sqrt(var)
    ci_low = math.exp(log_effect - z * se)
    ci_up = math.exp(log_effect + z * se)
    eff_value = math.exp(log_effect)

    return log_effect, var, eff_value, ci_low,ci_up

def safe_float(value, default=np.nan):
    """将值转换为 float，如果失败返回默认值"""
    try:
        if isinstance(value, str):
            value = value.replace(',', '').strip()  # 去掉逗号和空格
        return float(value)
    except:
        return default

def meta_analysis(studies, model="fixed", measure="RR", cc=0.5, cc_mode="zero-only"):
    """
    studies: 列表，每个元素为 dict，包含 keys:
        - events_experimental
        - n_experimental
        - events_control
        - n_control
    model: "fixed" 或 "random"
    measure: "RR" 或 "OR"
    """
    logs, variances = [], []

    study_check_result = [];
    data_size = len(studies);

    for s in studies:
        try:
            a = safe_float(s["events_experimental"])
            b = safe_float(s["n_experimental"]) - a
            c = safe_float(s["events_control"])
            d = safe_float(s["n_control"]) - c
            name = s['study'];
            log_eff, var, eff_value, ci_low, ci_up = compute_effect(a, b, c, d, measure=measure, cc=cc, cc_mode=cc_mode)
            logs.append(log_eff)
            variances.append(var)
            effect = s['Effect'];
            s_effect_value = effect['value'];
            s_effect_ci_lower = effect['ci_lower'];
            s_effect_ci_upper = effect['ci_upper'];

            eff_check = check_value_error(eff_value, s_effect_value, 0.1, 0.1);
            cli_lower_check = check_value_error(ci_low, s_effect_ci_lower, 0.1, 0.1);
            cli_upper_check = check_value_error(ci_up, s_effect_ci_upper, 0.1, 0.1);




            result = {'eff_value':eff_value, 'ci_low':ci_low,'ci_up':ci_up};
            study_check_result.append({'name': name, 'eff_check': eff_check, 'cli_lower_check': cli_lower_check,
                                       'cli_upper_check': cli_upper_check, 'model_result':result,'data':s});
        except Exception as e:
            print(f"Error processing study {s}: {e}")
            traceback.print_exc()
            results.append({
                "pooled_log": np.nan,
                "pooled_var": np.nan
            })



    logs = np.array(logs)
    variances = np.array(variances)
    weights = 1 / variances

    # 固定效应
    pooled_log = np.sum(weights * logs) / np.sum(weights)
    pooled_var = 1 / np.sum(weights)

    Q = np.sum(weights * (logs - pooled_log) ** 2)
    df = len(studies) - 1
    p_Q = 1 - chi2.cdf(Q, df) if df > 0 else None
    I2 = max(0, (Q - df) / Q) * 100 if Q > df and df > 0 else 0

    tau2 = 0
    if model == "random" and df > 0:
        tau2 = max(0, (Q - df) / (np.sum(weights) - np.sum(weights**2)/np.sum(weights)))
        weights = 1 / (variances + tau2)
        pooled_log = np.sum(weights * logs) / np.sum(weights)
        pooled_var = 1 / np.sum(weights)

    se = math.sqrt(pooled_var)
    z = pooled_log / se
    p = 2 * (1 - norm.cdf(abs(z)))

    ci_low = math.exp(pooled_log - 1.96 * se)
    ci_up = math.exp(pooled_log + 1.96 * se)

    effect_name = "pooled"
    if data_size > 1:
        return {
            "model": "Common effect model" if model == "fixed" else "Random effects model",
            effect_name: {
                f"value": math.exp(pooled_log),
                "ci_lower_value": ci_low,
                "ci_upper_value": ci_up,
            },
            "heterogeneity_info": {
                "tau_squared": tau2,
                "chi_squared": Q if df > 0 else None,
                "df": df if df > 0 else None,
                "p_value": p_Q if df > 0 else None,
                "i_squared": I2,
            },
            "overall_effect": {
                "overall_effect_z": z,
                "overall_effect_p": p,
            }
        },study_check_result
    else:
        return {
                "model": "Common effect model" if model == "fixed" else "Random effects model",
                   effect_name: {
                       f"value": None,
                       "ci_lower_value": None,
                       "ci_upper_value": None,
                   },
                   "heterogeneity_info": {
                       "tau_squared": None,
                       "chi_squared": None,
                       "df": None,
                       "p_value": None,
                       "i_squared": None,
                   },
                   "overall_effect": {
                       "overall_effect_z": None,
                       "overall_effect_p": None,
                   }
               }, study_check_result

def read_content(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    return content;

def meta_item(item):
    effect_type: str = item['effect_type'];
    title: str = item['title'];
    if effect_type.lower().__contains__('rr'):
        effect_type = 'RR';
    elif effect_type.lower().__contains__('or'):
        effect_type = 'OR';

    models = item['models'];
    studies = item['studies'];
    model_check_result = [];
    for model in models:
        model_type: str = model['model'];
        model_study_group: str = model['study_group'];
        if model_type.lower().__contains__('random'):
            model_type = "random"
        elif model_type.lower().__contains__("common"):
            model_type = "fixed";

        model_studies = [];
        filter_studies = [];
        if model_study_group.lower().__contains__("overall"):
            model_studies.extend(studies);
        else:
            for study in studies:
                sub_group: str = study['study_group'];
                pass_data = True;
                if  ('pass' in study):
                    pass_data = study['pass'];

                if model_study_group.lower() == (sub_group.lower()):
                    if pass_data:
                        model_studies.append(study);
                    else:
                        filter_studies.append(study);
        meta_compute_result,study_check_result = meta_analysis(model_studies, model_type, measure=effect_type);
        for study in filter_studies:
            name = study['study'];
            study_check_result.append({'name': name, 'eff_check': False, 'cli_lower_check': False, 'cli_upper_check': False,'data':study});
        compute_pool_result = meta_compute_result['pooled'];
        pool_result = model['pooled'];

        model_overall_effect = meta_compute_result['overall_effect'];
        model_heterogeneity_info = meta_compute_result['heterogeneity_info'];

        overall_effect = model['overall_effect'];
        heterogeneity_info = model['heterogeneity_info'];

        eff_check = False;
        if not ((pool_result['value'] is None) and (compute_pool_result['value'] is None)):
            eff_check = check_value_error(compute_pool_result['value'], pool_result['value'], 0.1, 0.1);

        cli_lower_check = False;
        if not ((pool_result['ci_lower_value'] is None) and (compute_pool_result['ci_lower_value'] is None)):
            cli_lower_check = check_value_error(compute_pool_result['ci_lower_value'], pool_result['ci_lower_value'], 0.1, 0.1);

        cli_upper_check = False;
        if not ((pool_result['ci_upper_value'] is None) and (compute_pool_result['ci_upper_value'] is None)):
            cli_upper_check = check_value_error(compute_pool_result['ci_upper_value'], pool_result['ci_upper_value'], 0.1, 0.1);

        overall_effect_z_check = check_value_error(model_overall_effect['overall_effect_z'], overall_effect['overall_effect_z'], 0.1, 0.1);
        overall_effect_p_check = check_value_error(model_overall_effect['overall_effect_p'], overall_effect['overall_effect_p'], 0.1, 0.1);

        tau_squared_check = check_value_error(model_heterogeneity_info['tau_squared'], heterogeneity_info['tau_squared'], 0.1, 0.1);
        chi_squared_check = check_value_error(model_heterogeneity_info['chi_squared'], heterogeneity_info['chi_squared'], 0.1, 0.1);
        df_check = check_value_error(model_heterogeneity_info['df'],heterogeneity_info['df'], 0.1, 0.1);
        p_value_check = check_value_error(model_heterogeneity_info['p_value'], heterogeneity_info['p_value'], 0.1, 0.1);
        i_squared_check = check_value_error(model_heterogeneity_info['i_squared'],heterogeneity_info['i_squared'], 0.1, 0.1);

        overall_effect_check = {'overall_effect_z':overall_effect_z_check,'overall_effect_p':overall_effect_p_check};
        heterogeneity_info_check = {'tau_squared_check':tau_squared_check,'chi_squared_check':chi_squared_check,'df_check':df_check,'p_value_check':p_value_check,'i_squared_check':i_squared_check};


        model_check_result.append({'model_type': model_type, 'name': model_study_group, 'eff_check': eff_check,'cli_lower_check': cli_lower_check,'cli_upper_check': cli_upper_check,
                                   'compute_pool_result':compute_pool_result,'pool_result':pool_result,
                                   'overall_effect':overall_effect,'heterogeneity_info':heterogeneity_info,
                                   'model_overall_effect':model_overall_effect,'model_heterogeneity_info':model_heterogeneity_info,
                                   'overall_effect_check':overall_effect_check,'heterogeneity_info_check':heterogeneity_info_check,
                                   'study_check_result':study_check_result});

    return model_check_result;

# ========== 示例 ==========
if __name__ == "__main__":

    response_txt = read_content('D:\\project\\zky\\paperAgent\\response.txt');
    results = json.loads(response_txt);
    for item in results:
        title: str = item['title'];
        model_check_result = meta_item(item);
        print(f" title is {title}, {model_check_result}")

        #print(f" item is {item}");

    '''
    studies = [
        {"events_experimental": 0, "n_experimental": 8, "events_control": 1, "n_control": 8},
        {"events_experimental": 0, "n_experimental": 25, "events_control": 1, "n_control": 25},
    ]

    res_fixed_rr = meta_analysis(studies, model="fixed", measure="RR")
    res_random_rr = meta_analysis(studies, model="random", measure="RR")
    res_fixed_or = meta_analysis(studies, model="fixed", measure="OR")

    print("固定效应 RR:", res_fixed_rr)
    print("随机效应 RR:", res_random_rr)
    print("固定效应 OR:", res_fixed_or)
    '''
