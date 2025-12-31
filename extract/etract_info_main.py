import json;
import os
import json5


from extract.meta_extract_info import extract_all_info
from extract.extract_info import extract_info
from extract.extract_info import filter_instruct
import re

def extract_code_blocks(text):
    """
    从包含 ```json 或 ``` 的文本中提取代码块内容
    """
    pattern = r"```(?:json)?\s*(.*?)```"  # 匹配 ```json 或 ``` 的代码块
    blocks = re.findall(pattern, text, flags=re.DOTALL)
    return [block.strip() for block in blocks]

def read_content(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    return content;

def process_result(meta_path, dir):
    meta_article = read_content(meta_path);
    '''
    data_extract_result = extract_plain_info(meta_article, "data_extract");
    infos = data_extract_result['extracted_information']
    num = 0;
    fields_desc = "";
    for item in infos:
        num = num + 1;
        name = item['feild_name'];
        instruct = item['extract_instruct']
        txt = f"{num}.{name}:{instruct}";
        fields_desc = fields_desc + "\n" + txt;
        # print(f"{txt}");
    '''
    if meta_article.__contains__('````json'):
        contents = extract_code_blocks(meta_article);
        meta_article = contents[0];
    meta_article = meta_article.replace("```json", "");
    meta_article = meta_article.replace("```", "");
    json_content = json.loads(meta_article);
    #tables = json_content['tables']
    tables = json_content['tables']
    result = extract_info(tables, "original_table")
   # num = 1;
    fields_desc = "";
    fields = result['fields']
    for item in fields:
        #num = num + 1;
        name = item['field_name'];
        instruct = item['extract_instruct']
        txt = f"{name}";
        fields_desc = fields_desc + "\n" + txt;
        # print(f"{txt}");

    print(f" fields_desc is {fields_desc} ");
    filtered_fields_result = filter_instruct(fields_desc);
    filter_fields = filtered_fields_result['kept_fields'];
    field_map = {};
    for field in filter_fields:
        field_map[field] = field;
    #field_map = dict(fields);
    print(f" field_map is {field_map} ");

    data_instruct = "";
    num = 0;
    for item in fields:

        name = item['field_name'];
        if not field_map.__contains__(name):
            continue;
        num = num + 1;
        instruct = item['extract_instruct']
        txt = f"{num}.{name}:{instruct}";
        data_instruct = data_instruct + "\n" + txt;

    print(f" data_instruct is {data_instruct} ");
    #print(f" filtered_instruct is {filtered_instruct} ");
    #print(f"data_extract_result is {data_extract_result}")

    dir_files = os.listdir(dir);
    for dir_file in dir_files:
        if not dir_file.endswith(".txt"):
            continue;
        if dir_file.__contains__('extracted'):
            continue;

        file_path: str = dir + "\\" + dir_file;
        save_path = file_path.replace(".txt", "_extracted.txt");
        if os.path.exists(save_path):
            continue;
        print(f" process file {file_path}");
        new_article = read_content(file_path);
        extract_info_result = extract_all_info(new_article, data_instruct);


        with open(save_path, "w", encoding="utf-8") as f:
            f.write(str(extract_info_result))  # 如果是字典，可以用 str() 或 json.dumps()


