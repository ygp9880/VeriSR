from openai import  OpenAI # 需 pip install openai
import json;
client = OpenAI(base_url='https://api.openai-proxy.org/v1', api_key='sk-p8KW4EtRdh7i2MWf9o7YmmQZihySS5HA5D0Z1iEdddtLURpJ');


def build_all_prompt(article_text, data_fields):
    prompt = f"""
    You are an expert assistant for biomedical literature extraction.
    
    **Task 1: Extract Basic Study Information**

    **Task:** Extract the basic information of the study from the provided text or PDF.
    The output must be in structured JSON format with the following fields:
    
    **Fields and Extraction Hints:**
    
    * **Title**: Extract the full title of the article.
    * **First_author**: Extract the first author’s name.
    * **Published_year**: Extract Year of online publication
    * **Journal**: Extract the name of the journal.
    * **Corresponding**: Extract the corresponding author information (email or affiliation).
    * **DOI**: Extract the DOI number.
    * **Declaration_of_interest**: Extract any conflict of interest statements.
    * **Funding**: Extract funding sources or grant information.

    **Instructions:**
    
    1. Extract information from both text paragraphs and tables if present.
    2. If a field is not reported, return `"NA"`.
    3. Return **valid JSON only**, without any extra commentary.
    
    **Task 2: Extract Study Design and Population Information**

    **Task:** Extract the study design and population information from the provided text or PDF.
    The output must be in structured JSON format with the following fields:
    
    **Fields and Extraction Hints:**
    
    * **Study_design**: Specify study type (e.g., `"RCT, multicenter, open-label, 2-arm"`).Blinding should not conflict with an open-label design; for instance, a double-blind study cannot be open-label. 
        If the study is single-blind, please indicate who is blinded (e.g., single-blind [patients]).
    * **Country**: Extract the country where participants were recruited.
    * **Sample_size**: Extract the total number of participants (after randomization if RCT).
    * **Age**: Overall mean age.Extraction format: mean (SD), median/mean [maximum, minimum], median/mean [first quartile, third quartile]
    * **Male(%)**: Extract the proportion of male participants. Please locate the relevant data in the original article first. If the data are not explicitly provided, calculate them and enter the results accordingly. 
    calculate them and enter the results accordingly.
    * **Inclusion_criteria**: Extract the inclusion criteria.
    * **Exclusion_criteria**: Extract the exclusion criteria.
    * **Follow_up_time**: Extract the duration of follow-up.Please specify the exact follow-up time, such as 24 hours.

    **Instructions:**
    
    1. Extract information from both text paragraphs and tables if present.
    2. If a field is not reported, return `"NA"`.
    3. Return **valid JSON only**, without any extra commentary.
    4 the result should Include `"source"` for each field.
    
     
    **Task 3 :** Extract experimental group information from the provided text or PDF. The output must be in structured JSON format with the following fields:
    - Experimental_group_definition: Definition or description of the experimental group.
    - Experimental_group_number: Number of participants in the experimental group.(Number of participants included in demographic information)
    - Experimental_group_male: Percentage of males in the experimental group.Please locate the relevant data in the original article first. If the data are not explicitly provided, calculate them and enter the results accordingly.
    - Experimental_group_female: Percentage of females in the experimental group.Please locate the relevant data in the original article first. If the data are not explicitly provided, calculate them and enter the results accordingly.
    - Experimental_group_mean_age: Mean age and standard deviation of the experimental group.Extraction format: mean (SD), median/mean [maximum, minimum], median/mean [first quartile, third quartile]
    - Experimental_group_ethnicity: Distribution of ethnicities in the experimental group,such as 92White、 3Hispanic、 3Black、 3Asian.
    **Instructions:**
    1. Extract information from both text paragraphs and tables if present.
    2. Ensure numeric values are accurate, and percentages sum logically.
    3. For ethnicity, use a clear format
    4. Return **valid JSON only**, without any extra commentary.
    5  the result should Include `"source"` for each field.

    **Task 4:** Extract control group information from the provided text or PDF. 
    The output must be in structured JSON format with the following fields:
    **Control Group Fields:**
    - Control_group_definition: Definition or description of the control group.
    - Control_group_number:Control group sample size (number of participants included in demographic information)
    - Control_group_male(%):Percentage of males in the control group.Please locate the relevant data in the original article first. If the data are not explicitly provided, calculate them and enter the results accordingly.
    - Control_group_female(%):Percentage of females in the control group.Please locate the relevant data in the original article first. If the data are not explicitly provided, calculate them and enter the results accordingly.
    - Control_group_mean_age(SD): Mean age and standard deviation of the control group.Extraction format: mean (SD), median/mean [maximum, minimum], median/mean [first quartile, third quartile]
    - Control_group_ethnicity(%):Distribution of ethnicities in the control  group.
    **Instructions:**
    1. Extract information from both text paragraphs and tables if present.
    2. Ensure numeric values are accurate, and percentages sum logically.
    3. For ethnicity, use a clear format, e.g., {{"White": 92, "Hispanic": 3, "Black": 3, "Asian": 3}}.
    4. Return **valid JSON only**, without any extra commentary.
    5  the result should Include `"source"` for each field.

    **Task 5:**  Extract the following Gene information from the provided biomedical text and return it in a structured JSON format.
    **Fields to extract:**
    1. Disease: Name of the disease studied.
    2. Drug_type: Category or type of drug used.
    3. Experimental_group_Drug_use: Medication use in the experimental group (dosage and administration under different conditions).Give a concise summary rather than a lengthy description.
    4. Control_group_Drug_use: Medication use in the control group (dosage and administration under different conditions).Give a concise summary rather than a lengthy description.
    5. Gene: Name of the gene involved.
    6. Genetic_testing_methods: Methods used for genetic testing.
    7. Variant: Specific gene variant or genotype.
    8. Method_of_genotyping: Methods used for genotyping.    
   **Instructions:** Include `"source"` for each field.

    **Task 6:**   Extract the study outcomes from the provided biomedical text and return them in a structured JSON format. Outcomes can appear in Tables or Firgs. Extract **completely and systematically** — ensure *no outcome is missed*. Each outcome indicator should be one entry, with the corresponding results for experimental and control groups, as well as statistical analysis details.
    Fields to extract:
    1. Outcomes: The outcome measure or study indicator (one per row/entry).You must identify **every distinct outcome measure or study indicator** reported in the paper.         
    2. Experimental_Outcome_number: Number of participants in the experimental group with measured effective outcome indicators
    3. Control_Outcome_number: Number of participants in the control group with measured effective outcome indicators
    5. Measurement_time: Time point or follow-up duration, e.g., "12 weeks post-surgery", "within 5-year follow-up".
    6.Experimental_group_results: Outcome results of the experimental group.Ensure consistency in the number of decimal places reported in the results. For binary outcome variables, present data as the number of occurrences (cases). For continuous variables, report data as mean (SD), median/mean [maximum, minimum], or median/mean [first quartile, third quartile].
    7.Control_group_results: Outcome results of the control group. Ensure consistency in the number of decimal places reported in the results. For binary outcome variables, present data as the number of occurrences (cases). For continuous variables, report data as mean (SD), median/mean [maximum, minimum], or median/mean [first quartile, third quartile].
    8. Statistical_method: The statistical method used to compare groups.
    9. Statistical_result: The statistical result corresponding to the method (e.g., P-value).
    10. Effect_size: The effect size reported in the study, e.g., OR(95%CI):10.1(8.91-12.03).
    **Instructions:** Include `"source"` for each field.
    
    
    
    **Task 7:** Data_Extract: Extract the fields  and return them in a structured JSON format.
    Fields to extract:
    {data_fields}

      The JSON must follow this exact structure：
    {{
      "Basic_information": {{
         "Title": {{"value": "", "source": ""}},
    "First_author": {{"value": "", "source": ""}},
    "Published_year": {{"value": "", "source": ""}},
    "Journal": {{"value": "", "source": ""}},
    "Corresponding": {{"value": "", "source": ""}},
    "DOI": {{"value": "", "source": ""}},
    "Declaration_of_interest": {{"value": "", "source": ""}},
    "Funding": {{"value": "", "source": ""}}
  }},
      "Study_design_population": {{
      "Study_design": {{"value": "", "source": ""}},
    "Country": {{"value": "", "source": ""}},
    "Sample_size": {{"value": "", "source": ""}},
    "Age": {{"value": "", "source": ""}},
    "Male(%)": {{"value": "", "source": ""}},
    "Inclusion_criteria": {{"value": "", "source": ""}},
    "Exclusion_criteria": {{"value": "", "source": ""}},
    "Follow_up_time": {{"value": "", "source": ""}}
  }},
    "Experimental_Group":{{
    
     "Experimental_group_definition": {{"value": "", "source": ""}},
    "Experimental_group_number": {{"value": "", "source": ""}},
    "Experimental_group_male": {{"value": "", "source": ""}},
    "Experimental_group_female": {{"value": "", "source": ""}},
    "Experimental_group_mean_age": {{"value": "", "source": ""}},
    "Experimental_group_ethnicity": {{"value": "", "source": ""}}
    
    }},
    "Control_Group":{{
    "Control_group_definition": {{"value": "", "source": ""}},
    "Control_group_number": {{"value": "", "source": ""}},
    "Control_group_male(%)": {{"value": "", "source": ""}},
    "Control_group_female(%)": {{"value": "", "source": ""}},
    "Control_group_mean_age(SD)": {{"value": "", "source": ""}},
    "Control_group_ethnicity(%)": {{"value": "", "source": ""}}
    
    }},
    "Gene":{{
    "Disease": {{"value": "", "source": ""}},
    "Drug_type": {{"value": "", "source": ""}},
    "Experimental_group_Drug_use": {{"value": "", "source": ""}},
    "Control_group_Drug_use": {{"value": "", "source": ""}},
    "Gene": {{"value": "", "source": ""}},
    "Genetic_testing_methods": {{"value": "", "source": ""}},
    "Variant": {{"value": "", "source": ""}},
    "Method_of_genotyping": {{"value": "", "source": ""}}
    
    
    }},
     "Outcomes":{{}},
     "Data_Extract":{{}} 
    }}
    The article is {article_text}.
    """

    return prompt;


def build_outcome_prompt(article_text):
    prompt = f"""
    Your task is to extract **all outcome measures (Outcomes)** from a clinical research article.
        ---
    
    ### 🔍 Your extraction goals:
    You must identify **every distinct outcome measure or study indicator** reported in the paper.  
    Outcomes can appear in:
    - Tables (especially Results tables)
    - Figures (Kaplan-Meier plots, line charts, forest plots, etc.)
    - Supplementary materials    
    Extract **completely and systematically** — ensure *no outcome is missed*.    
    ---    
    ### 🧩 Step 1. From Tables
    1. Scan all Tables (main and supplementary).  
    2. Extract each row or measure that represents an outcome or study indicator.  
    3. Ignore baseline characteristics or demographic summaries (they are *not* outcomes).     
      Fields to extract:
    1. Outcomes: The outcome measure or study indicator (one per row/entry).You must identify **every distinct outcome measure or study indicator** reported in the paper.         
    2. Experimental_Outcome_number: Number of participants in the experimental group with measured effective outcome indicators
    3. Control_Outcome_number: Number of participants in the control group with measured effective outcome indicators
    5. Measurement_time: Time point or follow-up duration, e.g., "12 weeks post-surgery", "within 5-year follow-up".
    6.Experimental_group_results: Outcome results of the experimental group.Ensure consistency in the number of decimal places reported in the results. For binary outcome variables, present data as the number of occurrences (cases). For continuous variables, report data as mean (SD), median/mean [maximum, minimum], or median/mean [first quartile, third quartile],don't compute please use orignal result.
    7.Control_group_results: Outcome results of the control group. Ensure consistency in the number of decimal places reported in the results. For binary outcome variables, present data as the number of occurrences (cases). For continuous variables, report data as mean (SD), median/mean [maximum, minimum], or median/mean [first quartile, third quartile],don't compute please use orignal result.
    8. Statistical_method: The statistical method used to compare groups.
    9. Statistical_result: The statistical result corresponding to the method (e.g., P-value).
    10. Effect_size: The effect size reported in the study, e.g., OR(95%CI):10.1(8.91-12.03). 
    please return json format.     
    The article is {article_text}. 
    """
    return prompt;




def build_data_extraction_prompt(article_text: str) -> str:
    """
    Build a prompt for extracting data extraction/data collection descriptions
    from meta-analysis or systematic review texts.

    Parameters:
        text (str): The input text (e.g., part of a study report).

    Returns:
        str: The formatted prompt ready to send to the model.
    """
    return f"""
You are an assistant for systematic reviews and meta-analyses. 
Your task is to carefully read the provided text and extract only the parts that describe 
1. Carefully read the provided text and extract only the parts that describe "data extraction" or "data collection" procedures.

Focus on details such as:
- if the feild is in ' 
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
Inclusion_criteria:the inclusion criteria
Exclusion_criteria:Extract the exclusion criteria.
Follow_up_time: the duration of follow-up.
Experimental_group_definition:
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
Disease
Drug_type
Experimental_group_Drug_use
Control_group_Drug_use
Gene
Genetic_testing_methods
Variant
Outcomes
Experimental_Outcome_number
Control_Outcome_number
Measurement_time:Time point or follow-up duration
Experimental_group_results: Outcome results of the experimental group
Control_group_results: Outcome results of the control group
Statistical_method
Statistical_result
Effect_size

' don't return it. because these fields we have extraced. please make sure and double-check.

- What type of information was extracted (e.g., study authors, population characteristics, interventions, outcomes, genes, dosing strategy, follow-up period, etc.)
- How the data were extracted (e.g., standardized form, independent reviewers, duplicate extraction, etc.)
- Tools or methods used for data extraction
- Any notes about resolving disagreements or quality checks during data extraction


Return a JSON object with the following fields:

{{
  "extracted_information": [{{
    "feild_name": "the extract field name, please make sure single field",
    "extract_instruct": "Instruction on how to extract this field from the text"    
  }}]
}}

The JSON should be the **only output**. Do not add any extra explanation or commentary.

Text:
{article_text}
"""

def extract_plain_info(article_text, type):

    #text = extract_pdf_text(pdf_path)
    if type == "data_extract":
        prompt = build_data_extraction_prompt(article_text);

    #print(f" prompt is {prompt}")

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
    print(f" response_text is {response_text} ");
    match_result = json.loads(response_text)
    return match_result

def extract_all_info(article_text, data_fields):
    prompt = build_all_prompt(article_text,data_fields);

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

    #match_result = json.loads(response_text)
    return response_text

def extract_original_outcome_info(article_text):
    prompt = build_outcome_prompt(article_text);

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

    #match_result = json.loads(response_text)
    return response_text