import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams['font.family'] = 'DejaVu Sans'  # 支持希腊字母
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号乱码问题
import matplotlib.patches as mpatches
import matplotlib;
matplotlib.use('Agg')
import numpy as np
from matplotlib.patches import Polygon



def plot_revman_style_forest(meta_result: dict, orignal_data:dict, title, save_path: str = "forest_plot_revman_fixed.png"):
    # 提取数据
    studies = meta_result['individual_studies']
    pooled = meta_result['pooled']

    pool_ci_lower_value = pooled['ci_lower_value'];
    pool_ci_upper = pooled['ci_upper'];

    if pool_ci_upper is None or pool_ci_lower_value is None:
        return;


    hetero = meta_result['heterogeneity_info']
    overall = meta_result.get('overall_effect', {})

    names = [s['study'] for s in studies]
    effects = np.array([float(s['effect']) for s in studies])
    ci_low = np.array([float(s['ci_lower']) for s in studies])
    ci_high = np.array([float(s['ci_upper']) for s in studies])
    weights = np.array([float(s.get('weight', 0)) for s in studies])

    # 左表需要的数据（示例，可替换为真实）
    # 如果你有真实 mean/sd/n 数据，请替换下面列表

    mean_exp = orignal_data['mean_exp'];
    sd_exp = orignal_data['sd_exp'];
    n_exp = orignal_data['n_exp'];

    mean_ctrl = orignal_data['mean_ctrl'];
    sd_ctrl = orignal_data['sd_ctrl'];
    n_ctrl = orignal_data['n_ctrl'];




    # y 位置（从上到下）
    n_studies = len(names)
    y_positions = np.arange(n_studies, 0, -1)  # e.g. [3,2,1]

    # 画布与子图布局（左表：右图 = 2.4:1）
    fig = plt.figure(figsize=(11, 4 + 0.6 * n_studies))
    gs = fig.add_gridspec(nrows=1, ncols=2, width_ratios=[2.6,1], wspace=0.05)

    # 左侧文本表格轴
    ax_table = fig.add_subplot(gs[0])
    ax_table.set_axis_off()

    # 绘制表头
    header_x = [0.02, 0.32, 0.42, 0.48, 0.62, 0.72, 0.78, 0.92]  # 归一化坐标（相对于 ax_table）
    headers = ["Study or Subgroup", "pharmacogenomic-guided\nMean", "SD", "Total",
               "usual care\nMean", "SD", "Total", "Weight"]
    for hx, h in zip(header_x, headers):
        ax_table.text(hx, 1.02, h, transform=ax_table.transAxes, ha='left', va='bottom', fontsize=9, fontweight='bold')

    # 绘制每行数据
    for yi, (name, me, se, ne, mc, sc, nc, w) in enumerate(zip(names, mean_exp, sd_exp, n_exp, mean_ctrl, sd_ctrl, n_ctrl, weights)):
        ypos_norm = 0.92 - yi * (0.8 / max(n_studies,1))  # 规范化纵向坐标
        ax_table.text(header_x[0], ypos_norm, name, transform=ax_table.transAxes, ha='left', va='center', fontsize=9)
        ax_table.text(header_x[1], ypos_norm, f"{me:.1f}", transform=ax_table.transAxes, ha='center', va='center', fontsize=9)
        ax_table.text(header_x[2], ypos_norm, f"{se:.1f}", transform=ax_table.transAxes, ha='center', va='center', fontsize=9)
        ax_table.text(header_x[3], ypos_norm, f"{ne}",   transform=ax_table.transAxes, ha='center', va='center', fontsize=9)
        ax_table.text(header_x[4], ypos_norm, f"{mc:.1f}", transform=ax_table.transAxes, ha='center', va='center', fontsize=9)
        ax_table.text(header_x[5], ypos_norm, f"{sc:.1f}", transform=ax_table.transAxes, ha='center', va='center', fontsize=9)
        ax_table.text(header_x[6], ypos_norm, f"{nc}",   transform=ax_table.transAxes, ha='center', va='center', fontsize=9)
        ax_table.text(header_x[7], ypos_norm, f"{w:.1f}%", transform=ax_table.transAxes, ha='center', va='center', fontsize=9)

    # 合并行（Total）
    total_ypos = 0.92 - n_studies * (0.8 / max(n_studies,1)) - 0.03
    ax_table.text(header_x[0], total_ypos, "Total (95% CI)", transform=ax_table.transAxes, ha='left', va='center', fontsize=9, fontweight='bold')
    ax_table.text(header_x[3], total_ypos, f"{meta_result.get('sample_sizes', {}).get('total_experimental', '')}", transform=ax_table.transAxes, ha='center', va='center', fontsize=9)
    ax_table.text(header_x[6], total_ypos, f"{meta_result.get('sample_sizes', {}).get('total_control', '')}", transform=ax_table.transAxes, ha='center', va='center', fontsize=9)
    ax_table.text(header_x[7], total_ypos, "100.0%", transform=ax_table.transAxes, ha='center', va='center', fontsize=9)

    # 右侧森林图轴
    ax = fig.add_subplot(gs[1])
    # 设置 y ticks 对齐左表
    ax.set_yticks(y_positions)
    ax.set_yticklabels([])  # y 标签已在左侧表里显示
    ax.invert_yaxis()
    ax.set_xlabel('Std. Mean Difference (IV, Random, 95% CI)')

    # x 轴范围根据数据自动扩展一点
    all_x = np.concatenate([ci_low, ci_high, [float(pooled['ci_lower_value']), float(pooled['ci_upper'])]])
    x_min, x_max = np.min(all_x), np.max(all_x)
    xpad = (x_max - x_min) * 0.12 if (x_max - x_min) > 0 else 1.0
    ax.set_xlim(x_min - xpad, x_max + xpad)

    # 绘制每项研究的CI线与方块（方块大小按 weight 缩放）
    # 将权重标准化到合理的 marker size
    if weights.max() > 0:
        sizes = 200 * (weights / weights.max())  # 可调整比例因子 200
    else:
        sizes = np.full_like(weights, 60)

    for xi, lo, hi, y, sz in zip(effects, ci_low, ci_high, y_positions, sizes):
        ax.hlines(y, lo, hi, color='black', linewidth=1)
        ax.plot(xi, y, marker='s', markersize=np.sqrt(sz), markeredgecolor='black', markerfacecolor='green')

    # 绘制合并效应（菱形）
    pooled_val = float(pooled['value'])
    pooled_low = float(pooled['ci_lower_value'])
    pooled_high = float(pooled['ci_upper'])
    diamond_coords = [
        (pooled_low, 0.0),
        (pooled_val, 0.2),
        (pooled_high, 0.0),
        (pooled_val, -0.2)
    ]
    diamond = Polygon(diamond_coords, closed=True, facecolor='black', edgecolor='black')
    ax.add_patch(diamond)
    # 标注 pooled 值与 CI
    ax.plot([pooled_low, pooled_high], [0,0], color='black', linewidth=1)

    # 垂直线（无效值）
    ax.axvline(0, linestyle='--', color='black', linewidth=0.8)

    # 在右侧加上数值标签（每项研究的 effect [ci]）
    for xi, lo, hi, y in zip(effects, ci_low, ci_high, y_positions):
        txt = f"{xi:.2f} [{lo:.2f}, {hi:.2f}]"
        ax.text(x_max + xpad*0.02, y, txt, va='center', ha='left', fontsize=8)

    # 合并行数值
    pooled_txt = f"{pooled_val:.2f} [{pooled_low:.2f}, {pooled_high:.2f}]"
    ax.text(x_max + xpad*0.02, 0, pooled_txt, va='center', ha='left', fontsize=9, fontweight='bold')

    # 添加异质性和总体效应信息在左下方表格区域（使用 fig.text 放置）
    hetero_text = (
        f"Heterogeneity: Tau²={hetero['tau_squared']:.2f}; "
        f"Chi²={hetero['chi_squared']:.2f}, df={hetero['df']} (P={hetero['p_value']:.3f}); "
        f"I²={hetero['i_squared']:.0f}%\n"
        f"Test for overall effect: Z={overall.get('overall_effect_z', np.nan):.2f} "
        f"(P={overall.get('overall_effect_p', np.nan):.2f})"
    )
    fig.text(0.02, 0.02, hetero_text, ha='left', va='bottom', fontsize=9)

    # 标题
    fig.suptitle(title, fontsize=11, y=0.98)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
   # print(f"✅ 修正后的森林图已保存：{save_path}")
# 使用示例
if __name__ == "__main__":
    # 您的数据
    data = {
        'individual_studies': [
            {
                'study': 'Agullo et al 2023',
                'effect': -1.0731374373878777,
                'se': 0.30444222894346534,
                'ci_lower': -1.6698332414901675,
                'ci_upper': -0.476441633285588,
                'weight': 29.031263855854938
            },
            {
                'study': 'Kraus et al 2024',
                'effect': -0.06700150483448068,
                'se': 0.23076139784805494,
                'ci_lower': -0.519285533638787,
                'ci_upper': 0.3852825239698257,
                'weight': 33.23667703265504
            },
            {
                'study': 'Thomas et al 2021',
                'effect': 0.04617665184232766,
                'se': 0.144283874325024,
                'ci_lower': -0.23661454538462273,
                'ci_upper': 0.32896784906927806,
                'weight': 37.73205911149002
            }
        ],
        'pooled': {
            'value': -0.31639103318403594,
            'ci_lower_value': -0.9059432914372622,
            'ci_upper': 0.27316122506919027
        },
        'heterogeneity_info': {
            'tau_squared': 0.21897595054502444,
            'chi_squared': 11.158959122900166,
            'df': 2,
            'p_value': 0.0037745294183204603,
            'i_squared': 82.07718141116186
        },
        'overall_effect': {
            'overall_effect_z': -1.0518406492232855,
            'overall_effect_p': 0.29287266571518655
        },
        'sample_sizes': {
            'total_experimental': 207,
            'total_control': 130,
            'total_participants': 337
        },
        'settings': {
            'effect_type': 'SMD',
            'model_type': 'random'
        }
    }

    # 绘制森林图
    plot_revman_style_forest(data,"Figure 2")