from openai import  OpenAI
import json;
import os;
from utils import content_utils;
client = OpenAI(base_url='https://api.openai-proxy.org/v1', api_key='sk-p8KW4EtRdh7i2MWf9o7YmmQZihySS5HA5D0Z1iEdddtLURpJ');

import openai


#一. Evaluation Summary
def extract_meta_analysis_info(article_text: str) -> str:
    """
    Extract structured information from a systematic review / meta-analysis article.

    Parameters:
        article_text (str): Full text or relevant excerpt of the meta-analysis article.
        model (str): LLM model to use. Default is 'gpt-5-mini'.

    Returns:
        str: JSON string with extracted information (Title, Objective, Sample_size, Inclusion_criteria, Main_results, Notes)
    """

    # Prompt template
    prompt = f"""
You are an expert biomedical literature extraction assistant.  
Extract structured information from the following systematic review / meta-analysis article.

Article content:
\"\"\"
{article_text}
\"\"\"

Requirements:
1. Return **only JSON** in the following format:

{{
  "Title": "",
  "Objective": "",
  "Sample_size_total": "",
  "Number_of_studies_included": "",
  "Inclusion_criteria": {{
    "Population": "",
    "Intervention": "",
    "Comparison": "",
    "Outcome": ""
  }},
  "Main_results": [
    "Result sentence 1",
    "Result sentence 2",
    "Result sentence 3"
  ],
  "Notes": ""
}}

2. Each item in "Main_results" must be a **single concise sentence** summarizing one study finding. Include effect size (SMD, CI, p-value) if provided.  
3. Leave fields empty ("") if data is not available.  
4. All extracted content must come directly from the article.  
5. Do not include any extra commentary or explanation.
"""
    return prompt


def generate_extraction_prompt(content: str) -> str:

    """
    1. 文献检索审核

    生成用于提取文献检索与筛选信息的 PROMPT，返回英文字段的 JSON，
    并针对每个字段提供抽取说明。

    Args:
        content: 原始文本内容（例如论文方法部分的描述）

    Returns:
        prompt: 给大模型使用的字符串
    """
    prompt = f"""
You are an expert in systematic reviews and meta-analyses. 
Your task is to extract information from the provided text and summarize it into four fields in **English**: 
1) Search_Strategy, 2) Screening_Process, 3) Results_Presentation, 4) Methodology_Summary.

Extraction Instructions for each field based on the provided text:

1. Search_Strategy:
   - Extract information about the databases searched (names), search date ranges, and search terms/strategies.
   - Include any details that ensure reproducibility, such as keywords, Boolean operators, and database coverage.

2. Screening_Process:
   - Extract details about how the literature screening was conducted, including reviewers involved.
   - Include methods for resolving disagreements (e.g., third-party arbitration).

3. Results_Presentation:
   - Extract information on how the study selection results were presented.
   - Include key numbers from PRISMA flowchart (records identified, duplicates removed, screened, excluded, included studies).
   - Include reasons for exclusion if mentioned.

4. Methodology_Summary:
   - Summarize the overall methodological quality of the search and screening process.
   - Highlight aspects such as transparency, standardization, bias minimization, and adherence to guidelines (e.g., PRISMA).

Return the result strictly in **JSON format** with the following keys: 
"Search_Strategy", "Screening_Process", "Results_Presentation", "Methodology_Summary".
Do not include any information outside of these fields.
If any field information is missing, return null for that field.

Input Text:
\"\"\"{content}\"\"\"

Example Output:
{{
  "Search_Strategy": "Authors searched four core databases (Medline, Embase, Cochrane, Web of Science) covering the main literature sources, with specific cutoff dates (Medline to 30 May 2024, Embase to 31 May 2024, Cochrane and Web of Science to 3 June 2024), and provided detailed search terms combining keywords and Boolean operators to ensure reproducibility.",
  "Screening_Process": "Two reviewers (SJ and MB) independently screened the literature, with disagreements resolved by a third reviewer (KL).",
  "Results_Presentation": "PRISMA 2020 flowchart clearly illustrates the selection process: 2,496 records identified, 535 duplicates removed, 1,961 records screened, 1,952 excluded, and 6 RCTs included; reasons for 3 full-text exclusions (e.g., results unavailable, no control group) are provided.",
  "Methodology_Summary": "The literature search and screening process is highly standardized and transparent, using dual independent screening, third-party arbitration, and PRISMA 2020 flowchart presentation, minimizing selection bias."
}}
"""
    return prompt

def generate_quality_extraction_prompt(content: str) -> str:
    """
    生成用于提取系统评价/Meta分析结论稳健性及证据质量信息的 PROMPT，
    返回四个英文字段的 JSON。

    Args:
        content: 原始文本内容（如敏感性分析、发表偏倚、证据质量和审核意见小结部分）

    Returns:
        prompt: 给大模型使用的字符串
    """
    prompt = f"""
You are an expert in systematic reviews and meta-analyses. 
Your task is to extract information from the provided text and summarize it into four fields in **English**: 
1) Sensitivity_Analysis, 2) Publication_Bias, 3) Evidence_Quality, 4) Methodology_Summary.

Extraction Instructions for each field based on the provided text:

1. Sensitivity_Analysis:
   - Extract information on whether sensitivity analyses were conducted.
   - Note if any important sensitivity analyses (e.g., excluding certain studies) are missing.
   - Mention the implications of missing sensitivity analyses for result stability.

2. Publication_Bias:
   - Extract information on whether publication bias was assessed.
   - Mention the number of included studies and whether any methods for assessing bias are appropriate or invalid.

3. Evidence_Quality:
   - Extract information on how the certainty/quality of evidence was evaluated.
   - Include frameworks or tools used (e.g., GRADE), any tables or summaries provided, and any limitations in reporting.

4. Methodology_Summary:
   - Summarize the overall methodological quality regarding robustness and evidence assessment.
   - Highlight any strengths or notable shortcomings.

Return the result strictly in **JSON format** with the following keys: 
"Sensitivity_Analysis", "Publication_Bias", "Evidence_Quality", "Methodology_Summary".
Do not include any information outside of these fields.
If any field information is missing, return null for that field.

Input Text:
\"\"\"{content}\"\"\"

Example Output:
{{
  "Sensitivity_Analysis": "No sensitivity analyses were reported, particularly for high-heterogeneity outcomes such as pain intensity. Missing these analyses limits the assessment of the robustness of conclusions.",
  "Publication_Bias": "Publication bias was not assessed. Given that only 3 and 2 studies were included in the respective meta-analyses, any formal assessment would be invalid or misleading, so omission aligns with methodological guidelines.",
  "Evidence_Quality": "The GRADE framework was used to assess evidence certainty, with each study outcome rated in Table 4. Although a Summary of Findings table for combined effect sizes was not provided, the evaluation reflects a structured consideration of evidence quality.",
  "Methodology_Summary": "The study shows notable shortcomings in exploring conclusion robustness but provides a standardized assessment of evidence quality."
}}
"""
    return prompt

def generate_data_extraction_prompt(content: str) -> str:
    """
    生成用于提取系统评价/Meta分析数据提取流程与内容信息的 PROMPT，
    返回三个英文字段的 JSON。

    Args:
        content: 原始文本内容（如数据提取流程、提取内容和方法学评价部分）

    Returns:
        prompt: 给大模型使用的字符串
    """
    prompt = f"""
You are an expert in systematic reviews and meta-analyses. 
Your task is to extract information from the provided text and summarize it into three fields in **English**: 
1) Extraction_Process, 2) Extracted_Contents, 3) Methodology_Summary.

Extraction Instructions for each field based on the provided text:

1. Extraction_Process:
   - Extract information on how data extraction was conducted.
   - Include details such as use of templates, independent reviewers, and methods for resolving disagreements.
   - Mention any procedures for obtaining missing data from original study authors.

2. Extracted_Contents:
   - Extract information on what data items were collected.
   - Include study characteristics, participant characteristics, interventions, outcomes, and any other relevant variables.
   - Note if the extracted data covers all core information needed for systematic review analyses.
Return the result strictly in **JSON format** with the following keys: 
"Extraction_Process", "Extracted_Contents".
Do not include any information outside of these fields.
If any field information is missing, return null for that field.

Input Text:
\"\"\"{content}\"\"\"

Example Output:
{{
  "Extraction_Process": "Data extraction was conducted using an Excel-based template, independently by two reviewers, with a third reviewer resolving disagreements. Authors of studies were contacted to obtain missing data.",
  "Extracted_Contents": "Extracted items included study author, publication year, title, design, sample size, country, participant characteristics (age, gender, ethnicity, type of pain), interventions (opioids prescribed, genetic tests performed), genes tested, and all measured outcomes. Data were fully captured in Tables 2, 3, and 4, covering all core information for systematic review analysis.",
  
}}
"""
    return prompt

def generate_risk_of_bias_prompt(content: str) -> str:
    """
    生成用于提取系统评价/Meta分析偏倚风险评估信息的 PROMPT，
    返回四个英文字段的 JSON。

    Args:
        content: 原始文本内容（如工具选择、评估过程、结果呈现与应用）

    Returns:
        prompt: 给大模型使用的字符串
    """
    prompt = f"""
You are an expert in systematic reviews and meta-analyses. 
Your task is to extract information from the provided text and summarize it into four fields in **English**: 
1) Tool_Selection, 2) Assessment_Process, 3) Results_Presentation, 4) Methodology_Summary.

Extraction Instructions for each field based on the provided text:

1. Tool_Selection:
   - Extract information about the risk of bias assessment tool used.
   - Mention whether the tool choice is appropriate for the included study designs.

2. Assessment_Process:
   - Extract details on how the risk of bias assessment was conducted.
   - Include independent reviewers, third-party arbitration, and any mention of reviewer training.

3. Results_Presentation:
   - Extract information on how risk of bias results were presented (e.g., tables, visualizations).
   - Include any decisions made based on risk of bias (e.g., exclusion of high-risk studies) and rationale.


Return the result strictly in **JSON format** with the following keys: 
"Tool_Selection", "Assessment_Process", "Results_Presentation"
Do not include any information outside of these fields.
If any field information is missing, return null for that field.

Input Text:
\"\"\"{content}\"\"\"

Example Output:
{{
  "Tool_Selection": "The study appropriately used the Cochrane Risk of Bias 2.0 (RoB 2.0) tool for assessing randomised controlled trials.",
  "Assessment_Process": "Two reviewers independently carried out the risk of bias assessment, with a third reviewer resolving disagreements. No information was provided regarding reviewer training.",
  "Results_Presentation": "Risk of bias was evaluated across five domains and visualized in Table 5. The study by Mosley et al. with high risk of bias was excluded from the meta-analysis to avoid contamination of pooled results."  
}}
"""
    return prompt

def generate_meta_analysis_prompt(content: str) -> str:
    """
    生成用于提取Meta分析方法信息的 PROMPT，
    返回四个英文字段的 JSON。

    Args:
        content: 原始文本内容（如效应量选择、模型选择、异质性评估、数据处理和软件使用）

    Returns:
        prompt: 给大模型使用的字符串
    """
    prompt = f"""
You are an expert in systematic reviews and meta-analyses. 
Your task is to extract information from the provided text and summarize it into four fields in **English**: 
1) Effect_Size_and_Model, 2) Heterogeneity_Assessment, 3) Data_Transformation_and_Software

Extraction Instructions for each field based on the provided text:

1. Effect_Size_and_Model:
   - Extract information on which effect size measure was used (e.g., SMD, MD) and why.
   - Include details on model choice (fixed-effect or random-effects) and the rationale considering statistical and clinical heterogeneity.

2. Heterogeneity_Assessment:
   - Extract information on how heterogeneity was assessed and quantified (e.g., I², Chi²).
   - Include any explanation or discussion of sources of heterogeneity, and mention if subgroup analyses were planned or not.

3. Data_Transformation_and_Software:
   - Extract information on handling of data that could not be directly used (e.g., converting median/IQR to mean/SD, exclusion of unusable data).
   - Include software used for meta-analysis and its version.

Return the result strictly in **JSON format** with the following keys: 
"Effect_Size_and_Model", "Heterogeneity_Assessment", "Data_Transformation_and_Software"
Do not include any information outside of these fields.
If any field information is missing, return null for that field.

Input Text:
\"\"\"{content}\"\"\"

Example Output:
{{
  "Effect_Size_and_Model": "Standardized mean difference (SMD) was used due to different continuous scales across studies. Random-effects models were appropriately chosen for both pain intensity and opioid consumption outcomes, considering statistical and clinical heterogeneity.",
  "Heterogeneity_Assessment": "Heterogeneity was assessed using I² and Chi² statistics. High heterogeneity (I²=81%) in pain intensity analysis was discussed with reference to pain type and surgery differences. Subgroup analysis was not feasible due to small number of studies (n=3).",
  "Data_Transformation_and_Software": "Studies with data not directly usable (e.g., median/IQR without mean/SD) were excluded from meta-analysis. Analysis was conducted using Cochrane RevMan 5.4.1 software." 
}}
"""
    return prompt


def extract_report_info(article_text, type):
    prompt = "";
    if type == "report_1" :
        prompt = extract_meta_analysis_info(article_text)
    elif type == "report_3_1":
        prompt = generate_extraction_prompt(article_text);
    elif type == "report_3_2":
        prompt = generate_data_extraction_prompt(article_text);
    elif type == "report_3_3":
        prompt = generate_risk_of_bias_prompt(article_text);
    elif type == "report_3_4":
        prompt = generate_meta_analysis_prompt(article_text);
    elif type == "report_3_5":
        prompt = generate_quality_extraction_prompt(article_text);


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
    #print(f" response is {response_text}")
    #match_result = json.loads(response_text)

   # response_text = response.text;
   # response_text = response_text.replace("```json", "")
    #response_text = response_text.replace("```", "");
   # print(f' match_result is {response_text}')
   # match_result = json.loads(response_text)

    return response_text

if __name__ == "__main__":
    meta_content = content_utils.read_content("D:\\project\\zky\\paperAgent\\all_txt\\SR1.txt");


    report_1 = extract_report_info(meta_content,"report_1");
    print(f" report_1 is {report_1}");
    report_3_1 = extract_report_info(meta_content, "report_3_1");
    print(f" report_3_1 is {report_3_1}");


    #report_3_2 = extract_report_info(meta_content, "report_3_2");
    #print(f" report_3_2 is {report_3_2}");


    '''
    report_3_3 = extract_report_info(meta_content, "report_3_3");
    print(f" report_3_3 is {report_3_3}");
    report_3_4 = extract_report_info(meta_content, "report_3_4");
    print(f" report_3_4 is {report_3_4}");
    report_3_5 = extract_report_info(meta_content, "report_3_5");
    print(f" report_3_5 is {report_3_5}");
    '''
