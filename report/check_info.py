from openai import  OpenAI
import json;
import os;
from utils import content_utils;
from prompt.meta_analysis import check_meta_analysis
from prompt.extract_info import indify_paper

client = OpenAI(base_url='https://api.openai-proxy.org/v1', api_key='sk-p8KW4EtRdh7i2MWf9o7YmmQZihySS5HA5D0Z1iEdddtLURpJ');

def read_content(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    return content;

def generate_meta_table_prompt(table_txt: str) -> str:
    """
    生成用于提取META论文原始研究信息的Prompt。

    参数:
        paper_text (str): 论文文本，包括表格内容和正文。

    返回:
        str: 可以直接发送给大模型的Prompt。
    """

    prompt = f"""
你是一个擅长从医学学术论文中提取结构化信息的助手。任务如下：

1. 我将提供一篇包含表格的论文文本。
2. 请先从所有 tables 中筛选出 **与原始研究信息相关的表格, **，这些表格通常包含每个研究的基本信息（例如作者、年份），而不是 META 分析汇总结果跟rob2检查结果。
3. 对每个筛选出的表格，请提取每一行的数据，至少包括：
   - 作者 (author)
   - 年份 (year)   
4. 最终返回 **JSON 格式**，按照下面模板组织：

{{
  "tables": [
    {{
      "table_index": "表格索引,需要是整数",
      "table_title": "表格标题",
      "studies": [
        {{
          "author": "作者姓名",
          "year": "年份",          
        }},
        ...
      ]
    }},    ...
  ]
}}

注意事项：
- 只提取原始研究信息，不要提取 META 分析汇总数据。
- 如果表格中缺失某个字段，可以填为空字符串 ""。
- 确保 JSON 语法正确，可直接解析。
- 尽量完整提取表格中的每一行信息。

论文的表格内容如下：
\"\"\"
{table_txt}
\"\"\"

请根据以上要求处理论文文本，并返回JSON。
"""

    return prompt


def extract_table(table_txt):

    prompt = generate_meta_table_prompt(table_txt)
    response = client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": "你是一个擅长从医学学术论文中提取结构化信息的助手"},
            {"role": "user", "content": prompt}
        ]
    )

    response_text = response.choices[0].message.content
    response_text = response_text.replace("```json", "")
    response_text = response_text.replace("```", "");
    print(f" response is {response_text}")
    #match_result = json.loads(response_text)

   # response_text = response.text;
   # response_text = response_text.replace("```json", "")
    #response_text = response_text.replace("```", "");
   # print(f' match_result is {response_text}')
   # match_result = json.loads(response_text)

    return response_text


def extract_table_result(basePath, name):
    meta_path = basePath + "\\" + name +".txt";
    cache_path = f"{basePath}\\{name}_table_index_info.txt";
    if os.path.exists(cache_path):
        cache_result_content = content_utils.read_content(cache_path);
        result = json.loads(cache_result_content)
        return result;

    content = content_utils.read_content(meta_path);
    result = json.loads(content)
    tables = result['tables'];
    response_text = extract_table(tables);
    content_utils.write_str_to_file(cache_path, response_text);
    return json.loads(response_text)

def meta_read(basePath, name):
    dir = f"{basePath}\\{name}";
    files = os.listdir(dir);
    meta_array = [];
    paper_list = [];
    for file in files:
        if file.__contains__("meta"):
            continue;
        if not file.__contains__(".txt"):
            continue;
        path = dir + "\\"+ file;
        content = content_utils.read_content(path);
        json_data = json.loads(content);
        paper_list.append(json_data);
        meta_data = json_data["metadata"]
        meta_array.append(meta_data);
    return meta_array,paper_list;

def build_verification_prompt(extracted_data_json: str, original_text: str) -> str:
    """
    构造一个用于验证从Meta分析文章中抽取数据是否正确的Prompt。

    参数：
        extracted_data_json (str): 抽取的数据（JSON字符串）
        original_text (str): 原文内容

    返回：
        str: 可直接用于大模型调用的完整Prompt
    """
    prompt = f"""
You are an expert assistant for biomedical literature verification.

Task: Check whether the extracted data is consistent with the information in the provided original text (from a meta-analysis article).

Input:
1. Extracted data (JSON):
{extracted_data_json}

2. Original text (from the article):
\"\"\" 
{original_text}
\"\"\"

Requirements:
- Treat each key (column) in the extracted data as an independent field that must be verified for correctness.
- For each column, carefully check whether its value matches the corresponding information described in the original text.
- If any part of the extracted data is inconsistent, incorrect, or missing, point out exactly what is wrong and provide the correct value based on the original text.
- Ignore fields related to author names or study names or Study design (e.g., "Author", "Study", "Study name").
- If all items are consistent, simply reply: "consistent".
- Do not add extra explanation if it is consistent.

Output format:
{{
  "result": "consistent" or "inconsistent",
  "details": "If inconsistent, explain exactly which fields differ and what the correct value should be."
}}
"""
    return prompt.strip()

def verification_data(extracted_data_json: str, original_text: str):

    prompt = build_verification_prompt(extracted_data_json, original_text)
    response = client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": "你是一个擅长从医学学术论文中提取结构化信息的助手"},
            {"role": "user", "content": prompt}
        ]
    )

    response_text = response.choices[0].message.content
    response_text = response_text.replace("```json", "")
    response_text = response_text.replace("```", "");
    print(f" response is {response_text}")
    #match_result = json.loads(response_text)

   # response_text = response.text;
   # response_text = response_text.replace("```json", "")
    #response_text = response_text.replace("```", "");
   # print(f' match_result is {response_text}')
   # match_result = json.loads(response_text)

    return response_text

def check_index_field(indify_result):
    """
    检查 indify_result 列表中的每个字典是否包含 'index' 键。
    返回：
        True  -> 所有元素都有 'index'
        False -> 有元素缺少 'index'
    """
    if not isinstance(indify_result, list):
        return False

    for item in indify_result:
        if not isinstance(item, dict):
            return False
        if 'index' not in item:
            return False

    return True


if __name__ == "__main__":
    path = "D:\\project\\zky\\paperAgent\\all_txt\\SR1.txt";
    base_path = "D:\\project\\zky\\paperAgent\\all_txt"
    meta_name = "SR1";

    meta_content,paper_list = meta_read(base_path,meta_name);
    print(f" meta_content is {meta_content} ");

    meta_path = base_path + "\\" + meta_name + ".txt";
    content = content_utils.read_content(meta_path);
    result = json.loads(content)
    original_tables = result['tables'];

    result = extract_table_result(base_path, meta_name);
    tables = result['tables'];
    index_map = {};
    for table in tables:
        index = table['table_index']
        table_item = original_tables[index-1];
        headers = table_item['headers'];
        new_header = headers + ['check'];

        new_table = {};
        new_table['headers'] = new_header;
        new_table['title'] = table_item['title'];
        rows = table_item['rows'];
        #print(f" headers is {headers} ");
        count = 0;
        new_rows = [];
        new_table['data'] = new_rows;
        for row in rows:
            study = table['studies'][count]['author'];
            study = content_utils.remove_dot_bracket(study);
            if not index_map.__contains__(study):
                #print(f" row is {row}, study is {study} ");
                indify_result = indify_paper(study, meta_content)
                check_result = check_index_field(indify_result);
                if not check_result:
                    # repeate call
                    indify_result = indify_paper(study, meta_content)
                paper_indexs = [item['index'] for item in indify_result];
                index_map[study] = paper_indexs;

            paper_indexs = index_map[study];
            check_result = [];

            data = f"{headers}\n{row}";
            check = '';
            for parper_index in paper_indexs:
                paper = paper_list[parper_index - 1];
                if check == 'consistent':
                    continue;
                verify_result = verification_data(data, paper);
                if not verify_result.__contains__('inconsistent'):
                    check = 'consistent'
                else:
                    result_json = json.loads(verify_result);
                    check = result_json['result'];
                    if check != 'consistent':
                        check = result_json['details'];
            new_row = row + [check];
            new_rows.append(new_row);
                #print(f" verify_result is {verify_result} ");
                #print(f" row is {data}, study is {study},  paper_indexs is {paper_indexs} ");
            count = count + 1;

        print(f" new_table is {new_table}");



