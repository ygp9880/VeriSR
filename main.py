from google import genai
from google.genai import types
import pathlib
import logging;
import os;
from utils.content_utils import read_content;
from extract.etract_info_main import process_result
from check.check_info import check_table
from check.meta_data_correct import meta_analy
from check.meta_check import meta_check
from rob2_meta.rob2_generate import generate
import argparse
import os
from dotenv import load_dotenv
from rob2_meta.rob2_refactor import refactor;
from report.rob_compare import compare;
from report.rob_compare import json_to_docx_multilevel_table;
from report.report_info2 import report_json;
from report.rob2_report import paper_to_doc
from report.report_info2 import wrong_field_report
from report.report_info2 import data_wrong_summary
from report.report_merge import merger
from report.report_info2 import rob2_summary_report
from report.report_info2 import meta_summary_report;

load_dotenv()

gemini_key = os.getenv("gemini_key");
print(f" gemini_key is {gemini_key} ");
client = genai.Client(api_key=gemini_key)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),                       # 输出到控制台
        logging.FileHandler("agent.log", encoding="utf-8")  # 输出到文件
    ]
)

extract_file_path = "prompt_extract_content.txt"

def process_pdf(file_name, input_prompt):
    save_file_name = file_name.replace(".pdf", ".txt");
    if os.path.exists(save_file_name):
        print(f" file {save_file_name} is processed");
        return ;

    #file_name = "SR1Hamiltonetal2020.pdf";e
    filepath = pathlib.Path(file_name)

    # Upload the PDF using the File API
    sample_file = client.files.upload(
      file=filepath,
    )

    logging.info(sample_file)
    #prompt=""

    response = client.models.generate_content(
      model="gemini-2.5-flash",
      contents=[sample_file, input_prompt])


    output_file = save_file_name
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(response.text)


# 读取整个文件内容
with open(extract_file_path, "r", encoding="utf-8") as f:
    extract_prompt = f.read()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="主程序")

    parser.add_argument("-dir", "--dir",  default="pdf", help="pdf")
    parser.add_argument("-m", "--meta_path", default="meta", help="meta")
    parser.add_argument("-n", "--meta_name", default="meta", help="meta")


    parser.add_argument("-c", "--command", required=True, default="process", help="process")
    parser.add_argument("-s", "--save_path", default="result",help="result")
    parser.add_argument("-t", "--type", default="result",help="result")

    parser.add_argument("-data", "--data_path", default="data", help="data")

    parser.add_argument("-r", "--rob2_path", default="meta", help="meta")


    #parser.add_argument("-n", "--meta_name", default="meta", help="meta")

    args = parser.parse_args()
    # 读取 parser 的参数
    input_dir = args.dir
    command = args.command
    save_path = args.save_path
    meta_path = args.meta_path;
    meta_name = args.meta_name
    data_path = args.data_path;

    rob2_path = args.rob2_path;

    type = args.type;

    print("dir       =", input_dir)
    print("command   =", command)
    print("save_path =", save_path)

    # python main.py -dir etal -c process
    # python #meta_file_path = "D:\\project\\zky\\paperAgent\\txt_new\\SR6.txt"  # 替换为你的文件路径
    # #process_result(meta_file_path,"D:\\project\\zky\\paperAgent\\txt_new\\SR6");
    # meta fenxi
    if command == "process":
        #python main.py -dir pdf  -c process -save_path = ''
        # 从pdf 提取文本
        files = os.listdir(input_dir)
        for file in files:
            file_path = input_dir + "\\" + file;
            process_pdf(file_path, extract_prompt);
            #print(f" file_path is {file_path} ");
    elif command == "extract":
        #python main.py -c extract -m D:\\project\\zky\\paperAgent\\txt_new\\SR6.txt -data D:\\project\\zky\\paperAgent\\txt_new\\SR6
        # 提取文档
        process_result(meta_path, data_path);
    elif command == "check_info":
        # 检查meta文章的table 数据, 如果一致则标注为一致，不一致，则标注错误信息。
        # -c  check_info  -m D:\project\zky\paperAgent\all_txt\SR1.txt  -data D:\project\zky\paperAgent\all_txt\SR1
        check_table(meta_path, data_path);
    elif command == "meta_data_correct":
        # extract_result_all_SR1
        # -c  meta_data_correct  -n SR1  -data D:\project\zky\paperAgent\all_txt
        meta_analy(meta_name,data_path);
    elif command == "meta_check":
        # SR1_meta_check_output
        # -c  meta_check  -n SR1  -data D:\project\zky\paperAgent\all_txt
        meta_check(meta_name, data_path);
    elif command == "rob2_generate":
        #-c  rob2_generate   -data D:\project\zky\paperAgent\all_txt\SR1 -s D:\project\zky\paperAgent\all_txt\SR1\rob2_result
        generate(data_path, save_path)
    elif command == "rob2_refactor":
        #-c  rob2_refactor   -data D:\project\zky\paperAgent\all_txt\SR1\rob2_result
        refactor(data_path);
    elif command == "rob2_compare":
        #-c  rob2_compare   -data D:\project\zky\paperAgent\all_txt\SR1\rob2_result -n SR1 -m D:\project\zky\paperAgent\all_txt\SR1.txt -s D:\project\zky\paperAgent\all_txt
        compare(meta_path, meta_name, data_path, save_path)
    elif command == "rob2_doc":
        # -c  rob2_doc -data D:\project\zky\paperAgent\all_txt\SR1_rob2_compare.txt -s D:\project\zky\paperAgent\report_doc\rob2.docx
        # rob2_compare.docx.
        json_str = read_content(data_path);
        json_to_docx_multilevel_table(json_str, save_path)
    elif command == "wrong_field_report" or command == "report_3_2_1":
        #-c wrong_field_report -n SR1 -data D:\project\zky\paperAgent\all_txt
        wrong_field_report(data_path, meta_name);
    elif command == "data_wrong_summary" or command == "report_2_2_3":
        #-c data_wrong_summary -n SR1 -data D:\project\zky\paperAgent\all_txt
        data_wrong_summary(data_path, meta_name);
    elif command == "report_2_3_4":
        #-c data_wrong_summary -n SR1 -data D:\project\zky\paperAgent\all_txt
        rob2_summary_report(data_path, meta_name);
    elif command == "report_2_4_4":
        # -c report_2_4_4 -n SR1 -data D:\project\zky\paperAgent\all_txt
        meta_summary_report(data_path, meta_name);
    elif command == "report_json":
        # -c report_json -m D:\project\zky\paperAgent\all_txt\SR1.txt -t report_1 -s D:\project\zky\paperAgent\all_txt\SR1_report_1.json
        report_json(meta_path,type,save_path,meta_name);
    elif command == "rob2_paper_doc":
        #-c rob2_paper_doc -r  D:\project\zky\paperAgent\all_txt\SR1\rob2_result\SR1Agulloetal2023.txt  -data D:\project\zky\paperAgent\all_txt\SR1\SR1Agulloetal2023.txt -s D:\project\zky\paperAgent\report_doc\SR1_1.docx
        #-c rob2_paper_doc -r  D:\project\zky\paperAgent\all_txt\SR1\rob2_result\SR1Agulloetal2023.txt  -data D:\project\zky\paperAgent\all_txt\SR1\SR1Agulloetal2023.txt -s D:\project\zky\paperAgent\report_doc\SR1_1.txt
        paper_to_doc(data_path, rob2_path,save_path);
    elif command == "merge":
        # -c merge    -n SR1  -data D:\project\zky\paperAgent\all_txt -s D:\project\zky\paperAgent\report_doc\SR1_output.docx
        merger(data_path,meta_name,save_path)


    # meta 相关数据的检查 meta_analysis.py
    # meta check meta_check.py


    '''
    elif command == "check_info":
        # meta_check
    elif command == "meta_analysis":
        # check_info , check data is
    elif command == "":
        # report
    '''





    '''
    elif command == "extract":

    elif command == "report":

    elif command == "merge":
    '''






