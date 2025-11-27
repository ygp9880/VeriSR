import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
import json
import numpy as np
from scipy.stats import norm, chi2
from scipy import stats
from report.plot_meta_forest import plot_revman_style_forest;
import re;

# ===== 各类效应量计算函数 =====
def calculate_md(mean_exp, sd_exp, n_exp, mean_ctrl, sd_ctrl, n_ctrl):
    md = mean_exp - mean_ctrl
    se = np.sqrt(sd_exp**2 / n_exp + sd_ctrl**2 / n_ctrl)
    return md, se

def calculate_smd(mean_exp, sd_exp, n_exp, mean_ctrl, sd_ctrl, n_ctrl):
    # Cohen's d, Hedges' correction 可根据需要加
    pooled_sd = np.sqrt(((n_exp - 1) * sd_exp**2 + (n_ctrl - 1) * sd_ctrl**2) / (n_exp + n_ctrl - 2))
    smd = (mean_exp - mean_ctrl) / pooled_sd
    se = np.sqrt((n_exp + n_ctrl) / (n_exp * n_ctrl) + smd**2 / (2 * (n_exp + n_ctrl)))
    return smd, se

def calculate_rom(mean_exp, sd_exp, n_exp, mean_ctrl, sd_ctrl, n_ctrl):
    rom = np.log(mean_exp / mean_ctrl)  # log ratio of means
    se = np.sqrt(sd_exp**2 / (n_exp * mean_exp**2) + sd_ctrl**2 / (n_ctrl * mean_ctrl**2))
    return rom, se

def calculate_ci(effect, se, alpha=0.05):
    z = stats.norm.ppf(1 - alpha / 2)
    return effect - z * se, effect + z * se


def safe_float(value, default=np.nan):
    """将值转换为 float，如果失败返回默认值"""
    try:
        if isinstance(value, str):
            value = value.replace(',', '').strip()  # 去掉逗号和空格
        return float(value)
    except:
        return default

# ===== 主函数 =====
def meta_analysis(studies_data: List[Dict], effect_type: str = "SMD", model_type: str = "random") -> Dict:
    """
    通用Meta分析函数

    参数:
        studies_data: 每个研究的dict，包含 mean_experimental, sd_experimental, n_experimental,
                      mean_control, sd_control, n_control, study
        effect_type: "SMD", "MD", "ROM"
        model_type: "fixed" 或 "random"

    返回:
        dict: meta分析结果
    """
    n_studies = len(studies_data)
    effects, ses, weights_fixed = [], [], []

    # 计算各研究效应量
    for study in studies_data:
        if effect_type.upper() == "SMD":
            effect, se = calculate_smd(
                safe_float(study['mean_experimental']), safe_float(study['sd_experimental']), safe_float(study['n_experimental']),
                safe_float(study['mean_control']), safe_float(study['sd_control']), safe_float(study['n_control'])
            )
        elif effect_type.upper() == "MD":
            effect, se = calculate_md(
                safe_float(study['mean_experimental']), safe_float(study['sd_experimental']), safe_float(study['n_experimental']),
                safe_float(study['mean_control']), safe_float(study['sd_control']), safe_float(study['n_control'])
            )
        elif effect_type.upper() == "ROM":
            effect, se = calculate_rom(
                safe_float(study['mean_experimental']), safe_float(study['sd_experimental']), safe_float(study['n_experimental']),
                safe_float(study['mean_control']), safe_float(study['sd_control']), safe_float(study['n_control'])
            )
        else:
            raise ValueError("effect_type 必须是 SMD, MD 或 ROM")

        effects.append(effect)
        ses.append(se)
        weights_fixed.append(1 / se**2)

    effects = np.array(effects)
    ses = np.array(ses)
    weights_fixed = np.array(weights_fixed)

    # 固定效应合并效应量
    pooled_fixed = np.sum(weights_fixed * effects) / np.sum(weights_fixed)

    # 计算异质性 Q, I², tau²
    Q = np.sum(weights_fixed * (effects - pooled_fixed) ** 2)
    df = n_studies - 1
    I_squared = max(0, (Q - df) / Q) * 100 if Q > 0 else 0
    if Q > df:
        sum_w = np.sum(weights_fixed)
        sum_w_sq = np.sum(weights_fixed ** 2)
        tau_squared = (Q - df) / (sum_w - sum_w_sq / sum_w)
    else:
        tau_squared = 0

    # 随机效应权重
    weights_random = 1 / (ses**2 + tau_squared)
    pooled_random = np.sum(weights_random * effects) / np.sum(weights_random)
    pooled_se_random = np.sqrt(1 / np.sum(weights_random))

    # 根据选择的模型输出
    if model_type == "fixed":
        pooled, pooled_se = pooled_fixed, np.sqrt(1 / np.sum(weights_fixed))
        ci_lower, ci_upper = calculate_ci(pooled, pooled_se)
    elif model_type == "random":
        pooled, pooled_se = pooled_random, pooled_se_random
        ci_lower, ci_upper = calculate_ci(pooled, pooled_se)
    else:
        raise ValueError("model_type 必须是 fixed 或 random")

    # Z检验
    z_score = pooled / pooled_se
    p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))


    if n_studies > 1:
        return {
            'individual_studies': [
                {
                    'study': study['study'],
                    'effect': eff,
                    'se': se,
                    'ci_lower': calculate_ci(eff, se)[0],
                    'ci_upper': calculate_ci(eff, se)[1],
                    'weight': (w / np.sum(weights_random) * 100) if model_type == "random" else (
                                w / np.sum(weights_fixed) * 100)
                }
                for study, eff, se, w in
                zip(studies_data, effects, ses, weights_random if model_type == "random" else weights_fixed)
            ],
            "pooled": {
                "value": pooled,
                "ci_lower_value": ci_lower,
                "ci_upper": ci_upper
            },
            "heterogeneity_info": {
                "tau_squared": tau_squared,
                "chi_squared": Q,
                "df": df,
                "p_value": 1 - stats.chi2.cdf(Q, df) if df > 0 else 1,
                "i_squared": I_squared
            },
            "overall_effect": {
                "overall_effect_z": z_score,
                "overall_effect_p": p_value
            },
            "sample_sizes": {
                'total_experimental': sum(study['n_experimental'] for study in studies_data),
                'total_control': sum(study['n_control'] for study in studies_data),
                'total_participants': sum(study['n_experimental'] + study['n_control'] for study in studies_data)
            },
            "settings": {
                'effect_type': effect_type,
                'model_type': model_type
            }
        }
    else:
        return {
            'individual_studies': [
                {
                    'study': study['study'],
                    'effect': eff,
                    'se': se,
                    'ci_lower': calculate_ci(eff, se)[0],
                    'ci_upper': calculate_ci(eff, se)[1],
                    'weight': (w / np.sum(weights_random) * 100) if model_type == "random" else (
                            w / np.sum(weights_fixed) * 100)
                }
                for study, eff, se, w in
                zip(studies_data, effects, ses, weights_random if model_type == "random" else weights_fixed)
            ],
            "pooled": {
                "value": None,
                "ci_lower_value": None,
                "ci_upper": None
            },
            "heterogeneity_info": {
                "tau_squared": None,
                "chi_squared": None,
                "df": None,
                "p_value":None,
                "i_squared": None
            },
            "overall_effect": {
                "overall_effect_z": None,
                "overall_effect_p": None
            },
            "sample_sizes": {
                'total_experimental': sum(study['n_experimental'] for study in studies_data),
                'total_control': sum(study['n_control'] for study in studies_data),
                'total_participants': sum(study['n_experimental'] + study['n_control'] for study in studies_data)
            },
            "settings": {
                'effect_type': effect_type,
                'model_type': model_type
            }
        }


def validate_meta_analysis(provided_data: Dict, calculated_results: Dict, filter_studies, tolerance: float = 0.05) -> Dict:
    """
    验证提供的meta分析结果与计算结果的一致性

    参数:
    provided_data: 用户提供的数据
    calculated_results: 计算得出的结果
    tolerance: 允许的误差范围

    返回:
    dict: 验证结果
    """
    validation_results = {
        'overall_match': True,
        'individual_studies_validation': [],
        'pooled_results_validation': {},
        'sample_size_validation': {}
    }

    # 验证个别研究的SMD
    for i, study in enumerate(provided_data['studies']):
        calc_study = calculated_results['individual_studies'][i]
        provided_smd = study['Effect']['value']
        calc_smd = calc_study['effect']

        mean_experimental,sd_experimental, n_experimental,  mean_control, sd_control, n_control = safe_float(study['mean_experimental']), safe_float(study['sd_experimental']), safe_float(study['n_experimental']),safe_float(study['mean_control']), safe_float(study['sd_control']), safe_float(study['n_control']);
        smd_match = abs(provided_smd - calc_smd) <= tolerance
        validation_results['individual_studies_validation'].append({
            'study': study['study'],
            'provided_smd': provided_smd,
            'calculated_smd': calc_smd,
            'difference': abs(provided_smd - calc_smd),
            'mean_experimental':mean_experimental,
            'sd_experimental':sd_experimental,
            'n_experimental':n_experimental,
            'mean_control':mean_control,
            'sd_control':sd_control,
            'n_control':n_control,
            'match': smd_match
        })

        if not smd_match:
            validation_results['overall_match'] = False

    size = len(filter_studies);
    if size > 0:
        for filter_study in filter_studies:
            provided_smd = filter_study['Effect']['value']
            mean_experimental, sd_experimental, n_experimental, mean_control, sd_control, n_control = safe_float(
                filter_study['mean_experimental']), safe_float(filter_study['sd_experimental']), safe_float(
                filter_study['n_experimental']), safe_float(filter_study['mean_control']), safe_float(
                filter_study['sd_control']), safe_float(filter_study['n_control']);
            validation_results['individual_studies_validation'].append({
                'study': filter_study['study'],
                'provided_smd': provided_smd,
                'calculated_smd': None,
                'difference': None,
                'mean_experimental': mean_experimental,
                'sd_experimental': sd_experimental,
                'n_experimental': n_experimental,
                'mean_control': mean_control,
                'sd_control': sd_control,
                'n_control': n_control,
                'match': False
            })

        validation_results['overall_match'] = False


    # 验证合并结果
    provided_pooled = provided_data['pooled']
    calc_pooled = calculated_results['pooled']

    if not (calc_pooled['value'] is None):
        smd_match = abs(provided_pooled['value'] - calc_pooled['value']) <= tolerance
        ci_lower_match = abs(provided_pooled['ci_lower_value'] - calc_pooled['ci_lower_value']) <= tolerance
        ci_upper_match = abs(provided_pooled['ci_upper'] - calc_pooled['ci_upper']) <= tolerance

        validation_results['pooled_results_validation'] = {
            'smd': {
                'provided': provided_pooled['value'],
                'calculated': calc_pooled['value'],
                'difference': abs(provided_pooled['value'] - calc_pooled['value']),
                'match': smd_match
            },
            'ci_lower': {
                'provided': provided_pooled['ci_lower_value'],
                'calculated': calc_pooled['ci_lower_value'],
                'difference': abs(provided_pooled['ci_lower_value'] - calc_pooled['ci_lower_value']),
                'match': ci_lower_match
            },
            'ci_upper': {
                'provided': provided_pooled['ci_upper'],
                'calculated': calc_pooled['ci_upper'],
                'difference': abs(provided_pooled['ci_upper'] - calc_pooled['ci_upper']),
                'match': ci_upper_match
            }
        }

        if not (smd_match and ci_lower_match and ci_upper_match):
            validation_results['overall_match'] = False

        # 验证样本量
        provided_exp = provided_data['total_participants_experimental']
        provided_ctrl = provided_data['total_participants_control']
        calc_exp = calculated_results['sample_sizes']['total_experimental']
        calc_ctrl = calculated_results['sample_sizes']['total_control']

        validation_results['sample_size_validation'] = {
            'experimental': {
                'provided': provided_exp,
                'calculated': calc_exp,
                'match': provided_exp == calc_exp
            },
            'control': {
                'provided': provided_ctrl,
                'calculated': calc_ctrl,
                'match': provided_ctrl == calc_ctrl
            }
        }

        return validation_results
    else:

        validation_results['pooled_results_validation'] = {
            'smd': {
                'provided': provided_pooled['value'],
                'calculated': None,
                'difference': None,
                'match': False
            },
            'ci_lower': {
                'provided': provided_pooled['ci_lower_value'],
                'calculated': None,
                'difference': None,
                'match': False
            },
            'ci_upper': {
                'provided': provided_pooled['ci_upper'],
                'calculated': None,
                'difference': None,
                'match': False
            }
        }

        validation_results['overall_match'] = False


        # 验证样本量
        provided_exp = provided_data['total_participants_experimental']
        provided_ctrl = provided_data['total_participants_control']
        calc_exp = calculated_results['sample_sizes']['total_experimental']
        calc_ctrl = calculated_results['sample_sizes']['total_control']

        validation_results['sample_size_validation'] = {
            'experimental': {
                'provided': provided_exp,
                'calculated': calc_exp,
                'match': provided_exp == calc_exp
            },
            'control': {
                'provided': provided_ctrl,
                'calculated': calc_ctrl,
                'match': provided_ctrl == calc_ctrl
            }
        }

        return validation_results


def meta_analysis_heterog(data):
    """
    多研究随机效应 META 分析，计算异质性指标
    data: list of dicts, 每个研究：
        {
            'mean1': float,
            'sd1': float,
            'n1': int,
            'mean2': float,
            'sd2': float,
            'n2': int
        }
    返回 dict，包括 SMD、方差、Q、I²、Tau²、随机效应总体效应、SE、Z、P
    """
    k = len(data)
    d_list = []
    var_list = []

    # 1️⃣ 计算每个研究的 SMD 和方差
    for study in data:
        mean1, sd1, n1 = study['mean_experimental'], study['sd_experimental'], study['n_experimental']
        mean2, sd2, n2 = study['mean_control'], study['sd_control'], study['n_control']

        # pooled SD
        sp = np.sqrt(((n1 - 1) * sd1 ** 2 + (n2 - 1) * sd2 ** 2) / (n1 + n2 - 2))
        d = (mean1 - mean2) / sp

        # SMD 方差
        v = (n1 + n2) / (n1 * n2) + d ** 2 / (2 * (n1 + n2))

        d_list.append(d)
        var_list.append(v)

    d_array = np.array(d_list)
    var_array = np.array(var_list)
    w_fixed = 1 / var_array

    # 2️⃣ 固定效应加权平均
    theta_fixed = np.sum(w_fixed * d_array) / np.sum(w_fixed)

    # 3️⃣ 计算 Q
    Q = np.sum(w_fixed * (d_array - theta_fixed) ** 2)
    df = k - 1
    p_Q = 1 - chi2.cdf(Q, df)

    # 4️⃣ I²
    I2 = max(0, (Q - df) / Q * 100) if Q > df else 0

    # 5️⃣ Tau² (DerSimonian-Laird)
    sum_w = np.sum(w_fixed)
    sum_w2 = np.sum(w_fixed ** 2)
    denom = sum_w - sum_w2 / sum_w
    tau2 = max(0, (Q - df) / denom) if denom > 0 else 0

    # 6️⃣ 随机效应加权平均
    w_random = 1 / (var_array + tau2)
    theta_random = np.sum(w_random * d_array) / np.sum(w_random)
    se_random = np.sqrt(1 / np.sum(w_random))
    Z = theta_random / se_random
    p_Z = 2 * (1 - norm.cdf(abs(Z)))

    result = {
        "tau_squared": tau2,
        "chi_squared": Q,
        "df": df,
        "p_value": p_Q,
        "i_squared": I2,
        "overall_effect_z": Z,
        "overall_effect_p": p_Z
    }

    return result

def print_meta_analysis_results(results: Dict, pass_studies, validation: Dict = None):
    """
    打印meta分析结果的格式化输出
    """
    print("=" * 80)
    print("SMD META分析结果")
    print("=" * 80)

    print("\n个别研究结果:")
    print("-" * 60)
    for study in results['individual_studies']:
        print(f"研究: {study['study']}")
        print(f"  Effect: {study['effect']:.3f} (95% CI: {study['ci_lower']:.3f} to {study['ci_upper']:.3f})")
        print(f"  权重: {study['weight']:.1f}%")
        print()


    for study in pass_studies:
        print(f"研究: {study['study']} 在原始论文没有找到相应的结果，被过滤掉，验证不对")

    valid_size = len(results['individual_studies'])
    print("合并结果:")
    print("-" * 60)
    if valid_size > 1:
        pooled = results['pooled']
        print(f"合并Effect: {pooled['value']:.2f}")
        print(f"95%置信区间: {pooled['ci_lower_value']:.2f} to {pooled['ci_upper']:.2f}")

        overall_effect = results['overall_effect']
        print(f"Z分数: {overall_effect['overall_effect_z']:.2f}")
        print(f"P值: {overall_effect['overall_effect_p']:.3f}")

        print("\n异质性分析:")
        print("-" * 60)
        het = results['heterogeneity_info']
        print(f"Q统计量: {het['chi_squared']:.2f} (df = {het['df']})")
        print(f"I²: {het['i_squared']:.1f}%")
        print(f"τ²: {het['tau_squared']:.4f}")
        print(f"异质性P值: {het['p_value']:.3f}")

        print("\n样本量信息:")
        print("-" * 60)
        sample = results['sample_sizes']
        print(f"实验组总数: {sample['total_experimental']}")
        print(f"对照组总数: {sample['total_control']}")
        print(f"总参与者: {sample['total_participants']}")

    if validation:
        print("\n" + "=" * 80)
        print("验证结果")
        print("=" * 80)
        print(f"整体匹配: {'✓' if validation['overall_match'] else '✗'}")

        print("\n个别研究验证:")
        for study_val in validation['individual_studies_validation']:
            status = '✓' if study_val['match'] else '✗'
            if not (study_val['calculated_smd'] is None):
                print(f"{status} {study_val['study']}: 提供值={study_val['provided_smd']:.3f}, "f"计算值={study_val['calculated_smd']:.3f}, 差异={study_val['difference']:.3f}")
            else:
                print(f"{status} {study_val['study']}: 提供值={study_val['provided_smd']:.3f}, "f"计算值=None, 差异=None")
        if valid_size > 1:
            print("\n合并结果验证:")
            pooled_val = validation['pooled_results_validation']
            for key, val in pooled_val.items():
                status = '✓' if val['match'] else '✗'
                print(f"{status} {key.upper()}: 提供值={val['provided']:.3f}, "
                      f"计算值={val['calculated']:.3f}, 差异={val['difference']:.3f}")


def check_heterogeneity(meta_data, cal_data, tolerance=0.1):
    """
    输入: meta_data (dict)，包含 "studies" 和 "heterogeneity_info"
    tolerance: 允许的相对误差 (默认 0.01 = 1%)

    输出: {calculated, given, consistency}
    """
    #calculated = compute_heterogeneity(meta_data["studies"])
    given_heter = meta_data["heterogeneity_info"]
    given_overall = meta_data["overall_effect"]

    given_all = {**given_heter, **given_overall}

    cal_heter = cal_data["heterogeneity_info"]
    cal_overall = cal_data["overall_effect"]

    cal_all =  {**cal_heter, **cal_overall}



    consistency = {}
    for k in cal_all:
        if cal_all[k] is None:
            continue;

        if given_all[k] is None:
            continue;

        calc_val = abs(cal_all[k])
        given_val = abs(given_all[k])

        # 避免除零
        if given_val == 0:
            consistency[k] = (abs(calc_val - given_val) < tolerance)
        else:
            rel_error = abs(calc_val - given_val) / abs(given_val)
            consistency[k] = (rel_error <= tolerance)



    return {
        "calculated": cal_all,
        "given": given_all,
        "consistency": consistency
    }


def extract_figure_title(text: str) -> str:
    """
    提取 Fig. X 开头的标题部分，去掉后面的英文说明。
    保留 Fig. X 后面的标题直到第一个句号为止。

    Parameters
    ----------
    text : str
        原始文本，例如 "Fig. 5 Random-effects meta-analysis ..."

    Returns
    -------
    str
        清理后的标题，例如 "Fig. 5 Random-effects meta-analysis ..."
    """
    # 匹配 Fig. + 数字 + 空格 + 任意字符直到第一个句号
    match = re.match(r'(Fig\. \d+ .*?)\.', text)
    if match:
        return match.group(1)
    else:
        return text  # 如果不匹配，原样返回

# 主函数：分析您的数据
def extract_original_data(meta_data):
    """
    从Meta分析数据中提取实验组和对照组的均值、标准差和样本量。

    参数:
        meta_data (dict): 原始Meta分析JSON数据

    返回:
        dict: 包含 mean_exp, sd_exp, n_exp, mean_ctrl, sd_ctrl, n_ctrl
    """
    mean_exp = []
    sd_exp = []
    n_exp = []

    mean_ctrl = []
    sd_ctrl = []
    n_ctrl = []

    for study in meta_data['studies']:
        mean_exp.append(study['mean_experimental'])
        sd_exp.append(study['sd_experimental'])
        n_exp.append(study['n_experimental'])

        mean_ctrl.append(study['mean_control'])
        sd_ctrl.append(study['sd_control'])
        n_ctrl.append(study['n_control'])

    return {
        'mean_exp': mean_exp,
        'sd_exp': sd_exp,
        'n_exp': n_exp,
        'mean_ctrl': mean_ctrl,
        'sd_ctrl': sd_ctrl,
        'n_ctrl': n_ctrl
    }

def analyze_data(data, count):
    """
    分析用户提供的数据
    """
    # 您的数据
    original_data = extract_original_data(data);
    effect_type = data['effect_type'];
    model_type = data['model_type'];
    title = extract_figure_title(data['title']);

    if effect_type.lower().__contains__('smd'):
        effect_type = 'SMD';
    elif effect_type.lower().__contains__('md'):
        effect_type = 'MD';
    elif effect_type.lower().__contains__('rom'):
        effect_type = 'ROM';

    # 执行meta分析
    new_studies = [];
    filter_studies = [];
    for study in data['studies']:
        if not 'pass' in study:
            continue;
        data_pass = study['pass'];
        if  data_pass:
            new_studies.append(study);
        else:
            filter_studies.append(study);

    calculated_results = meta_analysis(new_studies, effect_type, model_type)
    #plot_revman_style_forest(calculated_results, original_data, title, save_path=f"forest_plot_revman_{count}.png");
    #print(f" calculated_results is {calculated_results}");
    #heterog_results = meta_analysis_heterog(data['studies']);

    hetero_check_result = check_heterogeneity(data, calculated_results);

    print(f" hetero_check_result is {hetero_check_result} ");

    # 验证结果
    data['studies'] = new_studies;

    validation_results = validate_meta_analysis(data, calculated_results, filter_studies)

    # 打印结果
    print_meta_analysis_results(calculated_results, filter_studies, validation_results)

    return calculated_results, validation_results


def read_content(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    return content;

# 运行分析
if __name__ == "__main__":

    response_txt = read_content('D:\\project\\zky\\paperAgent\\smd.txt');
    results = json.loads(response_txt);
    for item in results:
        analyze_data(item)
    #results, validation = analyze_data(data);