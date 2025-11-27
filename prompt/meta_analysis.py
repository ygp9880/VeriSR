from openai import  OpenAI # 需 pip install openai
import json
# 实验组信息 Methods
# Set your API key
client = OpenAI(base_url='https://api.openai-proxy.org/v1', api_key='sk-p8KW4EtRdh7i2MWf9o7YmmQZihySS5HA5D0Z1iEdddtLURpJ');


def build_meta_trans_prompt(result):
    prompt = f"""
    You are an expert assistant in meta-analysis data extraction. You will receive a JSON object containing multiple figures, each with a "title" and "data" field. Your task is:
1. Identify all figures related to meta-analysis. 
2. For each meta-analysis figure, determine whether the outcome is continuous or binary:
   - outcome:The specific clinical or physiological outcome indicator measured in the study (i.e., what the study is evaluating).
   This represents the endpoint or variable used to assess the treatment effect.     
   - followup_time: The duration of follow-up or measurement time point at which the outcome was assessed. 
     Extraction rule:
        Extract from text or table where the follow-up duration is mentioned (often in column titles or parentheses).
        Common formats include "6 months", "12 weeks", "postoperative day 7".
        If multiple follow-up times exist, extract the one corresponding to the outcome being reported in that table row.

If not explicitly stated, set the value as null or "not reported".
   - If the data are presented as means, standard deviations, and sample sizes, treat it as a continuous outcome.
   - If the data are presented as events and totals, treat it as a binary outcome.
3. Extract the data and output as a JSON array, where each element follows one of the two structures:
### Continuous outcomes (e.g., mean difference, standardized mean difference):
{{
  "title": "<Figure title>",
  "effect_type":"effect type SMD(STD Mean Difference)/MD(Mean Difference)/ROM(Ratio of Means)"
  "model_type":"fixed/random"
  "num_studies": <Number of studies included in the meta-analysis>,
  "total_participants_experimental": <Total number of participants in the experimental group>,
  "total_participants_control": <Total number of participants in the control group>,
  "pooled": {{
    "value": <pooled effect value, must be double or int >,
    "ci_lower_value": <95% CI lower bound, must be double or int >,
    "ci_upper": <95% CI upper bound, must be double or int >
  }},
"heterogeneity_info": {{
    "tau_squared": <Tau² value, must be double or int >,
    "chi_squared": <Chi² value, must be double or int >,
    "df": <degrees of freedom, must be double or int >,
    "p_value": <P value,  must be double or int >,
    "i_squared": <I² value, must be double or int>,   
  }},
  "overall_effect":{{
    "overall_effect_z":<Test for overall effect's Z value>,
    "overall_effect_p": <Test for overall effect's P value>
  }},
  "studies": [
    {{
      "study": "<Study name>",
      "mean_experimental": <Mean of experimental group>,
      "sd_experimental": <SD of experimental group>,
      "n_experimental": <Sample size of experimental group>,
      "mean_control": <Mean of control group>,
      "sd_control": <SD of control group>,
      "n_control": <Sample size of control group>,
      "Weight" : <value>,
      "Effect": {{value":,"ci_lower":, "ci_upper"}},
      "outcome":
      "followup_time"
    }}
  ]
}},
### Binary outcomes (e.g., risk ratio, odds ratio):
{{
  "title": "<Figure title>"
  "effect_type":"<RR(risk ratio)/OR(odds ratio)>"
  "models": [
    {{
      "model": "<Common effect model | Random effects model>",
      "study_group":"<Study group name>",
      "num_studies": <Number of studies included in the meta-analysis>,
      "total_participants_experimental": <Total number of participants in the experimental group>,
       "total_participants_control": <Total number of participants in the control group>,  
      "pooled": {{
        "value": <Pooled Risk Ratio>,
        "ci_lower_value": <95% CI lower bound>,
        "ci_upper_value": <95% CI upper bound>
      }},
      "heterogeneity_info": {{
        "tau_squared": <Tau² value>,
        "chi_squared": <Chi² value>,
        "df": <Degrees of freedom>,
        "p_value": <P value>,
        "i_squared": <I² value>
      }},
      "overall_effect": {{
        "overall_effect_z": <Test for overall effect's Z value>,
        "overall_effect_p": <Test for overall effect's P value>
      }}
    }}
  ]
  ,
  "studies": [
    {{
      "study": "<Study name>",
      "study_group":"<Study group name>",
      "events_experimental": <Number of events in experimental group>,
      "n_experimental": <Sample size of experimental group>,
      "events_control": <Number of events in control group>,
      "n_control": <Sample size of control group>,
      "Weight": "<Weight, e.g., 4.6%>",
      "Effect": {{
        "value": <Risk Ratio/Odds ratio>,
        "ci_lower": <95% CI lower bound>,
        "ci_upper": <95% CI upper bound>
      }},
      "outcome":
      "followup_time"
      
    }}
  ]
}}

Important instructions:
- Ignore figures that are not meta-analysis related.
- The "data" field may be a table (array) or a textual description; extract relevant numerical information.
- The Effect field must be split into three numeric fields: value, ci_lower, and ci_upper.
- The output must be a JSON array containing all meta-analysis figures. Do NOT include any extra text.
Now, extract the meta-analysis figures from the following JSON data:
{result}
    
    """
    return prompt;

def build_check_meta_prompt(result):
    prompt = f"""You are an expert in meta-analysis and evidence synthesis, skilled at critically evaluating meta-analysis results, including pooled effects, individual study effects, and heterogeneity. 
Your task is to verify the correctness and consistency of the results based on the data provided.
```
{result}
```
Check whether the meta-analysis results are correct. Output the results in **JSON format** as follows:

{{
  "title": "",
  "pooled_effect_check": {{
    "result": true,
    "reason": ""
  }},
  "individual_studies_check": [
    {{
      "study": "",
      "check": true,
      "reason": ""
    }}
  ],
  "heterogeneity_check": {{
    "result": "unknown",
    "reason": ""
  }},
  "overall_check": {{
    "result": true,
    "reason": ""
  }}
}}

**Instructions for the model:**
* Verify the **pooled effect estimate** and indicate if it seems correct. If not, provide the reason.
* Check each **individual study’s reported effect** for consistency with the data.
* Check for **heterogeneity information**; if it cannot be determined from the data, mark it as `"unknown"`.
* Provide an **overall check** summarizing whether the meta-analysis results are reasonable.
* Only analyze the **analysis results themselves**, do not check submission format or software used.
    """

    return prompt;

def build_code_prompt(result):
    prompt = f"""You are an expert in meta-analysis and evidence synthesis, skilled at critically evaluating meta-analysis results, including pooled effects, individual study effects, and heterogeneity. 
Your task is to verify the correctness and consistency of the results based on the data provided.
```
{result}
```

    """

    return prompt;


def check_meta_analysis(result, type, model="gpt-5"):
    prompt = "";
    if type == "check":
        prompt = build_check_meta_prompt(result);
    elif type == "trans":
        prompt =  build_meta_trans_prompt(result);
    #print(f" prompt is {prompt}")

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "你是一个医学数据分析专家"},
            {"role": "user", "content": prompt}
        ]
    )

    response_text = response.choices[0].message.content
    response_text = response_text.replace("```json", "")
    response_text = response_text.replace("```", "");
   # print(f" response is {response_text}")
    #match_result = json.loads(response_text)

   # response_text = response.text;
   # response_text = response_text.replace("```json", "")
    #response_text = response_text.replace("```", "");
   # print(f' match_result is {response_text}')
    match_result = json.loads(response_text)
    return match_result