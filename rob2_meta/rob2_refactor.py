#content_json['domains'][1]['Q2_3']['answer']
import os;
from utils.content_utils import read_content,write_str_to_file
import json;

from rob2_meta.ROB2_analysis import compute_overall_judgement;
from rob2_meta.ROB2_analysis import compute_domain2_judgement;
from rob2_meta.ROB2_analysis import compute_domain2_deviations_judgement;
from rob2_meta.ROB2_analysis import compute_domain3_judgement;
from rob2_meta.ROB2_analysis import compute_domain4_judgement;



YES = {"Yes".lower(), "Probably Yes".lower()}
YESNI = {"Yes".lower(), "Probably Yes".lower(), "No Information".lower()}
NO = {"No".lower(), "NO".lower(), "Probably No".lower()}
NONI = {"No".lower(), "NO".lower(), "Probably No".lower(), "No Information".lower()}
NI = {"No Information".lower(), "NO".lower()}

NA = "Not Applicable";

def extract_answer(domain2,key):
    answer = domain2[key]['answer']
    answer_str:str = answer;
    return answer_str.lower();



#干预措施依从
def refactor_domain2_allocation_effect(domain2):
    """
    修复干预措施依从性和分析相关的问题：
    - Q2_4 和 Q2_5 依赖 Q2_3
    - Q2_6 和 Q2_7 依赖前面问题答案
    """
    answer_q1 = extract_answer(domain2, 'Q2_1')
    answer_q2 = extract_answer(domain2, 'Q2_2')

    #Q2_3
    if not ((answer_q1 in YESNI) or (answer_q2 in YESNI)):
        domain2['Q2_3']['answer'] = NA;

    # Q2_4
    answer_q3 = extract_answer(domain2, 'Q2_3')
    if answer_q3 not in YES:
        domain2['Q2_4']['answer'] = NA

    # Q2_5
    answer_q4 = extract_answer(domain2, 'Q2_4')
    if answer_q4 not in YESNI:
        domain2['Q2_5']['answer'] = NA



    # Q2_6 & Q2_7
    answer_q6 = extract_answer(domain2, 'Q2_6')
    # 如果 Q2_6 是 N/PN/NI 才可能检查 Q2_7
    if answer_q6 not in NONI:
        domain2['Q2_7']['answer'] = NA

    return domain2


def refactor_domain2_compliance_effect(domain2):
    """
       修复干预措施依从性和分析相关的问题：
       - Q2_4 和 Q2_5 依赖 Q2_3
       - Q2_6
       """
    answer_q1 = extract_answer(domain2, 'Q2_1')
    answer_q2 = extract_answer(domain2, 'Q2_2')

    # Q2_3
    if not ((answer_q1 in YESNI) or (answer_q2 in YESNI)):
        domain2['Q2_3']['answer'] = NA;


    answer_q3 = extract_answer(domain2, 'Q2_3')
    answer_q4 = extract_answer(domain2, 'Q2_4')
    answer_q5 = extract_answer(domain2, 'Q2_5')
    #Q2_6
    if not ((answer_q3 in NONI) or (answer_q4 in YESNI) or (answer_q5 in YESNI)):
        domain2['Q2_6']['answer'] = NA

# =========================
# 领域3：缺失数据
# =========================
def refactor_domain3(domain3):
    answer_q1 = extract_answer(domain3, 'Q3_1')
    #Q3_2
    if answer_q1 not in NONI:
        domain3['Q3_2']['answer'] = NA

    #Q3_3
    answer_q2 = extract_answer(domain3, 'Q3_2')
    if answer_q2 not in NO:
        domain3['Q3_3']['answer'] = NA

    #Q3_4
    answer_q3 = extract_answer(domain3, 'Q3_3')
    if answer_q3 not in YESNI:
        domain3['Q3_4']['answer'] = NA

    return domain3

# =========================
# 领域4：结局测量偏倚
# =========================
def refactor_domain4(domain4):
    answer_q1 = extract_answer(domain4, 'Q4_1')
    #Q4_3
    if answer_q1 not in NONI:
        domain4['Q4_3']['answer'] = NA

    #Q4_4
    answer_q3 = extract_answer(domain4, 'Q4_3')
    if answer_q3 not in YESNI:
        domain4['Q4_4']['answer'] = NA


    answer_q4 = extract_answer(domain4, 'Q4_4')
    if answer_q4 not in YESNI:
        domain4['Q4_5']['answer'] = NA

    return domain4

def refactor(data_path):
    base_path = data_path;
    files = os.listdir(base_path);
    save_base_path = data_path
    for file in files:
        full_path = base_path + "\\" + file;
        content = read_content(full_path);
        content_json = json.loads(content);
        domain2 = content_json['domains'][1];

        size = len(domain2);
        if size == 8:
            refactor_domain2_allocation_effect(domain2);
            compute_domain2_judgement(content_json);
        else:
            refactor_domain2_compliance_effect(domain2);
            compute_domain2_deviations_judgement(content_json);

        domain3 = content_json['domains'][2];
        domain4 = content_json['domains'][3];

        refactor_domain3(domain3)
        refactor_domain4(domain4);

        compute_domain3_judgement(content_json);
        compute_domain4_judgement(content_json);

        judgment_1 = content_json['domains'][0]['judgment'];
        judgment_2 = content_json['domains'][1]['judgment'];
        judgment_3 = content_json['domains'][2]['judgment'];
        judgment_4 = content_json['domains'][3]['judgment'];
        judgment_5 = content_json['domains'][4]['judgment'];

        judgement_list = [judgment_1, judgment_2, judgment_3, judgment_4, judgment_5];

        overall = compute_overall_judgement(judgement_list)
        content_json['overall'] = overall;

        save_file_path = save_base_path + "\\" + file;

        json_str = json.dumps(content_json, ensure_ascii=False, indent=4)

        write_str_to_file(save_file_path, json_str);



    #print(f" size is {size}");
    #print(f" domains is {domains}");
    #domain2 = content_json['domains'][1];
    #refactor_domain2_compliance(domains);
    #print(f" d");
    #for domain in domains:
    #refactor_doamin2(domain2);
    #print(f"value is ");
    #print(f" full_path is {full_path}");
    #print(f" content is {content}");