from dotenv import load_dotenv
import os
import logging;
import argparse;
from rob2_run import rob_run;
from report.report_info import extract_report_info;
from meta_check import meta_check
from utils.content_utils import read_content;

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),                       # 输出到控制台
        logging.FileHandler("mylog.log", encoding="utf-8")  # 输出到文件
    ]
)

def parse_args():
    """命令行参数解析"""
    parser = argparse.ArgumentParser(description="PDF Extractor")

    parser.add_argument("--command", type=str, default=None, help="要执行的命令")
    parser.add_argument("--meta_path", type=str, default=None, help="元数据路径")
    parser.add_argument("--data_path", type=str, default=None, help="PDF 数据目录")
    parser.add_argument("--save_path", type=str, default=None, help="SAVE 路径")

    return parser.parse_args()

def get_config():
    """从 .env 和命令行整理最终参数"""
    load_dotenv()

    args = parse_args()

    config = {
        "command": args.command or os.getenv("COMMAND", "default_cmd"),
        "meta_path": args.meta_path or os.getenv("META_PATH", "./meta"),
        "data_path": args.data_path or os.getenv("DATA_PATH", "./data"),
        "save_path":  args.save_path or os.getenv("DATA_PATH", "./save"),
        "file_path": args.save_path or os.getenv("DATA_PATH", "./save"),

    }

    logging.info(f"当前配置：{config}")
    return config

def main():
    # 1. 加载 .env

    logging.info("文件内容如下：")
    config = get_config()
    data_path = config["data_path"]
    save_path = config['save_path']
    file_path = config['file_path']
    command = config['command'];


    #meta_path = config['meta_path'];

    if command == 'rob':
        files = os.listdir(data_path);
        for file in files:
            pdf_file = "data/" + file;
            rob_run(data_path, file, save_path);
            #txt_file_name = pdf_file.replace(".pdf", ".txt");
    elif command == 'report':
        meta_content = read_content(file_path);
        report_1 = extract_report_info(meta_content, "report_1");
        print(f" report_1 is {report_1}");

        report_3_1 = extract_report_info(meta_content, "report_3_1");
        print(f" report_3_1 is {report_3_1}");
        report_3_2 = extract_report_info(meta_content, "report_3_2");
        print(f" report_3_2 is {report_3_2}");
        report_3_3 = extract_report_info(meta_content, "report_3_3");
        print(f" report_3_3 is {report_3_3}");
        report_3_4 = extract_report_info(meta_content, "report_3_4");
        print(f" report_3_4 is {report_3_4}");
        report_3_5 = extract_report_info(meta_content, "report_3_5");
        print(f" report_3_5 is {report_3_5}");
    elif command == 'check':
        files = os.listdir(data_path);
        for file in files:
            file_path = data_path + "\\" + file;
            meta_check(file_path, file);
        #process_result(meta_path, data_path);
        #extract_info_result = extract_all_info(new_article, data_instruct);





if __name__ == "__main__":
    main()