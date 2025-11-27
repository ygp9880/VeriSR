import json;
from prompt.continue_meta_code import analyze_data;
from utils import content_utils;
import math
from prompt.bin_meta_code import meta_item;
#SR3 SR6 SR7

def preprocess_for_json(data):
    """预处理数据使其适合JSON序列化"""
    if isinstance(data, dict):
        return {k: preprocess_for_json(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [preprocess_for_json(item) for item in data]
    elif isinstance(data, float) and math.isnan(data):
        return None
    elif data in ["False", "True"]:
        return data.lower() == "true"
    else:
        return data

def meta_check(file_name,meta_name):
    #meta_name = "SR4";
   # file_name = f"extract_result_all_{meta_name}.json";
    with open(file_name, 'r', encoding='utf-8') as f:
        extract_result = json.load(f)

    count = 0;
    all_result = [];
    for item in extract_result:
        effect_type: str = item['effect_type'];
        title: str = item['title'];
        studies = item['studies'];
        size = len(studies);
        count = count + 1;

        if size == 0:
            continue;


        study_check = 'events_control' in item['studies'][0];
        if study_check:
            # bin_meta_code 二元结局
            model_check_result = meta_item(item);
            print(f" title is {title}\n data: {item}\n result: {model_check_result}")

            all_result.append(model_check_result);
            # 将数据转成 JSON 字符串
            data_to_save = {
                "title": title,
                "data": item,
                "result": model_check_result
            }



            print("已保存到 output.json")

        else:
            # continue_meta_code 连续结局
            calculated_results, validation_results = analyze_data(item, count);
            print(f" title is {title}, {calculated_results}")
            all_result.append(validation_results);


    cleaned_data = preprocess_for_json(all_result)

    json_str = json.dumps(cleaned_data, default=str, ensure_ascii=False, indent=4)

    # 保存到文件
    with open(f"{meta_name}_output.json", "w", encoding="utf-8") as f:
        f.write(json_str)