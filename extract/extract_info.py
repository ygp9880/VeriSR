from openai import  OpenAI # 需 pip install openai
import json
from google import genai
from google.genai import types

# Set your API key
client = OpenAI(base_url='https://api.openai-proxy.org/v1', api_key='sk-p8KW4EtRdh7i2MWf9o7YmmQZihySS5HA5D0Z1iEdddtLURpJ');
#client = genai.Client(api_key='AIzaSyBeHNk55lDMRU5EH6SIdhtNQQsW04HJXzk')


import openai
import json



openai.api_key = "YOUR_API_KEY_HERE"

def build_check_continue_outcome_prompt(given_outcome_type: str, outcomes_json: str) -> str:
    prompt = f"""
    You are an expert biomedical data reviewer specializing in meta-analysis verification.

    ### Task:
    You are given:
    1. The outcome type: "Continuous"
    2. A text segment extracted from a meta-analysis article (the source evidence)
    3. The extracted numeric data (JSON)

    Your goal:
    Check whether the extracted numeric values for the following fields are **accurate and logically consistent** with the evidence text:

    - mean_experimental  
    - sd_experimental  
    - n_experimental  
    - mean_control  
    - sd_control  
    - n_control  
    ---
     If a value is incorrect, identify the issue and provide the **true value from the article**.
    ### Input:
    Excerpt from the meta-analysis article describing the continuous outcome data:
    "{given_outcome_type}"
    original article is :
    {outcomes_json}
    ---
    ### Output (strict JSON format):
    {{
      "extraction_correct": <true or false>,          # whether all numeric fields match the article
      "issues": [                                     # if incorrect, list all problems
         {{
            "field": "<mean_experimental / sd_control / n_control / ...>",
            "description": "<explain what is wrong or inconsistent>",
            "value": "<true value from the article>, must be double or NONE, if don't extract, the data is NONE" 
            "evidence_reference": "<relevant part of the article>"
         }}
      ],
      "confidence": "<High/Medium/Low>",              # confidence in your judgment
      "summary": "<concise evaluation summary>"
    }}

    """
    return prompt;


def build_check_binary_outcome_prompt(given_outcome_type: str, outcomes_json: str) -> str:
    prompt = f"""
        You are an expert biomedical data reviewer specializing in meta-analysis verification.

        ### Task:
        You are given:
        1. The outcome type: "Binary"
        2. A text segment extracted from a meta-analysis article (the source evidence)
        3. The extracted numeric data (JSON)

        Your goal:
        Check whether the extracted numeric values for the following fields are **accurate and logically consistent** with the evidence text:
        - events_experimental  
        - n_experimental  
        - events_control  
        - n_control          
        ---
        
        If a value is incorrect, identify the issue and provide the **true value from the article**.

        ### Input:
        Excerpt from the meta-analysis article describing the continuous outcome data:
        "{given_outcome_type}"
        original article is ::
        {outcomes_json}
        ---
        ### Output (strict JSON format):
        {{
          "extraction_correct": <true or false>,          # whether all numeric fields match the article
          "issues": [                                     # if incorrect, list all problems
             {{
                "field": "<mean_experimental / sd_control / n_control / ...>",
                "value": "<true value from the article>,  must be double or NONE, if don't extract, the data is NONE" 
                "description": "<explain what is wrong or inconsistent>",
                "evidence_reference": "<relevant part of the article>"
             }}
          ],
          "confidence": "<High/Medium/Low>",              # confidence in your judgment
          "summary": "<concise evaluation summary>"
        }}
        """
    return prompt;


def build_outcome_prompt(given_outcome_type: str, outcomes_json: str) -> str:
    """
    构建用于标准化生物医学结果的 prompt（精简版本，只保留 type/mean/sd/total）。

    参数:
    - user_query: 用户输入的查询文本
    - outcomes_json: JSON 格式的 outcomes 数据（字符串）

    返回:
    - 完整的 prompt 字符串
    """
    prompt_template = f"""
You are an expert biomedical data normalizer. 
###  Input:
the given out_come type is :
"{given_outcome_type}"

Outcomes JSON:
{outcomes_json}

Task:
1. From the provided list of outcomes (in JSON format), identify the outcome that best matches the given outcome indicator (e.g., blood pressure, heart rate, etc.) and the corresponding follow-up time (e.g., 3 months, 6 months, 24h).
2. Normalize the matched outcome into the following simplified JSON format:
### Continuous outcomes  Output JSON format (strict):
[
{{
  "Matched_query": <string>,           # keyword(s) from user input
  "Outcome_name": <string>,            # exact name of the matched outcome
  "Experimental_group": {{
      "type": "mean_sd",
      "mean": <float>,
      "sd": <float>,
      "total": <int or null>
  }},
  "Control_group": {{
      "type": "mean_sd",
      "mean": <float>,
      "sd": <float>,
      "total": <int or null>
  }},
  "Statistical_method": <string>,
  "Statistical_result": <string>,
  "Effect_size": <float or null>
}}
]
### Binary outcomes (e.g., risk ratio, odds ratio) (strict):
[
{{
  "Matched_query": <string>,           # keyword(s) from user input
  "Outcome_name": <string>,            # exact name of the matched outcome
  "Experimental_group": {{
      "type": "<RR(risk ratio)/OR(odds ratio)>",
      "events_experimental": (must be integer),
      "n_experimental": (must be integer)
  }},
  "Control_group": {{
      "type": "<RR(risk ratio)/OR(odds ratio)>",
      "events_control": (must be integer),
      "n_control": (must be integer),
  }}
}}
]

"""
    return prompt_template




def classify_methods_keys(article_text):
    """
    Input:
        methods_json: dict, the 'methods' section of a paper as JSON
    Output:
        dict with keys: Study_design_or_population, Experimental_group_info,
                        Control_group_info, Drug_disease_gene_info
    """
    prompt = f"""
    You are an expert assistant for biomedical literature methods extraction.
    
    Task:
    Given the 'methods' section of a study in JSON format, identify which JSON keys correspond to the following categories:
    
    1. Study_design:Study design / population
    2. Experimental_group_info: Experimental group information
    3. Control_group_info:Control group information
    4. Drug_disease_gene_info:Drug, disease, or gene information
    
    Instructions:
    - Treat the input as a JSON object.    
    - For each category, list the title in JSON that correspond.
    - Output the result in a structured JSON format exactly as below.
    
    Output JSON format:
    {{
    "Study_design": ["key1", "key2", ...],
    "Experimental_group_info": ["key1", "key2", ...],
    "Control_group_info": ["key1", "key2", ...],
    "Drug_disease_gene_info": ["key1", "key2", ...]
    }}
    
    Text to analyze:
    \"\"\"{article_text}\"\"\"
    """
    return prompt;


# 示例使用
if __name__ == "__main__":
    methods_example = {
        "Study_design": "RCT, single-center",
        "Sample_size": 100,
        "Experimental_group": {"N": 50, "Age_mean": 45},
        "Control_group": {"N": 50, "Age_mean": 46},
        "Drug_info": "Aspirin",
        "Disease": "Hypertension"
    }

    result = classify_methods_keys(methods_example)
    print(json.dumps(result, indent=2, ensure_ascii=False))


def build_identify_fig_prompt(figs_str):
    prompt = f"""
    You are an expert assistant for biomedical literature extraction. 
    From the provided JSON structure under the key "figs", identify and extract only the figures that are related to meta-analysis results. 
    Return their index (starting from 1 in the input order) and titles in a JSON array.

    Input:
    {figs_str}

    Output format:
    {{
      "meta_analysis_figures": [
        {{
          "index": <figure index>,
          "title": "<figure title>"
        }}
      ]
    }}

    Rules:
    - A figure is related to meta-analysis if its title or description mentions terms such as "meta-analysis", "forest plot", or pooled results.
    - Index is the original position of the figure in the input list, starting from 1.
    - Preserve the original title text exactly as in the input.
    """

    return prompt

def build_identify_original_table_prompt(tables):
    prompt = f"""
    You are an expert assistant for biomedical literature extraction. 
    From the provided JSON structure under the key "tables", identify and extract only the tables that describe data extracted from the original studies (e.g., study characteristics, baseline information, outcome measures, or data collection details used for meta-analysis).  
    Return their index (starting from 1 in the input order) and titles in a JSON array, and please extract fields from the tables. please merge table's fields and return these fields,filter duplicate field.
    Input:
    {tables}
    Output format:
    {{
      "meta_analysis_tables": [
        {{
          "index": <table index>,
          "title": "<table title>"
          "fields","table's fileds"
        }}
      ],
      "fields":[{{ "field_name": "the extract field name, please make sure single field",
    "extract_instruct": "Instruction on how to extract this field from the text"    }}
    }}]

    Rules:
    - A  table is related to original paper's study.
    - Index is the original position of the table in the input list, starting from 1.
    - Preserve the original title text exactly as in the input.
    """

    return prompt

def build_identify_table_prompt(tables_str):
    prompt = f"""
    You are an expert assistant for biomedical literature extraction. 
    From the provided JSON structure under the key "tables", identify and extract only the figures that are related to meta-analysis results. 
    Return their index (starting from 1 in the input order) and titles in a JSON array.

    Input:
    {tables_str}

    Output format:
    {{
      "meta_analysis_figures": [
        {{
          "index": <figure index>,
          "title": "<figure title>"
        }}
      ]
    }}

    Rules:
    - A table is related to meta-analysis if its title or description mentions terms such as "meta-analysis", "forest plot", or pooled results.
    - Index is the original position of the table in the input list, starting from 1.
    - Preserve the original title text exactly as in the input.
    """

    return prompt


def build_identify_rob2_prompt(tables_str):
    prompt = f"""
    You are an expert assistant for biomedical literature extraction. 
    From the provided JSON structure under the key "tables", identify and extract only the table that are related to rob2 results. 
    Return their index (starting from 1 in the input order) and titles in a JSON array.

    Input:
    {tables_str}

    Output format:
    {{
      "meta_analysis_tables": [
        {{
          "index": <table index>,
          "title": "<table title>"
        }}
      ]
    }}

    Rules:
    - A table is rob2 to meta-analysis.
    - Index is the original position of the table in the input list, starting from 1.
    - Preserve the original title text exactly as in the input.
    """

    return prompt

def build_match_study_prompt(studies, files):
    prompt = f"""
    You are given two lists:

1. A list of study references:
studies is {studies}
2. A list of file names:
files is {files}
Task:
Match each study to its corresponding file based on author name and year (if provided). 
Each study should be matched to exactly one file.

Output requirements:
- Return the result strictly in valid JSON format.
- Use the file name as the key and the matched study name as the value.
- Do not include any explanations or extra text outside the JSON.

Expected output format example:
{{
  ["FileName.txt": "Study Name"] 
}}
    """
    return prompt;

#研究结果 result
def build_result_prompt(article_text):
    prompt =  f"""
    You are an expert biomedical literature extraction assistant. Your task is:

    Extract the study outcomes from the provided biomedical text and return them in a structured JSON format. Each outcome indicator should be one entry, with the corresponding results for experimental and control groups, as well as statistical analysis details.

    Fields to extract:
    1. Outcomes: The outcome measure or study indicator (one per row/entry).
    2. Experimental_group_results: The results for the experimental group, corresponding to "Pharmacogenomic group results (SD)".
    3. Control_group_results: The results for the control group, corresponding to "Treatment as usual group results (SD)".
    4. Statistical_method: The statistical method used to compare groups.
    5. Statistical_result: The statistical result corresponding to the method (e.g., P-value).
    6. Effect_size: The effect size reported in the study, e.g., OR(95%CI):10.1(8.91-12.03).

    Rules:
    - Each outcome indicator should be a separate JSON object in an array.
    - If some information is not reported, use null.
    - Preserve the text exactly as it appears in the source.
    - Ensure JSON output is valid and structured as an array of objects.

    Text to analyze:
    \"\"\"{article_text}\"\"\"
    """
    return prompt;



def build_indify_prompt(study_names, articles_list):
    prompt = f"""
    You are an expert assistant for biomedical literature extraction. 

    Task: From the provided list of research articles (each represented as a JSON object with fields like Title, First_author, Published_year, Journal, DOI, etc.), find the articles that correspond to the given list of Study or Subgroup names. 

    Requirements:
    1. Return the result in JSON format as a list.
    2. For each matched article, include only the following keys:
       - "study_name": The Study_or_Subgroup name you matched.
       - "index": The position of the article in the list, starting from 1.
       - "Title": The title of the matched article.
    3. **If a study  name matches multiple articles, include all matches in the list.**
    4. If a study name has no matching article, return an empty object {{}} for that study name.
    5. The output should preserve the input order of study names.

    Here is an example of the expected output:
    [
      {{
        "study_name": ,
        "index": ,
        "Title": 
      }},
      {{
        "study_name": ,
        "index":,
        "Title":
      }}
    ]

    Input:
    study name: {study_names}
    Articles_list: {articles_list}
    
    
    Output:
    """
    return prompt


# 药物、疾病、基因信息
# Methods Result
def build_gene_info_prompt(article_text):
    prompt = f"""
    You are an expert biomedical literature extraction assistant. Your task is:

    **Objective:**
    Extract the following information from the provided biomedical text and return it in a structured JSON format.

    **Fields to extract:**
    1. Disease: Name of the disease studied.
    2. Drug_type: Category or type of drug used.
    3. Experimental_group_Drug_use: Details of drug use in the experimental group, including dosage, frequency, and conditions if available.
    4. Control_group_Drug_use: Details of drug use in the control group, including dosage, frequency, and conditions if available.
    5. Gene: Name of the gene involved.
    6. Genetic_testing_methods: Methods used for genetic testing.
    7. Variant: Specific gene variant or genotype.
    8. Method_of_genotyping: Methods used for genotyping.

    **Rules:**
    - Extract all relevant information even if some fields are not explicitly mentioned; if unavailable, use null.
    - Output must be a single valid JSON object.
    - Keep all text exactly as it appears in the source when populating values.
    - Ensure consistent key names as listed above.

    **Output format example:**
    {{
      "Disease": "Type 2 Diabetes",
      "Drug_type": "Oral hypoglycemic",
      "Experimental_group_Drug_use": "Metformin 500mg twice daily",
      "Control_group_Drug_use": "Placebo once daily",
      "Gene": "TCF7L2",
      "Genetic_testing_methods": "PCR-RFLP",
      "Variant": "rs7903146",
      "Method_of_genotyping": "TaqMan assay"
    }}

    **Text to analyze:** 
    \"\"\"{article_text}\"\"\"
        """
    return prompt



#实验组信息 Methods
def build_all_prompt(article_text):
    prompt = f"""
    You are an expert assistant for biomedical literature extraction. 
    **Task 1 :** Extract experimental group information from the provided text or PDF. The output must be in structured JSON format with the following fields:
    - Experimental_group_definition: Definition or description of the experimental group.
    - Experimental_group_number: Number of participants in the experimental group.
    - Experimental_group_male: Percentage of males in the experimental group.
    - Experimental_group_female: Percentage of females in the experimental group.
    - Experimental_group_mean_age: Mean age and standard deviation of the experimental group.
    - Experimental_group_ethnicity: Distribution of ethnicities in the experimental group.
    **Instructions:**
    1. Extract information from both text paragraphs and tables if present.
    2. Ensure numeric values are accurate, and percentages sum logically.
    3. For ethnicity, use a clear format
    4. Return **valid JSON only**, without any extra commentary.
    
    **Task 2:** Extract control group information from the provided text or PDF. 
    The output must be in structured JSON format with the following fields:
    **Control Group Fields:**
    - Control_group_definition
    - Control_group_number
    - Control_group_male(%)
    - Control_group_female(%)
    - Control_group_mean_age(SD)
    - Control_group_ethnicity(%)
    **Instructions:**
    1. Extract information from both text paragraphs and tables if present.
    2. Ensure numeric values are accurate, and percentages sum logically.
    3. For ethnicity, use a clear format, e.g., {{"White": 92, "Hispanic": 3, "Black": 3, "Asian": 3}}.
    4. Return **valid JSON only**, without any extra commentary.
    
    
    **Task 3:**  Extract the following Gene information from the provided biomedical text and return it in a structured JSON format.
    **Fields to extract:**
    1. Disease: Name of the disease studied.
    2. Drug_type: Category or type of drug used.
    3. Experimental_group_Drug_use: Details of drug use in the experimental group, including dosage, frequency, and conditions if available.
    4. Control_group_Drug_use: Details of drug use in the control group, including dosage, frequency, and conditions if available.
    5. Gene: Name of the gene involved.
    6. Genetic_testing_methods: Methods used for genetic testing.
    7. Variant: Specific gene variant or genotype.
    8. Method_of_genotyping: Methods used for genotyping.    
    Now, extract the information from the following text:
    
    **Task 4:**   Extract the study outcomes from the provided biomedical text and return them in a structured JSON format. Each outcome indicator should be one entry, with the corresponding results for experimental and control groups, as well as statistical analysis details.

    Fields to extract:
    1. Outcomes: The outcome measure or study indicator (one per row/entry).
    2. Experimental_group_results: The results for the experimental group, corresponding to "Pharmacogenomic group results (SD)".
    3. Control_group_results: The results for the control group, corresponding to "Treatment as usual group results (SD)".
    4. Statistical_method: The statistical method used to compare groups.
    5. Statistical_result: The statistical result corresponding to the method (e.g., P-value).
    6. Effect_size: The effect size reported in the study, e.g., OR(95%CI):10.1(8.91-12.03).
    
      The JSON must follow this exact structure：
    {{
    "Experimental_Group":{{}},
    "Control_Group":{{}},
    "Gene":{{}},
     "Outcomes":{{
         "Outcomes":, 
          "Experimental_group_results": ,
          "Control_group_results": ,
          "Statistical_method": ,
          "Statistical_result": ,
          "Effect_size": ,
          "follow-time":,
     }}    
    }}
    
    {article_text}
    """

    return prompt;


# 实验组信息 Methods
def build_rob2_domin_prompt(article_text):
    prompt = f"""
    请你帮我判断以下随机对照试验（RCT）在 ROB 2 领域 2（Bias due to deviations from intended interventions）中，
    应该使用哪一个信号问题（signaling question）：
    1. Effect of assignment to intervention（分配干预的效应）
    2. Effect of adhering to intervention（遵循干预的效应）
    以下是论文信息：
     {article_text}
    请根据以上信息，判断：
    A. 论文应选择“Effect of assignment to intervention”信号问题
    B. 论文应选择“Effect of adhering to intervention”信号问题
    结果只有assignment,adhering两种情况,只要返回最后的结果,
    """
    return prompt;


#对照组信息 Methods
def build_control_group_prompt(article_text):
    prompt = f"""
    You are an expert assistant for biomedical literature extraction. 

    **Task:** Extract both experimental group and control group information from the provided text or PDF. 
    The output must be in structured JSON format with the following fields:
    **Control Group Fields:**
    - Control_group_definition
    - Control_group_number
    - Control_group_male(%)
    - Control_group_female(%)
    - Control_group_mean_age(SD)
    - Control_group_ethnicity(%)
    **Instructions:**
    1. Extract information from both text paragraphs and tables if present.
    2. Ensure numeric values are accurate, and percentages sum logically.
    3. For ethnicity, use a clear format, e.g., {{"White": 92, "Hispanic": 3, "Black": 3, "Asian": 3}}.
    4. Return **valid JSON only**, without any extra commentary.
    
  
    Now, extract the information from the following text:
    {article_text}
    """
    return prompt;


# 研究设计/人群 Methods
def build_study_info_prompt(article_text):
    prompt = f"""
You are an expert biomedical literature analysis assistant. Your task is to extract specific study design and population details from the provided clinical research article.

**Objective:**  
Extract the following fields accurately from the full text of the paper. For certain fields, standardize the output into a machine-readable format:
1. **Study_design**: Standardize into one of the following enum values:  
   "RCT", "Non-Randomized Controlled Trial", "Cohort Study", "Case-Control Study", "Cross-Sectional Study", "Case Series", "Case Report", "Diagnostic Accuracy Study", "Prognostic Study", "Screening Study", "Qualitative Study", "Registry Study".  
   Also capture attributes as a list: "Single-center", "Multicenter", "Open-label", "Blinded", "Randomized", "Non-randomized", "Parallel-group", "Crossover".
2. **Country**: Output a standardized country name or list of country names using English official country names (e.g., "United States", "China", "Germany").  
3. **Sample_size**: Output only the integer number of participants (e.g., 350).  
4. **Age**: Output standardized mean age in years (integer or float), optionally with range in parentheses (e.g., "53±5").  
5. **Male**: Output percentage as a number without the % sign (e.g., 42).  
6. **Inclusion_criteria**: List the inclusion criteria as text.  
7. **Exclusion_criteria**: List the exclusion criteria as text.  
8. **Follow_up_time**: Extract the follow-up duration and standardize it into **integer months**. 
   - Output must be 1h,12m,1y,10d,2min.
   - If follow-up time is not reported, return 0.  

**Important Requirements:**  
- Extract only what is explicitly stated in the text.  
- Do not guess or fabricate data. If a field is not reported, use "Not Reported" for text fields, 0 for numeric fields.  
- Output strictly valid JSON that can be parsed by standard JSON parsers.  
- Preserve numeric values in standardized formats for easy program parsing.  


**Output Format (JSON):**  
{{
  "Study_design": {{
    "Type": "",
    "Attributes": []
  }},
  "Country": [],
  "Sample_size": 0,
  "Age": "",
  "Male": 0,
  "Inclusion_criteria": "",
  "Exclusion_criteria": "",
  "Follow_up_time": "2m"
}}

Now, read the article text and return the result in the specified JSON format.

Article:

{article_text}
    """
    return prompt



def normal_outcome(user_query:str, outcomes_json:str):
    prompt = build_outcome_prompt(user_query, outcomes_json);
    response = client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": "你是一个医学数据分析专家"},
            {"role": "user", "content": prompt}
        ]
    )

    response_text = response.choices[0].message.content
    response_text = response_text.replace("```json", "")
    response_text = response_text.replace("```", "");
    print(f" response is {response_text}")
    # match_result = json.loads(response_text)

    # response_text = response.text;
    # response_text = response_text.replace("```json", "")
    # response_text = response_text.replace("```", "");
    # print(f' match_result is {response_text}')
    match_result = json.loads(response_text)

    return match_result


def check_outcome(user_query:str, outcomes_json:str, type:str):
    prompt = None;

    if type == "continue":
        prompt = build_check_continue_outcome_prompt(user_query, outcomes_json);
    else:
        prompt = build_check_binary_outcome_prompt(user_query, outcomes_json);


    response = client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": "你是一个医学数据分析专家"},
            {"role": "user", "content": prompt}
        ]
    )

    response_text = response.choices[0].message.content
    response_text = response_text.replace("```json", "")
    response_text = response_text.replace("```", "");
    print(f" response is {response_text}")
    # match_result = json.loads(response_text)

    # response_text = response.text;
    # response_text = response_text.replace("```json", "")
    # response_text = response_text.replace("```", "");
    # print(f' match_result is {response_text}')
    match_result = json.loads(response_text)

    return match_result

# 3. Call the model
def extract_info(article_text, type):

    #text = extract_pdf_text(pdf_path)
    if type == "all":
        prompt = build_all_prompt(article_text);
    if type == "fig":
        # 定位FIG 中的META 分析结果
        prompt = build_identify_fig_prompt(article_text);
    elif type == "table":
        # 定位TABLE 中的META 分析结果
        prompt = build_identify_table_prompt(article_text);
    elif type == 'original_table':
        prompt = build_identify_original_table_prompt(article_text);
    elif type == "classify":
        prompt = classify_methods_keys(article_text);
    elif type == 'study':
        prompt = build_study_info_prompt(article_text)
    elif type == 'control_group':
        prompt = build_control_group_prompt(article_text);
    elif type == 'result':
        prompt = build_result_prompt(article_text);
    elif type == 'gene':
        prompt = build_gene_info_prompt(article_text);
    elif type == 'rob2':
        prompt = build_rob2_domin_prompt(article_text);
    elif type == 'rob2_table':
        prompt = build_identify_rob2_prompt(article_text);



    #print(f" prompt is {prompt}")

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "你是一个医学数据分析专家"},
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
    match_result = json.loads(response_text)

    return match_result


# 3. Call the model
def extract_rob2_info(article_text):
    prompt = build_rob2_domin_prompt(article_text);

    response = client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": "你是一个医学数据分析专家"},
            {"role": "user", "content": prompt}
        ]
    )

    response_text = response.choices[0].message.content

    return response_text

def extract_outcome_type(title):

    #text = extract_pdf_text(pdf_path)
    prompt = f"""
    You are a medical research assistant. Based on the given study title or description, identify the **outcome type(s)** being studied or analyzed.
    the given title is {title}
    Requirements:
    1. Output only the outcome type(s), not the intervention or control information.
    2. If multiple outcomes are mentioned, list each one separately.
    3. Use concise medical terms (e.g., pain intensity, opioid consumption, recurrence rate, survival time, complication incidence, etc.).
    4. If the outcome type cannot be determined, output “Not specified.”    
    """

    #print(f" prompt is {prompt}")

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "你是一个医学数据分析专家"},
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
    #match_result = json.loads(response_text)

    return response_text


def filter_instruct(instruct):
    prompt = f"""
    You are an expert assistant for biomedical literature data extraction.  
    You will be given a list of field names.
    The field name list is {instruct}.⚠️
    Your task:  
    1. Compare each field name against the exclusion list provided.  
    2. Filter out a field ONLY IF it has a clear semantic match to one of the exclusion items.  
       - Consider synonyms, paraphrases, abbreviations, and alternative expressions as valid matches.  
       - Do NOT filter fields that only have a vague or weak relation; only remove fields with a reasonably strong semantic correspondence.  
    3. For each filtered field, provide the reason in the format: "Field_name — matched to 'Exclusion_item'".  
    4. Output two clearly separated sections:  
       - ✅ "Kept fields": field names that are NOT filtered.  
       - ❌ "Filtered fields": field names that were removed, each followed by the matching reason.  
    5. Ensure that the reasoning for each filtered field explains why the semantic match is strong enough to justify removal.  
    6.Output ONLY the results in JSON format with two keys:  
      {{
            "kept_fields": [list of field names NOT filtered],
            "filtered_fields": [
                {{
                    "field_name": "name of filtered field",
                    "matched_to": "exclusion item",
                    "reason": "explain why this field is filtered"
                }},
                ...
            ]
     }}
    Exclusion list (by meaning/semantics):
    Title
    First_author
    Published_year
    Journal
    Corresponding
    DOI
    Declaration_of_interest
    Funding
    Study_design
    Country
    Sample_size
    Age
    Male(%)
    Inclusion_criteria
    Exclusion_criteria
    Follow_up_time
    Experimental_group_definition
    Experimental_group_number
    Experimental_group_male(%)
    Experimental_group_female(%)
    Experimental_group_mean_age(SD)
    Experimental_group_ethnicity(%)
    Control_group_definition
    Control_group_number
    Control_group_male(%)
    Control_group_female(%)
    Control_group_mean_age
    Control_group_ethnicity(%)    
    Drug_type
    Experimental_group_Drug_use
    Control_group_Drug_use
    Gene
    Genetic_testing_methods
    Variant
    Outcomes
    Experimental_Outcome_number
    Control_Outcome_number
    Measurement_time
    Experimental_group_results
    Control_group_results
    Statistical_method
    Statistical_result
    Effect_size           
    """

    #print(f" prompt is {prompt}")

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "你是一个医学数据分析专家"},
            {"role": "user", "content": prompt}
        ]
    )

    response_text = response.choices[0].message.content
    response_text = response_text.replace("```json", "")
    response_text = response_text.replace("```", "");
    #print(f" response is {response_text}")
    match_result = json.loads(response_text)

   # response_text = response.text;
   # response_text = response_text.replace("```json", "")
    #response_text = response_text.replace("```", "");
   # print(f' match_result is {response_text}')


    return match_result


def indify_paper(study_names, article_list):

    prompt = build_indify_prompt(study_names, article_list)

    #print(f" prompt is {prompt}")

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "你是一个医学数据分析专家"},
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
    match_result = json.loads(response_text)

    return match_result

def indify_rob2_table(article_list):

    prompt = build_identify_rob2_prompt(article_list)

    #print(f" prompt is {prompt}")

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "你是一个医学数据分析专家"},
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
    match_result = json.loads(response_text)

    return match_result

def match_study_file(studies, files):

    prompt = build_match_study_prompt(studies, files);

    #print(f" prompt is {prompt}")

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "你是一个医学数据分析专家"},
            {"role": "user", "content": prompt}
        ]
    )

    response_text = response.choices[0].message.content
    response_text = response_text.replace("```json", "")
    response_text = response_text.replace("```", "");
    match_result = json.loads(response_text)
    return match_result


# Example usage:
if __name__ == "__main__":
    pdf_file = "example_clinical_study.pdf"
   # output = extract_study_info(pdf_file)
    #print(json.dumps(output, indent=2, ensure_ascii=False))
