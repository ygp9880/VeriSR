from openai import  OpenAI
import json;
import os;
from utils import content_utils;
client = OpenAI(base_url='https://api.openai-proxy.org/v1', api_key='sk-p8KW4EtRdh7i2MWf9o7YmmQZihySS5HA5D0Z1iEdddtLURpJ');
from utils.content_utils import read_content;
import openai


def generate_prompt_for_check_summary(header, data, table):
    """
    Generate the English prompt used to summarize discrepancies from the `check` field
    across included studies (Table 2, Table 3, Table 4).
    """

    prompt = f"""
You are an expert in systematic review quality verification and data extraction auditing.

Your task is to analyze the provided JSON data, especially the contents of the **"check"** field for each included study, and generate a structured discrepancy summary.

header is {header},
data is {data}
table ttile is {table}

## Dynamic Table Handling
- The dataset may contain discrepancies related to *Table 1, Table 2, Table 3, Table 4,* or other tables.
- **Do NOT assume fixed table numbers.**
- Instead, detect which tables are referenced in the "check" text and generate corresponding sections.
- For every table name that appears (e.g., “Table 2”, “Table 3”, “Table 4”), create a section titled:

### Table X – Main Issues

## Output Requirements
For each detected Table:
- Identify and group recurring discrepancy types into **bullet-point categories**.
- Each issue category must include:
  1. **A short category title**
  2. **A concise explanation**
  3. **Specific study examples** extracted from the `check` field  
     (e.g., “Hamilton et al. [21]”)

## Examples of Possible Issue Categories (not exhaustive):
- Gene panel mismatch or incomplete reporting  
- Baseline demographic inconsistencies  
- Errors in outcome data type or statistical reporting  
- Missing extraction of key variables  
- Incorrect sample size or participant flow  
- Misalignment between reported dataset and actual analysis population  

## Content Rules
- Only use information found in the `check` field of each study.
- Summaries should focus on **issue types**, not rewrite long texts.
- Group similar discrepancies across studies under the same category.
- Maintain an analytical, concise tone.

## Final Output Format Example (structure only)

### Table X – Main Issues
  1.Issue category 1
    brief explanation

  2. Issue category 2
     explanation 
- ...


"""

    return prompt

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
You are a biomedical literature extraction assistant.
Please read the provided systematic review and meta-analysis (META) article and extract key information.
Return the results strictly in JSON format.

Extract the following fields:

- title: Full study title.
- objective: Main research objective.
- sample_size: Total number of participants across all included studies.

- inclusion_exclusion_criteria:
    Provide a structured summary of the study’s eligibility criteria, following the PICO framework.  
    This section should describe who was included or excluded from the studies and why.
    - population:Describe the participants targeted by the included studies, including age range, clinical condition, and other defining characteristics.
    - intervention:Describe the control or alternative condition used for comparison, such as standard care, placebo, or another therapy.
    - comparison:Describe the control or alternative condition used for comparison, such as standard care, placebo, or another therapy.
    - outcome:Describe the key outcomes or endpoints that studies must report to be included (e.g., symptom scores, adverse events, medication usage).

- results:
    A list (array) of one-sentence summaries.
    Each sentence must describe one key outcome or finding reported in the article.
    Do not break results into effect size or p-value fields; each result must be a single concise sentence.

Return the output in the following JSON structure:

{{
  "title": "",
  "objective": "",
  "sample_size": "",
  "inclusion_exclusion_criteria": {{
    "population": "",
    "intervention": "",
    "comparison": "",
    "outcome": "",
   }},
  "results": [
    ""
  ]
}}

Rules:
1. Follow JSON format strictly.
2. If some information is missing, return an empty string.
3. Results must be a list of complete single sentences.
4. Do not add explanations—only produce the JSON.

 Meta Article  Text:
  {article_text}
    
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
    Please extract the methodology sections from the following meta-analysis / systematic review text 
    and return the results in strict JSON format.

    JSON format:
    {{
      "Search_Strategy": {{
        "summary": "",
        "evidence": ""
      }},
      "Screening_Process": {{
        "summary": "",
        "evidence": ""
      }},
      "Results_Presentation": {{
        "summary": "",
        "evidence": ""
      }},
      "Verification_Summary": {{
        "summary": ""
      }}
    }}

    Field instructions:

    1. Search_Strategy: Include databases searched, search date ranges, search terms (keywords + Boolean operators), and reproducibility. Provide supporting quotes.
    2. Screening_Process: Include whether screening was done independently by two reviewers, whether a third reviewer arbitrated disagreements, and clarity of screening process. Provide supporting quotes.
    3. Results_Presentation: Include PRISMA flowchart, record counts, final included studies, and reasons for exclusion. Provide supporting quotes.
    4. Verification_Summary: Provide a summary evaluation specifically of the search strategy and screening process only, focusing on rigor, transparency, and reduction of selection bias. Provide supporting quotes.

    Meta Article  Text:
    \"\"\"
    {content}
    \"\"\"
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
1) Sensitivity_Analysis, 2) Publication_Bias, 3) Evidence_Quality, 4) Verification_Summary.

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
   - Include the original 'evidence' text from the article as a separate subfield named "evidence".
   - Include frameworks or tools used (e.g., GRADE), any tables or summaries provided, and any limitations in reporting.
   - Clearly reference or paraphrase the 'evidence' content when justifying your evaluation.

4. Verification_Summary:
   - Provide a brief reviewer comment summarizing the overall methodological quality.
   - Highlight strengths, shortcomings, and overall robustness of the study design and evidence assessment.

Return the result strictly in **JSON format** with the following keys: 
"Sensitivity_Analysis", "Publication_Bias", "Evidence_Quality", "Verification_Summary". 
The "Evidence_Quality" field must be an object with two subfields: "assessment" (your evaluation) and "evidence" (the original text from the article). 
Do not include any information outside of these fields. If any field information is missing, return null for that field.

Input Text:
{content}

Example Output:
{{
  "Sensitivity_Analysis": "No sensitivity analyses were reported, particularly for high-heterogeneity outcomes such as pain intensity. Missing these analyses limits the assessment of the robustness of conclusions.",
  "Publication_Bias": "Publication bias was not assessed. Given that only 3 and 2 studies were included in the respective meta-analyses, any formal assessment would be invalid or misleading, so omission aligns with methodological guidelines.",
  "Evidence_Quality": {{
      "assessment": "The GRADE framework was used to assess evidence certainty. Each outcome was rated in Table 4. Although a Summary of Findings table for combined effect sizes was not provided, the evaluation reflects a structured consideration of evidence quality.",
      "evidence": "The data from the included studies was extracted using a data extraction template created in Excel, completed independently by two reviewers with arbitration by a third for discrepancies."
  }},
  "Verification_Summary": "Reviewer comment: The study shows notable shortcomings in exploring conclusion robustness but provides a standardized assessment of evidence quality."
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
    You are an AI assistant. Extract information about the data extraction methods and data extraction content from the following meta-analysis article. 
    Return the result in JSON format. For each field, include both the extracted information and the exact supporting text from the article in a field called 'evidence'.

    Article text:
    \"\"\"{content}\"\"\"

    Instructions:

    1. Extract the following fields:

    - Extraction_Method: Describe the data extraction process (who extracted, how, any arbitration, handling of missing data).
    - Extraction_Content: List the data items extracted from the studies (study characteristics, participant characteristics, intervention, outcomes, etc.).
    - Verification_Summary: Describe how the extracted data were verified or checked for accuracy and consistency, such as duplicate checking, cross-checking between reviewers, consensus meetings, adjudication by a third reviewer, or any quality control or validation procedures applied to the extracted data.

    2. For each field, return a subfield `evidence` for Extraction_Method, Extraction_Content that contains the exact sentence(s) from the article supporting your extraction.

    3. Format example:

    {{
      "Extraction_Method": {{
        "description": "Data was extracted using an Excel template by two independent reviewers, with disagreements resolved by a third reviewer. Missing data was requested from study authors.",
        "evidence": "\"The data from the included studies was extracted using a data extraction template created in Excel.\" \"This was also carried out by a second reviewer, MB.\" \"Where data was missing or incomplete, the authors of the studies were contacted to request it.\""
      }},
      "Extraction_Content": {{
        "description": "Extracted items included study author, year, title, study design, sample size, country, sample characteristics, prescribed opioids, genetic test, genes tested, and outcomes measured.",
        "evidence": "\"Extracted data items included: study author, year of publication, study title, study design, sample size, country, sample characteristics (age, gender, ethnicity, type of pain), opioids prescribed in intervention and control groups, genetic test used, genes tested, and outcomes measured.\""
      }},
      "Verification_Summary": {{
        "description": "The extracted data were cross-checked between reviewers to ensure accuracy, and disagreements were resolved through consensus."   
      }}
    }}

    Make sure the JSON is valid and all extracted fields are accompanied by their original text under 'evidence'.
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
    prompt = f'''
    You are an expert in systematic reviews and meta-analyses. 
    Your task is to extract information from the provided text and summarize it into three fields in **English**, ensuring that each statement is directly supported by evidence from the text. 

    Output Fields:

    1) Tool_Selection:
       - Extract information about the risk of bias assessment tool used.
       - Mention whether the tool choice is appropriate for the included study designs.
       - For each statement, include the supporting evidence from the text, e.g., "Evidence: 'The data from the included studies was extracted using...'" 

    2) Assessment_Process:
       - Extract details on how the risk of bias assessment was conducted.
       - Include independent reviewers, third-party arbitration, and any mention of reviewer training.
       - For each statement, include supporting evidence from the text.

    3) Results_Presentation:
       - Extract information on how risk of bias results were presented (tables, visualizations, figures).
       - Include any decisions made based on risk of bias (e.g., exclusion of high-risk studies) and rationale.
       - For each statement, include supporting evidence from the text.
    
    4) Verification_Summary:
        - Provide a brief structured self-check summarizing:
        - Whether all statements are directly supported by quotes.
        - Whether any fields were returned as null due to missing information.
        - Any limitations encountered in extraction (e.g., vague reporting).
    
    
    Instructions:
    - Return the result strictly in **JSON format** with keys: "Tool_Selection", "Assessment_Process", "Results_Presentation".
    - If any field information is missing in the text, return null for that field.
    - Each statement in a field must be accompanied by a direct quote or reference to the text under "Evidence".

    Input Artcile Text:
    {content}

    Example Output:
    {{
      "Tool_Selection": {{
        "statement": "The study appropriately used the Cochrane Risk of Bias 2.0 (RoB 2.0) tool for assessing randomised controlled trials.",
        "evidence": "Evidence: 'The data from the included studies was extracted using a data extraction template created in Excel and assessed with RoB 2.0 for RCTs.'"
      }},
      "Assessment_Process": {{
        "statement": "Two reviewers independently carried out the risk of bias assessment, with a third reviewer resolving disagreements.",
        "evidence": "Evidence: 'Two reviewers independently extracted the data, and a third reviewer resolved any discrepancies.'"
      }},
      "Results_Presentation": {{
        "statement": "Risk of bias was evaluated across five domains and visualized in Table 5. High-risk studies were excluded from meta-analysis to avoid contamination.",
        "evidence": "Evidence: 'The risk of bias results are presented in Table 5. Studies rated as high risk were excluded from pooled analyses.'"
      }},
      "Verification_Summary": {{
        "statement":"All extracted statements are directly supported by explicit quotations from the text."
      }}
    }}
    '''

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
    Your task is to extract information from the provided text and summarize it into three fields in **English**, each supported by evidence from the text: 

    1) Effect_Size_and_Model
    2) Heterogeneity_Assessment
    3) Data_Transformation_and_Software
    4) Verification_Summary

    Extraction Instructions for each field based on the provided text:

    1. Effect_Size_and_Model:
       - Extract information on which effect size measure was used (e.g., SMD, MD) and why.
       - Include details on model choice (fixed-effect or random-effects) and the rationale considering statistical and clinical heterogeneity.
       - Provide the **evidence** from the original text that supports your summary.

    2. Heterogeneity_Assessment:
       - Extract information on how heterogeneity was assessed and quantified (e.g., I², Chi²).
       - Include any explanation or discussion of sources of heterogeneity, and mention if subgroup analyses were planned or not.
       - Provide the **evidence** from the original text that supports your summary.

    3. Data_Transformation_and_Software:
       - Extract information on handling of data that could not be directly used (e.g., converting median/IQR to mean/SD, exclusion of unusable data).
       - Include software used for meta-analysis and its version.
       - Provide the **evidence** from the original text that supports your summary.
    
    4. Verification_Summary:
        - Provide a brief structured self-check summarizing:
        - Whether all statements are directly supported by quotes.
        - Whether any fields were returned as null due to missing information.
        - Any limitations encountered in extraction (e.g., vague reporting).

    Return the result strictly in **JSON format** with the following keys and structure: 
    {{
    "Effect_Size_and_Model": {{
    "summary": "Your summary here",
          "evidence": "Supporting text from the article"
      }},
      "Heterogeneity_Assessment": {{
    "summary": "Your summary here",
          "evidence": "Supporting text from the article"
      }},
      "Data_Transformation_and_Software": {{
    "summary": "Your summary here",
          "evidence": "Supporting text from the article"
      }},
      "Verification_Summary": {{
            "summary": "Your summary here"
      }}
    }}

    If any field information is missing, return null for both "summary" and "evidence".

    Input Text:
    {content}
    """

    return prompt


def extract_meta_summary_info(article_text):
    """
    Extract key information from a meta-analysis article using a large language model.

    Args:
        article_text (str): Full text of the meta-analysis article.
        model (str): Model to use. Default is "gpt-5-mini".

    Returns:
        dict: A dictionary with keys "Strengths", "Limitations", "Reliability_of_Conclusions".
    """

    prompt = f"""
    You are a scientific research assistant. Please extract key information from the following meta-analysis article. 
    Return the output strictly in JSON format using the exact structure below:

    {{
      "Strengths": "2-3 concise sentences summarizing the main methodological and analytical strengths of the study.",
      "Limitations": "2-3 concise sentences summarizing the main limitations, including potential biases, data issues, or analysis constraints.",
      "Reliability_of_Conclusions": "2-3 concise sentences evaluating the robustness and reliability of the conclusions, noting heterogeneity, data consistency, or need for sensitivity analysis."
    }}

    Requirements:
    - Each field must be 2-3 sentences only.
    - If a section is not mentioned in the article, set its value to "Not explicitly stated".
    - Do not include any text outside the JSON.
    - Keep language clear, concise, and professional.

    Article content:
    \"\"\"
    {article_text}
    \"\"\"
    """
    return prompt;


def generate_error_extraction_prompt_en(text: str) -> str:
    """
    Generate an English prompt for extracting erroneous fields from each study in a text.

    Args:
        text (str): The source text containing study reports.

    Returns:
        str: A prompt string that can be directly used for LLM calls.
    """
    prompt = f"""
You are an expert reviewer.

Task: From the following text, identify all studies that have errors in their reported data. For each study, extract:

1. "error_fields": the specific field or data point that has an error, muse be split by ,


Output Format: JSON array where each element corresponds to a study:
[
  {{
    "study": "<study name or identifier>",
     "error_fields":""
      ...
    ]
  }},
  ...
]

Text:
{text}
"""
    return prompt

def extract_report_info(article_text, type, save_path, meta_name):
    prompt = "";
    if type == "report_1" :
        prompt = extract_meta_analysis_info(article_text)
    elif type == "report_2_1":
        prompt = generate_extraction_prompt(article_text);
    elif type == "report_2_2":
        prompt = generate_data_extraction_prompt(article_text);
    elif type == "report_2_3":
        prompt = generate_risk_of_bias_prompt(article_text);
    elif type == "report_2_4":
        prompt = generate_meta_analysis_prompt(article_text);
    elif type == "report_2_5":
        prompt = generate_quality_extraction_prompt(article_text);
    elif type == "report_3_1":
        prompt = extract_meta_summary_info(article_text);
    elif type == "report_3_2_1":
        prompt = generate_error_extraction_prompt_en(article_text);

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

    file_path = f"{save_path}\\{meta_name}_{type}.json";
    content_utils.write_str_to_file(file_path, response_text);
    return response_text

def report_json(meta_path,type,save_file_path,meta_name):
    meta_content = content_utils.read_content(meta_path);
    extract_report_info(meta_content,type,save_file_path, meta_name);


def check_data(base_path, meta_name):
    data_files = os.listdir(base_path);
    result = "";
    for file in data_files:
        if file.__contains__("txt") and file.__contains__(meta_name) and file.__contains__("table"):
            full_path = base_path + "\\" + file;
            content = read_content(full_path);
            result = result + content + "\n";
    return result;

def wrong_field_report(base_path, meta_name):
    result = check_data(base_path, meta_name);
    extract_report_info(result, "report_3_2_1", base_path, meta_name);

def data_wrong_summary(base_path, meta_name):
    data_files = os.listdir(base_path);

    results = '';
    for file in data_files:
        if file.__contains__("txt") and file.__contains__(meta_name) and file.__contains__("table") and (not file.__contains__("index")):
            full_path = base_path + "\\" + file;
            content = read_content(full_path);
            print(f" file is {file}");
            data_content = json.loads(content);
            title = data_content['title'];
            data = data_content['data'];
            data_checks = [];
            for row in data:
                check = row[-1];
                data_checks.append(row);
                # print(f" check is {check}");
            # print(f" content is {content} ");
            print(f" title is {title}");
            headers = data_content['headers'];
            prompt = generate_prompt_for_check_summary(headers, data_checks, title);
            #print(f" prompt is {prompt} ");


            response = client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {"role": "system", "content": "你是一个医学数据分析专家"},
                    {"role": "user", "content": prompt}
                ]
            )
            response_text = response.choices[0].message.content
            results = results + "\n" + response_text ;


    type = "report_2_2_3";
    file_path = f"{base_path}\\{meta_name}_{type}.txt";
    content_utils.write_str_to_file(file_path, results);


def build_rob2_comparison_prompt(rob2_json_string: str) -> str:
    """
    Build a complete prompt that embeds the ROB2 comparison JSON
    and instructs the model to generate an academic-style narrative summary.
    """
    return (
        "You are an expert in risk of bias assessment and systematic review methodology.\n\n"
        "Your task is to analyze the ROB2 comparison results provided below. "
        "These results were generated using a ROB2 evaluation module via a tool, "
        "comparing extracted ROB2 judgments with computed ROB2 judgments across "
        "multiple studies and domains (D1–D5 and Overall).\n\n"
        "ROB2 comparison results (JSON):\n"
        "```json\n"
        f"{rob2_json_string}\n"
        "```\n\n"
        "Based strictly on the data provided above, write a concise, academic-style "
        "narrative summary that includes:\n\n"
        "1. A brief statement indicating that the included studies were re-assessed "
        "using the ROB2 evaluation module via a tool.\n"
        "2. An overall assessment of agreement between extracted and computed ROB2 "
        "ratings across studies:\n"
        "   - Describe whether agreement is generally high or low.\n"
        "   - Report how many domains typically match per study.\n"
        "   - Explicitly mention which study (if any) achieved agreement on the "
        "Overall judgment.\n"
        "3. A domain-level synthesis:\n"
        "   - For each ROB2 domain (D1–D5), report the number of studies with matching "
        "judgments (e.g., \"2/6 studies\").\n"
        "   - Identify which domain shows the highest concordance and which show the "
        "lowest or no concordance.\n"
        "4. A brief explanation of common patterns of disagreement, referring to "
        "discrepancies such as extracted \"+\" versus computed \"-\" or \"X\".\n\n"
        "Constraints:\n"
        "- Do NOT invent or infer information not supported by the JSON.\n"
        "- Use explicit quantitative expressions (e.g., \"4/6 studies\").\n"
        "- Maintain a formal, publication-ready academic tone.\n"
        "- Write a single cohesive paragraph in English."
    )

def rob2_summary_report(base_path, meta_name):
    file_path = f"{base_path}\\{meta_name}_rob2_compare.txt";
    compare_content = content_utils.read_content(file_path);
    prompt = build_rob2_comparison_prompt(compare_content);

    response = client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": "你是一个医学数据分析专家"},
            {"role": "user", "content": prompt}
        ]
    )
    response_text = response.choices[0].message.content
    response_text = response_text + "The risk of bias reports for each study included in this systematic review are provided in the appendix.";
    type = "report_2_3_4";
    file_path = f"{base_path}\\{meta_name}_{type}.txt";
    content_utils.write_str_to_file(file_path, response_text);


def build_meta_analysis_validation_prompt(validation_json: str) -> str:
    """
    Build a prompt for LLM to generate a methodological consistency
    and statistical cross-check narrative based on validation JSON.
    """
    prompt = f"""
You are an expert in meta-analysis methodology and statistical validation.

Your task is to analyze the provided JSON validation results of forest plots
and meta-analyses, including:
- individual study-level SMD verification,
- pooled effect size and confidence interval validation,
- sample size checks, and
- heterogeneity statistics (τ², χ², I², Z, P values).

Based strictly on the evidence in the JSON, perform a methodological cross-check
and generate a concise narrative summary in English, similar in style to a
peer-review or systematic review appendix.

Specifically:
1. Assess whether the outcome data used in the forest plots (sample size N,
   mean, SD, SMD, pooled effects, heterogeneity metrics) are consistent with
   the calculated results.
2. Identify and clearly describe any inconsistencies, partial mismatches,
   or limitations in verification, including:
   - discrepancies in statistical significance (e.g., P value or Z direction),
   - minor numerical deviations due to rounding,
   - partial agreement across heterogeneity statistics,
   - cases of partial or incomplete verification.
3. If results are largely consistent, explicitly state this, while still noting
   any minor issues.

Output requirements:
- Write in formal academic English.
- Use numbered bullet points.
- Be concise but precise (2-3 points per figure if applicable).
- Do not restate raw numbers unless necessary to explain an inconsistency.
- Focus on interpretation and verification conclusions, not computation steps.

Begin with a sentence similar to:
"Statistical analyses were cross-checked against the reported forest plot data.
A summary of verification findings is provided below:"

Here is the validation JSON to analyze:
{validation_json}
"""
    return prompt

def meta_summary_report(base_path, meta_name):
    file_path = f"{base_path}\\{meta_name}_meta_check_output.json";
    check_output = content_utils.read_content(file_path);
    prompt = build_meta_analysis_validation_prompt(check_output);

    response = client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": "你是一个医学数据分析专家"},
            {"role": "user", "content": prompt}
        ]
    )
    response_text = response.choices[0].message.content
    response_text = response_text;
    type = "report_2_4_4";
    file_path = f"{base_path}\\{meta_name}_{type}.txt";
    content_utils.write_str_to_file(file_path, response_text);

def extract_error_domains(data, sep=", "):
    """
    提取 match == False 的 domain 名称，并拼接成字符串
    """
    result = []

    for item in data:
        study = item.get("study")
        domains = item.get("domains", {})

        error_domain_list = [
            domain
            for domain, values in domains.items()
            if values.get("match") is False
        ]

        if error_domain_list:
            result.append({
                "study": study,
                "error_domains": sep.join(error_domain_list)
            })

    return result




if __name__ == "__main__":
    meta_path = "D:\\project\\zky\\paperAgent\\all_txt\\SR1.txt";
    meta_name = "SR1";
    meta_content = content_utils.read_content(meta_path);

    report_2_2 = extract_report_info(meta_content, "report_2_2", "D:\\project\\zky\\paperAgent\\all_txt\\", meta_name);

    #wrong_field_report("D:\\project\\zky\\paperAgent\\all_txt", meta_name);


    #report_json(meta_path, "report_1", "D:\\project\\zky\\paperAgent\\all_txt\\", meta_name);

    #report_json(meta_path, "report_2_1", "D:\\project\\zky\\paperAgent\\all_txt\\", meta_name);
    #report_json(meta_path, "report_3_1", "D:\\project\\zky\\paperAgent\\all_txt\\", meta_name);
    #report_json(meta_path, "report_2_3", "D:\\project\\zky\\paperAgent\\all_txt\\", meta_name);
    #report_json(meta_path, "report_2_4", "D:\\project\\zky\\paperAgent\\all_txt\\", meta_name);
    #report_json(meta_path, "report_2_5", "D:\\project\\zky\\paperAgent\\all_txt\\", meta_name);

    #report_2_3 = extract_report_info(meta_content, "report_2_3","D:\\project\\zky\\paperAgent\\all_txt\\",meta_name);

    '''
    report_1 = extract_report_info(meta_content,"report_1","D:\\project\\zky\\paperAgent\\result\\report_1.json"); 
    
    report_2_1 = extract_report_info(meta_content, "report_2_1", "D:\\project\\zky\\paperAgent\\all_txt\\report_2_1.json");
    report_2_2 = extract_report_info(meta_content, "report_2_2","D:\\project\\zky\\paperAgent\\all_txt\\report_2_2.json");

    report_2_3 = extract_report_info(meta_content, "report_2_3","D:\\project\\zky\\paperAgent\\all_txt\\report_2_3.json");
     '''
    #report_2_4 = extract_report_info(meta_content, "report_2_4","D:\\project\\zky\\paperAgent\\all_txt\\report_2_4.json");
    #report_2_5 = extract_report_info(meta_content, "report_2_5","D:\\project\\zky\\paperAgent\\all_txt\\report_2_5.json");


