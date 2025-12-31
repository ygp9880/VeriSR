import os
import logging;
from openai import  OpenAI
from utils.client_utils import get_client;
from rob2_meta.ROB2_analysis import rob2_analysis;
from rob2_meta.ROB2_analysis import compute_overall_judgement

from utils.content_utils import write_str_to_file;
from extract.extract_info import extract_rob2_info
import json;

# 基本配置：输出到文件
logging.basicConfig(
    filename="rob2.log",           # 日志文件名
    level=logging.INFO,           # 日志级别：DEBUG / INFO / WARNING / ERROR / CRITICAL
    format="%(asctime)s - %(levelname)s - %(message)s",  # 日志格式
    datefmt="%Y-%m-%d %H:%M:%S",  # 时间格式
)


client = get_client();
 # 替换为你的文件路径

def read_content(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    return content;

#+,-,X,?;Low risk,High risk,Some concerns,Unclear
#SR1Agulloetal2023，domain2_deviations
if __name__ == "__main__":
    #file_path = "new_txt\\SR1Krausetal2023.txt"
    #SR1Agulloetal2023 domain2_deviations
    #file_path = "all_txt\\SR1\\SR1Agulloetal2023.txt";
    base_path = "rob2_run";
    files = os.listdir(base_path);
    save_base_path = "rob2_run_gpt";
    claude_model = "gpt-5";
    for file in files:
        domain2 = "domain2";

        save_path = save_base_path + "/" + file;
        if os.path.exists(save_path):
            continue;
        logging.info(f" file is {file}");
        logging.info(f" domain2 is {domain2} ");
        file_path = base_path + "/" + file;
        content = read_content(file_path);
        content = content.replace("```json","").replace("```","");
        result:str = extract_rob2_info(content);
        if result.__contains__('adhering'):
            domain2 = "domain2_deviations";
        #print(f" content is {content} ");
        #match_result = rob2_analysis(content, 'domain2', model="gemini-2.5-pro");
        #domain2_deviations

        match_1_result = rob2_analysis(content, 'domain1', model=claude_model);
        logging.info(f" domain1 is {match_1_result} ");
        #match_1_result = None;

        match_2_result = rob2_analysis(content, domain2, model=claude_model);
        logging.info(f" domain2 is {match_2_result} ");
        match_3_result = rob2_analysis(content, 'domain3', model=claude_model);
        logging.info(f" domain3 is {match_3_result} ");
        match_4_result = rob2_analysis(content, 'domain4', model=claude_model);
        logging.info(f" domain4 is {match_4_result} ");
        match_5_result = rob2_analysis(content, 'domain5', model=claude_model);
        logging.info(f" domain5 is {match_5_result} ");
        #print(f" match_result is {match_result} ");



        judgment_1 = match_1_result['domains']['domain_1']['judgment'];
        judgment_2 = match_2_result['domains']['domain_2']['judgment'];
        judgment_3 = match_3_result['domains']['domain_3']['judgment'];
        judgment_4 = match_4_result['domains']['domain_4']['judgment'];
        judgment_5 = match_5_result['domains']['domain_5']['judgment'];


        domain_1 = match_1_result['domains']['domain_1'];
        domain_2 = match_2_result['domains']['domain_2'];
        domain_3 = match_3_result['domains']['domain_3'];
        domain_4 = match_4_result['domains']['domain_4'];
        domain_5 = match_5_result['domains']['domain_5']

        domains = [domain_1, domain_2, domain_3,domain_4, domain_5];

        match_all = match_1_result;
        match_all['domains'] = domains;

        judgement_list = [judgment_1,judgment_2,judgment_3,judgment_4,judgment_5];

        overall = compute_overall_judgement(judgement_list)
        match_all['overall'] = overall;

        json_str = json.dumps(match_all, ensure_ascii=False, indent=4)
        write_str_to_file(save_path, json_str);

        logging.info(f" match_all is {match_all} ");
    '''
    data_json = json.loads(content);
    article_structures = data_json['article_structure'];
    for item in article_structures:
        title:str = item['title'];
        if title.lower().__contains__('methods'):
            #print(f" item is {item}");
            content_answer = rob2_analysis(content);
            print(f" content_answer is {content_answer} ");
    '''
    #content_answer = rob2_analysis(content);
    #print(f" content_answer is {content_answer} ");