from typing import List, Dict
import os;
from utils import content_utils
import json

def compare_rob2(extracted: Dict, computed: Dict) -> List[Dict]:
    """
    Compare ROB2 results from paper extraction vs computed by framework.

    Parameters
    ----------
    extracted : dict
        Extracted ROB2 results from the article (simplified table with +/X/-)
    computed : dict
        Computed ROB2 JSON results from rob2 framework

    Returns
    -------
    List[Dict]
        A list of dictionaries with comparison results for each study and domain
    """
    # Mapping rob2 judgement to simplified symbols
    judgement_map = {
        "Low": "+",
        "Some concerns": "X",
        "High": "-"
    }

    results = []

    # Build a lookup for computed results
    computed_lookup = {}
    for study_json in computed.get("studies", []):
        study_name = study_json["study"]
        domain_map = {}
        for domain in study_json["domains"]:
            # Take the overall judgement for each domain
            domain_map[domain["index"]] = judgement_map.get(domain["judgement"], "?")
        # Overall
        domain_map["Overall"] = judgement_map.get(study_json.get("overall_judgement", "?"), "?")
        computed_lookup[study_name] = domain_map

    # Compare each row in extracted
    for row in extracted["rows"]:
        study_name = row[0]
        comparison = {"study": study_name, "domains": {}}
        if study_name not in computed_lookup:
            comparison["note"] = "Study not found in computed results"
        else:
            comp_domains = computed_lookup[study_name]
            for i, domain_symbol in enumerate(row[1:], 1):
                key = extracted["headers"][i]
                computed_symbol = comp_domains.get(i if i <= 5 else "Overall", "?")
                comparison["domains"][key] = {
                    "extracted": domain_symbol,
                    "computed": computed_symbol,
                    "match": domain_symbol == computed_symbol
                }
        results.append(comparison)

    return results


# 示例调用
extracted_rob2 = {
    "title": "Table 5. Risk of bias assessment.",
    "headers": ["Study", "D1", "D2", "D3", "D4", "D5", "Overall"],
    "rows": [
        ["Kraus et al", "+", "+", "+", "+", "+", "+"],
        ["Mosley et al", "+", "X", "-", "+", "+", "X"],
        ["Agullo et al", "+", "+", "+", "+", "+", "+"],
        ["Hamilton et al (2022)", "+", "+", "+", "+", "+", "+"],
        ["Thomas et al", "+", "+", "+", "-", "+", "-"],
        ["Hamilton et al (2020)", "+", "+", "+", "+", "+", "+"]
    ]
}

'''
computed_rob2 = {
    "studies": [
        {
            "study": "Kraus et al",
            "overall_judgement": "High",
            "domains": [
                {"index": 1, "judgement": "High"},
                {"index": 2, "judgement": "High"},
                {"index": 3, "judgement": "High"},
                {"index": 4, "judgement": "Low"},
                {"index": 5, "judgement": "Some concerns"}
            ]
        },
        # ...其他研究
    ]
}
'''

# 对比

'''
comparison_results = compare_rob2(extracted_rob2, computed_rob2)
for res in comparison_results:
    print(res)
'''
path = "D:\\project\\zky\\paperAgent\\all_txt\\SR1\\rob2_result";
files = os.listdir(path);
studies = [];
for file in files:
    rob2_file = path + "\\" + file;
   # content_utils.read_content(rob2_file);
    #print(f" rob2_file is {rob2_file}");
    content = content_utils.read_content(rob2_file);
    content_json = json.loads(content);
    rob2_obj = {};
    rob2_obj['overall_judgement'] = content_json['overall_judgement'];
    domains = content_json['domains'];
    judge_domains = [];
    index = 1;
    for domain in domains:
        judgement = domain['judgement'];
        data = {"index": index, "judgement": judgement};
        #print(f" judgement is {judgement}");
        index = index + 1;
        #print(f" data is {data}");
        judge_domains.append(data);

    rob2_obj['domains'] = judge_domains;
    study = '';
    if file.__contains__('Kraus'):
        study = 'Kraus et al';
    elif file.__contains__('Mosley'):
        study = 'Mosley et al';
    elif file.__contains__('Agullo'):
        study = 'Agullo et al'
    elif file.__contains__('Thomas'):
        study = 'Thomas et al'
    elif file.__contains__('Hamilton') and file.__contains__('2020'):
        study = 'Hamilton et al (2020)';
    elif file.__contains__('Hamilton') and file.__contains__('2022'):
        study = 'Hamilton et al (2022)';

    rob2_obj['study'] = study;
    studies.append(rob2_obj);

computed_rob2 = {"studies":studies};
comparison_results = compare_rob2(extracted_rob2, computed_rob2)
print(comparison_results)

