from openai import  OpenAI
from check.meta_trans import check_meta_analysis
from prompt_1.continue_meta_code import analyze_data;
from utils import content_utils;
from prompt_1.bin_meta_code import meta_item;
import json;
from utils.client_utils import get_client
import os;
from extract.extract_info import indify_paper
from extract.extract_info import check_outcome;

client = get_client();

def dump_result_to_file(result, filename: str = "extract_result_all.json"):
    """
    将 extract_result 以 JSON 格式写入文件。

    参数:
        result: 任意可序列化对象（如 list / dict）
        filename: 输出文件名（默认 extract_result.json）
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
        print(f"[OK] Result dumped to {filename}")
    except Exception as e:
        print(f"[ERROR] Failed to dump result: {e}")

# SR1, D:\\project\\zky\\paperAgent\\all_txt
def meta_analy(meta_name, data_path):
    #meta_name = "SR4";

    base_path = f"{data_path}\\{meta_name}";
    files = os.listdir(base_path);
    meta_array = [];
    paper_list = [];
    original_paper_list = [];
    paper_extract_info_s = [];
    index = 1;
    for file in files:
        if file.__contains__("meta"):
            continue;
        if not file.__contains__(".txt"):
            continue;

        path = base_path + "\\" + file;
        content = content_utils.read_content(path);
        content = content.replace("```json", "")
        content = content.replace("```", "");
        json_data = json.loads(content);

        append_path = path.replace(".txt", ".xlsx");

        if os.path.exists(append_path):
            append_content = content_utils.read_excel(append_path);
            content = content + "\n" + append_content;

        paper_list.append(json_data);
        original_paper_list.append(content);

        '''
        try:
            paper_extract_info = extract_info(json_data, "all");
            print(f" extract data is {paper_extract_info}");
        except Exception as e:
            paper_extract_info = extract_info(json_data, "all");
    
        paper_extract_info_s.append(paper_extract_info);
        '''
        meta_data = json_data["metadata"]
        meta_data['index'] = index;
        meta_array.append(meta_data);
        index = index + 1;


    file_path = f"{data_path}\\{meta_name}.txt";


    content = content_utils.read_content(file_path);
    content = content.replace("```json","")
    content = content.replace("```","");
    content = content.strip();
    json_data = json.loads(content);
    figs = json_data['Figs'];
    #fig = figs[2];
    #result = check_meta_analysis(fig, "check", model="gpt-5");
    #print(f"result is {result}");
    #result = check_meta_analysis(fig, "check");

    #print(f" fig is {figs} ");
    extract_result = check_meta_analysis(figs, "trans", model="gpt-5");
    print(f" extract_result is {extract_result}");

    results = extract_result;
    all_result = "";
    for item in results:
        studies = item['studies'];
        title = item['title'];
        #outcome_type = extract_outcome_type(title);
        #print(f" outcome_type is {outcome_type}");
        study_names = [];
        study_map = {};
        effect_type:str = item['effect_type'];
        #print(f" outcome_type is {outcome_type}");
        for study in studies:
            study_names.append(study['study'])
            study_map[study['study']] = study;

        try:
            indify_result = indify_paper(study_names, meta_array)
            print(f" indify_result is {indify_result}");
        except Exception as e:
            print("发生异常:", e)
            indify_result = indify_paper(study_names, meta_array)
            print(f" indify_result is {indify_result}");

        effect_type = effect_type.lower()

        for item in indify_result:
            if not item:
                continue;
            if not 'index' in item:
                continue;

            if 'title' in item:
                title = item['title'];
            elif 'Title' in item:
                title = item['Title'];

            study_name = item['study_name'];
            meta_study = study_map[study_name];
            index = item['index'];
            followup_time = meta_study['followup_time'];
            outcome = meta_study['outcome']
            meta_study['pass'] = True;
            input = {'outcome_type': outcome, 'followup_time': followup_time, "study_group": meta_study['study_group']};
            if 'mean_experimental' in meta_study:
                paper = paper_list[index - 1];
                original_paper = original_paper_list[index - 1];
                # 提取需要的值
                mean_exp = meta_study.get("mean_experimental")
                sd_exp = meta_study.get("sd_experimental")
                n_exp = meta_study.get("n_experimental")

                mean_ctrl = meta_study.get("mean_control")
                sd_ctrl = meta_study.get("sd_control")
                n_ctrl = meta_study.get("n_control")

                data = f"mean_experimental:{mean_exp},sd_experimental:{sd_exp},n_experimental:{n_exp},mean_control:{mean_ctrl},sd_control:{sd_ctrl},n_control:{n_ctrl}";
                input['data'] = data;
                if mean_exp is None:
                    meta_study.get("mean_experimental")

                meta_data = paper["metadata"]
                #print(f"{meta_data}");

                #paper_info = paper_extract_info_s[index - 1];

               # out_comes = paper_info['Outcomes']
               # outcomes_str1 = str(out_comes);
                result = check_outcome(input, original_paper, 'continue');
                print(f"result is {result} ");
                extraction_correct = result['extraction_correct']

                if not extraction_correct:
                    issues = result['issues'];
                    for issue in issues:
                        issue_field = issue['field'];
                        value = issue['value'];
                        if value == 'NONE':
                            meta_study['pass'] = False;
                            continue;
                        if not ((value is None) or (value == 0.0)):
                            meta_study[issue_field] = issue['value'];

                #print(f" study_name is {study_name}, data is {data} check outcome is {result}");
            elif 'events_experimental' in meta_study:
                study_name = item['study_name'];
                meta_study = study_map[study_name];
                paper = paper_list[index - 1];
                original_paper = original_paper_list[index - 1];

                # 提取需要的值
                events_experimental = meta_study.get("events_experimental")
                n_experimental = meta_study.get("n_experimental")
                # n_exp = meta_study.get("n_experimental")

                events_control = meta_study.get("events_control")
                n_control = meta_study.get("n_control")

                data = f"events_experimental:{events_experimental},n_experimental:{n_experimental},events_control:{events_control},n_control:{n_control}";
                input['data'] = data;

                # paper_info = extract_info(paper, "all");
               # paper_info = paper_extract_info_s[index - 1];

                meta_data = paper["metadata"]
                # print(f"{meta_data}");

               # out_comes = paper_info['Outcomes']
                #outcomes_str1 = str(out_comes);

                try:
                    result = check_outcome(input, original_paper, 'binary');
                    #print(f" study_name is {study_name}, data is {data} check outcome is {result}");
                except Exception as e:
                    print("发生异常:", e)
                    result = check_outcome(input, original_paper, 'binary');
                    #print(f" study_name is {study_name}, data is {data} check outcome is {result}");

                if not result is None:
                    extraction_correct = result['extraction_correct']
                    if not extraction_correct:
                        issues = result['issues'];
                        for issue in issues:
                            issue_field = issue['field'];
                            value = issue['value'];
                            if value == 'NONE':
                                meta_study['pass'] = False;
                                continue;
                            if not ((value is None) or (value == 0.0)):
                                meta_study[issue_field] = issue['value'];


    save_file_path = f"{data_path}\\extract_result_all_{meta_name}.json";
    dump_result_to_file(extract_result, save_file_path);

'''
count = 0;
for item in extract_result:
    effect_type:str = item['effect_type'];
    title: str = item['title'];
    studies = item['studies'];
    size = len(studies);
    count = count + 1;

    if size == 0:
        continue;

    
    first_study = studies[0];
    if not ('pass' in first_study):
        continue;
   

    data_pass_check = True;
    for item_study in studies:
        if not 'pass' in item_study:
            data_pass_check = False;

    if not data_pass_check:
        continue;

    study_check = 'events_control' in item['studies'][0];
    if study_check:
        #bin_meta_code 二元结局
        model_check_result = meta_item(item);
        print(f" title is {title}, {model_check_result}")
    else:
        #continue_meta_code 连续结局
        model_check_result = analyze_data(item,count);
        print(f" title is {title}, {model_check_result}")
'''

