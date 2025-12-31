from openai import  OpenAI # 需 pip install openai
import json
from google import genai
from google.genai import types
from anthropic import Anthropic

# 实验组信息 Methods
# Set your API key
client = OpenAI(base_url='https://api.openai-proxy.org/v1', api_key='sk-p8KW4EtRdh7i2MWf9o7YmmQZihySS5HA5D0Z1iEdddtLURpJ');

genai_client = genai.Client(api_key="sk-p8KW4EtRdh7i2MWf9o7YmmQZihySS5HA5D0Z1iEdddtLURpJ", vertexai=True, http_options={"base_url": "https://api.openai-proxy.org/google"},)

anthropic_client = Anthropic(base_url='https://api.openai-proxy.org/anthropic',api_key='sk-p8KW4EtRdh7i2MWf9o7YmmQZihySS5HA5D0Z1iEdddtLURpJ',)

def build_answer_prompt(result):
    prompt = f"""You are an expert assistant for systematic reviews and meta-analyses, specialized in using the **ROB2 (Risk of Bias 2) tool**.
Your task is to carefully read the provided article text (Methods and Results sections, or the full text) and answer the following questions from **Domain
 the article text is {result}
 5: Risk of bias in selection of the reported result**.
Please follow the evaluation rules exactly as stated below, and provide the final answers in **structured JSON format**.
#### Domain 5 Questions
**Question 5.1**
*Were the data that produced this result analysed in accordance with a pre-specified analysis plan that was finalized before unblinded outcome data were available for analysis?*
Instructions:
* Extract all **outcome measurement methods** and **analysis methods** reported in the *Methods section*.
* Extract all **outcome measurement methods** and **analysis methods** reported in the *Results section*.
* Compare them and judge based on rules:
  * If consistent OR changes unrelated to the results → `"Y"`
  * If inconsistent AND changes related to results → `"N"`
  * If no information → `"NI"`
**Question 5.2**
*Is the numerical result being assessed likely to have been selected, on the basis of the results, from multiple eligible outcome measurements (e.g. scales, definitions, time points) within the outcome domain?*
Instructions:
* Compare **measurement methods for the same outcome** between Methods vs Results.
* Judge based on rules:
  * If multiple measurements were possible but only some were reported → `"Y"`
  * If all intended outcomes were reported → `"N"`
  * If only one way to measure the outcome → `"N"`
  * If inconsistencies exist but justified and unrelated to results → `"N"`
  * If no information → `"NI"`
**Question 5.3**
*Is the numerical result being assessed likely to have been selected, on the basis of the results, from multiple eligible analyses of the data?*
Instructions:
* Compare **analysis methods** reported in Methods vs Results.
* Judge based on rules:
  * If multiple analyses were possible but only some were reported → `"Y"`
  * If all intended analyses were reported → `"N"`
  * If only one possible way to analyse → `"N"`
  * If no information → `"NI"`
---
#### Output Format
Return your final judgment in **JSON format** as follows:
{{
  "5_1": {{
    "methods_measurement": "...",
    "methods_analysis": "...",
    "results_measurement": "...",
    "results_analysis": "...",
    "answer": "Y/N/NI"
  }},
  "5_2": {{
    "methods_measurement": "...",
    "results_measurement": "...",
    "answer": "Y/N/NI"
  }},
  "5_3": {{
    "methods_analysis": "...",
    "results_analysis": "...",
    "answer": "Y/N/NI"
  }}
}}
""";
    return prompt;

def build_rob2_domain1_answer_prompt(result):
    prompt = f"""
        You are an expert in systematic reviews and meta-analyses, specialized in applying the Cochrane RoB 2 (Risk of Bias 2) tool.  
Your task is to assess the risk of bias in a single randomized controlled trial (RCT) article.  
the article is {result}
        Guidelines for Evaluation:
Certainty Rating System:
You should use the following certainty rating system to qualify the confidence in your evaluations:
High Certainty (95-100%): The evaluation is based on clear, direct, and comprehensive information provided in the RCT.
Moderate Certainty (75-94%): The evaluation is based on information that is mostly clear and direct, but with some minor uncertainties or gaps.
Low Certainty (50-74%): The evaluation is based on limited or indirect information, with significant uncertainties or gaps.
Very Low Certainty (0-49%): The evaluation is based on sparse, unclear, or highly speculative information.
For each evaluation item, include the certainty rating along with the percentage to provide a clear indication of the confidence in the assessment.
    Question 1.1: Was the allocation sequence random?   
    If the article describes the method used to generate the allocation sequence, including computer-generated random numbers, reference random number tables, coin tossing, block randomization, shuffling cards or envelopes, dice rolling, drawing lots, or minimization, answer “Yes”.
    If the generation of the allocation sequence did not involve a random component or the sequence is predictable, including methods such as alternation; methods based on dates (birth or admission); patient medical record numbers; allocation determined by clinicians or participants; allocation based on the availability of interventions; or any other systematic or arbitrary method, answer “No”.
    If the only description regarding the randomization method is a statement that the study is randomized, answer “No Information”.
    In some cases, for example, in a large trial conducted by an experienced clinical trial unit, if a paper published in a journal with strict word limits does not explicitly describe the method for generating the random sequence, it is more likely to be judged as “Probably Yes” rather than “No Information”.
    If other (concurrent) trials by the same research team have explicitly used a non-random sequence, there is reason to suspect that the current study used a similar method, making it more likely to be judged as “Probably No”.    
    
    Question 1.2: Was the allocation sequence concealed until participants were enrolled and assigned to interventions?
        (1) If the trial uses any form of remote or centralized management method to allocate interventions to participants, and the allocation process is controlled by an external unit or organization independent of the recruiting personnel (for example, an independent central pharmacy, a telephone-based or internet-based randomization service provider); or if sequentially numbered, opaque drug envelopes or sequentially numbered, identically appearing drug containers are distributed or administered after being irreversibly assigned to participants; or if a randomization system or randomization software directly generates group assignments — then answer “Yes.”
        (2) If there is reason to suspect that the enrolling investigators or participants were aware of the upcoming allocation sequence — then answer “No.”
        (3) If the article does not mention whether the allocation sequence was concealed, even if the study is described as double-blind or triple-blind — then answer “No Information.”    
    
    
    Question 1.3: Did baseline differences between intervention groups suggest 
        a problem with the randomization process?
        (1) If there are no significant differences between the intervention and control groups, or if any existing differences are due to random error, answer “NO.”
(2) If there are imbalances between the intervention and control groups that indicate problems with the randomization process, including:
1.significant differences between groups in sample sizes compared to the expected allocation ratio;
2.the number of statistically significant differences in baseline characteristics between groups clearly exceeding what would be expected by chance;
3.imbalances in one or more key prognostic factors or baseline measurements of outcome variables that are very unlikely to be due to chance, and where the group differences are sufficient to bias the estimated intervention effect;
 4. excessive similarity in baseline characteristics that does not follow a pattern expected by chance,
then answer “YES.”
(3) If baseline information for the intervention and control groups is unavailable (e.g., only an abstract is provided, or the study reports only baseline characteristics of participants in the final analysis), answer “No Information.”     

### Output format (JSON)

Return your evaluation in structured JSON format:
{{
  "article_title": "Insert the article title here",
  "domains": {{
    "domain_1": {{
        "Q1_1": {{
            "answer": "...",
            "confidence"
            "analysis": "Explanation of why this answer was chosen based on the article."
        }},
        "Q1_2": {{
            "answer": "...",
            "confidence"
            "analysis": "Explanation of why this answer was chosen based on the article."
        }},
        "Q1_3": {{
            "answer": "...",
            "confidence"
            "analysis": "Explanation of why this answer was chosen based on the article."
        }}
    }}
}}    
    """
    return  prompt;

def build_rob2_domain2_answer_prompt(result):
    prompt = f"""
        You are an expert in systematic reviews and meta-analyses, specialized in applying the Cochrane RoB 2 (Risk of Bias 2) tool.  
Your task is to assess the risk of bias in a single randomized controlled trial (RCT) article.  
the article is {result}
        Guidelines for Evaluation:
Certainty Rating System:
You should use the following certainty rating system to qualify the confidence in your evaluations:
High Certainty (95-100%): The evaluation is based on clear, direct, and comprehensive information provided in the RCT.
Moderate Certainty (75-94%): The evaluation is based on information that is mostly clear and direct, but with some minor uncertainties or gaps.
Low Certainty (50-74%): The evaluation is based on limited or indirect information, with significant uncertainties or gaps.
Very Low Certainty (0-49%): The evaluation is based on sparse, unclear, or highly speculative information.
For each evaluation item, include the certainty rating along with the percentage to provide a clear indication of the confidence in the assessment.
Please be sure to strictly adhere to this rule: answer all questions in order, and make each subsequent answer dependent on the previous answers and the original text content.        
Question 2.1: Were participants aware of their assigned intervention during the trial?
(1) If the article clearly indicates: ① participants are aware of the assigned intervention; ② the study is non-blinded or open-label, then answer “Yes.”
(2) If participants experience a side effect or toxicity specific to a particular intervention, answer “Yes” or “Probably Yes.”
(3) If the article clearly indicates: ① participants are unaware of the assigned intervention; ② the study is double-blind or triple-blind; ③ a placebo or sham intervention is used, then answer “No.”
(4) If the article does not mention any information regarding participant blinding, answer “No Information.”    
Question 2.2: Were carers and people delivering the interventions aware of participants' assigned intervention during the trial?
(1) If the article clearly states that the nursing staff or intervention providers are aware of the interventions assigned to participants and the study is an open-label or unblinded trial, answer “Yes.”
(2) If the side effects or toxicities experienced by participants are specific to a particular intervention and known to the nursing staff or intervention providers, or if the researchers must implement specific interventions based on certain clinical characteristics of participants during the trial, answer “Yes” or “Probably Yes.”
(3) If random allocation was not concealed, it is likely that the nursing staff and intervention providers were aware of the participants’ assigned interventions during the trial; answer “Probably Yes.”
(4) If the article clearly states that the nursing staff or intervention providers were not aware of the participants’ assigned interventions and the study is a double-blind or triple-blind trial, answer “No.”
(5) If the article does not mention any information regarding blinding of the nursing staff or intervention providers, answer “No Information.”   
Question 2.3: If Yes, Probably Yes or No Information to 2.1 or 2.2:  Were there deviations from the intended intervention that arose because of the trial context?
(1) Only answer “Yes” or “Probably Yes” if there is evidence or sufficient reason to believe that the trial setting caused the planned intervention to be not implemented or interventions not allowed by the protocol to be implemented.
(2) If blinding was affected due to participants reporting side effects or toxicities specific to an intervention, answer “Yes” or “Probably Yes” only when the specified intervention underwent changes inconsistent with the trial protocol and these changes were caused by the trial context.
(3) Answer “No” or “Probably No” if: 1) the specified intervention underwent changes inconsistent with the trial protocol, such as non-adherence, but these changes are consistent with what could occur outside the trial context; or 2) the specified intervention underwent changes consistent with the trial protocol, such as stopping the drug due to acute toxicity or using additional interventions intended to treat consequences of an expected intervention.
(4) Answer “No Information” if trial personnel did not report whether bias arose due to the trial setting.
Question 2.4: If Yes or Probably Yes to 2.3: Were these deviations  likely to have affected the outcome?
(1) If the specified intervention is inconsistent with the trial protocol, and the change caused by the trial environment affects the outcome, answer “Yes.”
(2) If the specified intervention is inconsistent with the trial protocol, and the change caused by the trial environment may affect the outcome, answer “Probably Yes.”
(3) If the specified intervention is inconsistent with the trial protocol, and the change caused by the trial environment does not affect the outcome, answer “No.”
(4) If the specified intervention is inconsistent with the trial protocol, and the change caused by the trial environment may not affect the outcome, answer “Probably No.”
(5) If the article does not mention the relevant information, answer “No Information.” 
Question 2.5: If Yes, Probably Yes or No Information to 2.4: Were these deviations from intended intervention balanced between groups?
(1) If the specified intervention is inconsistent with the trial protocol, and changes caused by the trial environment affected the outcome, answer “Yes.”
(2) If the specified intervention is inconsistent with the trial protocol, and changes caused by the trial environment may have affected the outcome, answer “Probably Yes.”
(3) If the specified intervention is inconsistent with the trial protocol, and changes caused by the trial environment did not affect the outcome, answer “No.”
(4) If the specified intervention is inconsistent with the trial protocol, and changes caused by the trial environment may not have affected the outcome, answer “Probably No.”
(5) If the article does not mention relevant information, answer “No Information.”
Question 2.6: Was an appropriate analysis used to estimate the effect of assignment to intervention?
(1) If the article explicitly states that an intention-to-treat (ITT) analysis or modified intention-to-treat (mITT) analysis was used, answer “Yes.”
(2) If, based on the information provided in the article, participants who did not meet the eligibility criteria were identified after randomization (and this determination was not influenced by intervention assignment), answer “Yes.”
(3) If the article explicitly states that a per-protocol (PP) analysis (excluding participants who did not receive the assigned intervention) or an “as-treated” analysis (grouping participants according to the intervention they actually received rather than the assigned intervention) was used, answer “No.”
(4) If, based on the information provided in the article, eligible participants were excluded from the analysis after randomization, answer “No.”
(5) If the article does not mention the analysis method, and the number of participants included in the final analysis is less than the number randomized, answer “Probably No.”
(6) If the article does not mention the analysis method, and the number of participants included in the final analysis equals the number randomized, answer “Probably Yes.”
(7) If the article does not provide relevant information, answer “No Information.”  
Question 2.7: If No, Probably No or No Information to 2.6: Was there potential for a substantial impact on the result of the failure to analyse participants in the group to which they were randomized?
(1) If the number of participants who were incorrectly assigned to the intervention group or excluded from the analysis is sufficient to have a substantial impact on the results, answer “Yes.”
(2) If the number of participants who were incorrectly assigned to the intervention group or excluded from the analysis may have a substantial impact on the results, answer “Probably Yes.”
(3) If the number of participants who were incorrectly assigned to the intervention group or excluded from the analysis did not have a substantial impact on the results, answer “No.”
(4) If the number of participants who were incorrectly assigned to the intervention group or excluded from the analysis is unlikely to have a substantial impact on the results, answer “Probably No.”
(5) If the article does not provide relevant information, answer “No Information.”

### Output format (JSON)

Return your evaluation in structured JSON format:
{{
  "article_title": "Insert the article title here",
  "domains": {{
     "domain_2": {{
        "Q2_1": {{
            "answer": "...",
            "confidence"
            "analysis": "..."
        }},
        "Q2_2": {{
            "answer": "...",
             "confidence"
            "analysis": "..."
        }},
        "Q2_3": {{
            "answer": "...",
             "confidence"
            "analysis": "..."
        }},
        "Q2_4": {{
            "answer": "...",
             "confidence"
            "analysis": "..."
        }},
        "Q2_5": {{
            "answer": "...",
             "confidence"
            "analysis": "..."
        }},
        "Q2_6": {{
            "answer": "...",
             "confidence"
            "analysis": "..."
        }},
        "Q2_7": {{
            "answer": "...",
             "confidence"
            "analysis": "..."
        }}
    }},
}}    
    """
    return prompt;



def build_rob2_domain2_adhering_answer_prompt(result):
    prompt = f"""
        You are an expert in systematic reviews and meta-analyses, specialized in applying the Cochrane RoB 2 (Risk of Bias 2) tool.  
Your task is to assess the risk of bias in a single randomized controlled trial (RCT) article.  
the article is {result}
        Guidelines for Evaluation:
Certainty Rating System:
You should use the following certainty rating system to qualify the confidence in your evaluations:
High Certainty (95-100%): The evaluation is based on clear, direct, and comprehensive information provided in the RCT.
Moderate Certainty (75-94%): The evaluation is based on information that is mostly clear and direct, but with some minor uncertainties or gaps.
Low Certainty (50-74%): The evaluation is based on limited or indirect information, with significant uncertainties or gaps.
Very Low Certainty (0-49%): The evaluation is based on sparse, unclear, or highly speculative information.
For each evaluation item, include the certainty rating along with the percentage to provide a clear indication of the confidence in the assessment.
Please be sure to strictly adhere to this rule: answer all questions in order, and make each subsequent answer dependent on the previous answers and the original text content.   
Question 2.1: Were participants aware of their assigned intervention during the trial?
(1) If the article clearly states that: 1. participants are aware of the assigned intervention; 2. the study is unblinded or open-label, answer “Yes.”
(2) If participants experience side effects or toxicities specific to a particular intervention, answer “Yes” or “Probably Yes.”
(3) If the article clearly states that: 1. participants are unaware of the assigned intervention; 2. the study is double-blind or triple-blind; 3. a placebo or sham intervention is used, answer “No.”
(4) If the article does not mention any information regarding participant blinding, answer “No Information.”  
Question 2.2: Were carers and people delivering the interventions aware of participants' assigned intervention during the trial?
(1) If the article clearly states that the nursing staff or intervention providers are aware of the interventions assigned to participants and the study is an open-label or unblinded trial, answer “Yes.”
(2) If the side effects or toxicities experienced by participants are specific to a particular intervention and known to the nursing staff or intervention providers, or if the researchers must implement specific interventions based on certain clinical characteristics of participants during the trial, answer “Yes” or “Probably Yes.”
(3) If random allocation was not concealed, it is likely that the nursing staff and intervention providers were aware of the participants’ assigned interventions during the trial; answer “Probably Yes.”
(4) If the article clearly states that the nursing staff or intervention providers were not aware of the participants’ assigned interventions and the study is a double-blind or triple-blind trial, answer “No.”
(5) If the article does not mention any information regarding blinding of the nursing staff or intervention providers, answer “No Information.”   
Question 2.3: If Yes, Probably Yes or No Information to 2.1 or 2.2: Were there deviations from the intended intervention that arose because of the trial context?
(1) If there are important non-protocol interventions in the trial, including: 1. inconsistent with the trial protocol; 2. possibly received by participants after the assigned intervention began; 3. having prognostic significance for the outcome, and such interventions are balanced between the intervention and control groups, answer “Yes.”
(2) If there are important non-protocol interventions in the trial, including: 1. inconsistent with the trial protocol; 2. possibly received by participants after the assigned intervention began; 3. having prognostic significance for the outcome, and such interventions are unbalanced between the intervention and control groups, answer “No.”
(3) If the article does not mention relevant information, answer “No Information.”
Question 2.4: If Yes or Probably Yes to 2.3: Were these deviations likely to have affected the outcome?
If more than 10% of the interventions were not implemented as intended, answer “Yes.”
If the intervention was successfully implemented for most participants, answer “No” or “Probably No.”        
If the article does not mention the relevant information, answer “No Information.” 
Question 2.5: If Yes, Probably Yes or No Information to 2.4: Were these deviations from intended intervention balanced between groups?
(1) For studies with ongoing interventions, if the non-adherence rate (including partial non-compliance with the ongoing intervention, discontinuation of the intervention, crossover to the control intervention, or switching to other active interventions) exceeds 10% and affects the outcome, answer “Yes”; if it exceeds 10% and may affect the outcome, answer “Probably Yes.”
(2) If the study involves a one-time intervention, or if in studies with ongoing interventions all or most participants received the assigned intervention, answer “No.”
(3) If the article does not report relevant information, answer “No Information.”    
Question 2.6: Was an appropriate analysis used to estimate the effect of assignment to intervention?
(1) If the article indicates the use of appropriate analytical methods, including: 1. instrumental variable analysis, suitable for trials comparing a single baseline intervention (using an all-or-none adherence pattern) with standard care, used to estimate the effect of receiving the assigned intervention; 2. inverse probability weighting, used in trials with a sustained treatment strategy to adjust for participants’ data censored due to discontinuation of the assigned intervention, then answer “Yes.”
(2) If the article indicates the use of the following analytical methods, including: 1. intention-to-treat (ITT) analysis; 2. per-protocol (PP) analysis; 3. as-treated analysis; 4. analysis according to received treatment, then answer “No.”
(3) If the article does not mention relevant information, then answer “No Information.”
### Output format (JSON)

Return your evaluation in structured JSON format:
{{
  "article_title": "Insert the article title here",
  "domains": {{
     "domain_2": {{
        "Q2_1": {{
            "answer": "...",
             "confidence"
            "analysis": "..."
        }},
        "Q2_2": {{
            "answer": "...",
             "confidence"
            "analysis": "..."
        }},
        "Q2_3": {{
            "answer": "...",
             "confidence"
            "analysis": "..."
        }},
        "Q2_4": {{
            "answer": "...",
             "confidence"
            "analysis": "..."
        }},
        "Q2_5": {{
            "answer": "...",
             "confidence"
            "analysis": "..."
        }},
        "Q2_6": {{
            "answer": "...",
             "confidence"
            "analysis": "..."
        }}
    }},
}}    
    """
    return prompt;

def build_rob2_domain3_answer_prompt(result):
    prompt = f"""
        You are an expert in systematic reviews and meta-analyses, specialized in applying the Cochrane RoB 2 (Risk of Bias 2) tool.  
Your task is to assess the risk of bias in a single randomized controlled trial (RCT) article.  
the article is {result}
        Guidelines for Evaluation:
Certainty Rating System:
You should use the following certainty rating system to qualify the confidence in your evaluations:
High Certainty (95-100%): The evaluation is based on clear, direct, and comprehensive information provided in the RCT.
Moderate Certainty (75-94%): The evaluation is based on information that is mostly clear and direct, but with some minor uncertainties or gaps.
Low Certainty (50-74%): The evaluation is based on limited or indirect information, with significant uncertainties or gaps.
Very Low Certainty (0-49%): The evaluation is based on sparse, unclear, or highly speculative information.
For each evaluation item, include the certainty rating along with the percentage to provide a clear indication of the confidence in the assessment.
Please be sure to strictly adhere to this rule: answer all questions in order, and make each subsequent answer dependent on the previous answers and the original text content. 
Question 3.1: Were data for this outcome available for all, or nearly all,  participants randomized?
(1) For continuous outcome measures, answer "Yes" if data are available for 95% or more of participants (excluding imputed data).
(2) For continuous outcome measures, answer "No" if data are available for less than 95% of participants (excluding imputed data).
(3) For binary outcome measures, answer "Yes" if the number of observed events is much greater than the number of participants with missing outcome data (excluding imputed data).
(4) For binary outcome measures, answer "No" if the number of observed events is less than or only slightly more than the number of participants with missing outcome data (excluding imputed data).
(5) Only answer "No Information" if the trial report provides no information regarding the extent of missing outcome data.    
Question 3.2: If No, Probably No or No Information to 3.1: Is there evidence that the result was not biased by missing outcome data?
(1) If the article indicates that appropriate analytical methods were used, including: 1. methods that adjust for bias; 2.sensitivity analyses (where results do not vary substantially under multiple reasonable assumptions regarding the relationship between missing outcomes and their true values), then answer “Yes.”
(2) If the article only uses a single imputation method, such as “last observation carried forward,” or only performs multiple imputation based on the intervention group to estimate outcome variables, then answer “No.”    
Question 3.3: If No or Probably No to 3.2: Could missingness in the outcome depend on its true value?
Based on the information provided in the article, if loss to follow-up or withdrawal from the study is related to the outcome, answer “Yes.”
Based on the information provided in the article, if loss to follow-up or withdrawal from the study may be related to the participants’ health status, answer “Probably Yes.”
Based on the information provided in the article, if all missing outcome data are recorded and unrelated to the outcome (e.g., measurement device failure or routine data collection interruptions), answer “No” or “Probably No.”
If the article does not provide relevant information, answer “No Information.”  
Question 3.4: If Yes, Probably Yes or No Information to 3.3: Is it likely that missingness in the outcome depended on its true value?
(1) Based on the information provided in the article, if any of the following situations occur:
    1.There is a difference in the proportion of missing outcome data between the intervention and control groups;
    2.The reported reasons for missing outcome data indicate that the missingness depends on the true outcome values;
    3.There is a difference in the reported reasons for missing outcome data between the intervention and control groups;
    4.The trial setting suggests that missing outcomes may depend on their true values;
    5.In time-to-event analyses, participants stop or change the assigned intervention (e.g., due to drug toxicity),
    then answer “Yes.”
(2) Based on the information provided in the article, if the analysis has accounted for participant characteristics that may explain the relationship between missing outcomes and their true values, then answer “No.”
(3) If the article does not provide relevant information, then answer “No Information.”  

Return your evaluation in structured JSON format:
{{
  "article_title": "Insert the article title here",
  "domains": {{
      "domain_3": {{
        "Q3_1": {{
            "answer": "...",
             "confidence"
            "analysis": "..."
        }},
        "Q3_2": {{
            "answer": "...",
             "confidence"
            "analysis": "..."
        }},
        "Q3_3": {{
            "answer": "...",
             "confidence"
            "analysis": "..."
        }},
        "Q3_4": {{
            "answer": "...",
             "confidence"
            "analysis": "..."
        }}       
    }}
}}   
    """
    return prompt;


def build_rob2_domain4_answer_prompt(result):
    prompt = f"""
        You are an expert in systematic reviews and meta-analyses, specialized in applying the Cochrane RoB 2 (Risk of Bias 2) tool.  
Your task is to assess the risk of bias in a single randomized controlled trial (RCT) article.  
the article is {result}
        Guidelines for Evaluation:
Certainty Rating System:
You should use the following certainty rating system to qualify the confidence in your evaluations:
High Certainty (95-100%): The evaluation is based on clear, direct, and comprehensive information provided in the RCT.
Moderate Certainty (75-94%): The evaluation is based on information that is mostly clear and direct, but with some minor uncertainties or gaps.
Low Certainty (50-74%): The evaluation is based on limited or indirect information, with significant uncertainties or gaps.
Very Low Certainty (0-49%): The evaluation is based on sparse, unclear, or highly speculative information.
For each evaluation item, include the certainty rating along with the percentage to provide a clear indication of the confidence in the assessment.
Please be sure to strictly adhere to this rule: answer all questions in order, and make each subsequent answer dependent on the previous answers and the original text content.    
Question 4.1: Was the method of measuring the outcome inappropriate?
(1) Based on the information provided in the article, if the outcome measurement method is inappropriate, including: 1.the method may be insensitive to a reasonable intervention effect (e.g., the range of important outcome values exceeds the detectable level of the measurement method); 2.the measurement tool has been shown to have poor validity, then answer "Yes" or "Probably Yes."
(2) Based on the information provided in the article, if the outcome is pre-specified and the outcome measurement method is reliable, then answer "No" or "Probably No."
(3) If the article does not mention the outcome measurement method, then answer "No Information."
Question 4.2: Could measurement or ascertainment of the outcome have differed between intervention groups?
(1) Based on the information provided in the article, if the intervention and control groups passively collected outcome data or the intervention involved additional medical visits, answer “Yes.”
(2) Based on the information provided in the article, if the intervention and control groups used the same outcome measurement methods and thresholds, and measurements were taken at comparable time points, answer “No.”
(3) If the article does not mention relevant information, answer “No Information.”  
Question 4.3: If No, Probably No or No Information to 4.1 and 4.2: Were outcome assessors aware of the intervention received by participants?
(1) Based on the information provided in the article, if any of the following apply:
1.it is explicitly stated that outcome assessors are aware of the intervention status;
2. the study is non-blinded or open-label,
then answer “Yes.”
(2) Based on the information provided in the article, if any of the following apply:
1.it is explicitly stated that outcome assessors are unaware of the intervention status;
2.the study is double-blind or triple-blind;
3.it is indicated that a placebo or sham intervention was used;
4. any form of remote or centralized management method is used for intervention allocation, with the allocation process controlled by an external unit or organization independent of the recruiters (e.g., an independent central pharmacy, or a randomization service provider via telephone or internet),
then answer “No.”        
(3) If the article only mentions outcome assessors but does not specify whether they are aware of the intervention status, then answer “No Information.”
Question 4.4: If Yes, Probably Yes or No Information to 4.3: Could assessment of the outcome have been influenced by knowledge of intervention received?
(1) Based on the information provided in the article, if the outcome measure is subjective, such as pain intensity, answer “Yes” or “Probably Yes.”
(2) Based on the information provided in the article, if the outcome measure is objective, such as all-cause mortality, answer “No” or “Probably No.”
(3) If the article does not mention the method of measuring the outcome, answer “No Information.”
Question 4.5: If Yes, Probably Yes or No Information to 4.4: Is it likely that assessment of the outcome was influenced by knowledge of intervention received?
(1) Based on the information provided in the article, if the outcome measure is subjective, such as pain severity, answer “Yes” or “Probably Yes.”
(2) Based on the information provided in the article, if the outcome measure is objective, such as all-cause mortality, answer “No” or “Probably No.”
(3) If the article does not mention how the outcome measure was assessed, answer “No Information.”  

### Output format (JSON)

Return your evaluation in structured JSON format:
{{
  "article_title": "Insert the article title here",
  "domains": {{
    "domain_4": {{
        "Q4_1": {{
            "answer": "...",
             "confidence"
            "analysis": "..."
        }},
        "Q4_2": {{
            "answer": "...",
             "confidence"
            "analysis": "..."
        }},
        "Q4_3": {{
            "answer": "...",
             "confidence"
            "analysis": "..."
        }},
        "Q4_4": {{
            "answer": "...",
             "confidence"
            "analysis": "..."
        }},
        "Q4_5": {{
            "answer": "...",
             "confidence"
            "analysis": "..."
        }}      
    }}
}}    
    """
    return prompt;

def build_rob2_domain5_answer_prompt(result):
    prompt = f"""
        You are an expert in systematic reviews and meta-analyses, specialized in applying the Cochrane RoB 2 (Risk of Bias 2) tool.  
Your task is to assess the risk of bias in a single randomized controlled trial (RCT) article.  
the article is {result}
        Guidelines for Evaluation:
Certainty Rating System:
You should use the following certainty rating system to qualify the confidence in your evaluations:
High Certainty (95-100%): The evaluation is based on clear, direct, and comprehensive information provided in the RCT.
Moderate Certainty (75-94%): The evaluation is based on information that is mostly clear and direct, but with some minor uncertainties or gaps.
Low Certainty (50-74%): The evaluation is based on limited or indirect information, with significant uncertainties or gaps.
Very Low Certainty (0-49%): The evaluation is based on sparse, unclear, or highly speculative information.
For each evaluation item, include the certainty rating along with the percentage to provide a clear indication of the confidence in the assessment.
Please be sure to strictly adhere to this rule: answer all questions in order, and make each subsequent answer dependent on the previous answers and the original text content.    
Question 5.1: Were the data that produced this result analysed in accordance with a pre-specified analysis plan that was finalized  before unblinded outcome data were available for analysis?
According to the information provided in the article, answer **“Yes”** if **any** of the following conditions are met:
    1. The article mentions a study registration number, demonstrating that all aspects of the results (including outcome definitions, measurement time points, statistical models, etc.) strictly followed a pre-specified plan finalized before data unblinding;
    2. Changes to the analysis plan occurred before the acquisition of unblinded outcome data, or were clearly unrelated to the results (for example, data could not be collected due to equipment failure).
According to the information provided in the article, answer **“No”** if changes to the analysis plan occurred **after** the acquisition of unblinded outcome data or were clearly related to the results — for instance, if “exploratory analyses” or “post-hoc analyses” were conducted.
    If the article does **not** provide a pre-specified analysis plan, answer **“No Information.” 
Question 5.2: Is the numerical result being  assessed likely to have been selected, on the basis of the results, from multiple eligible outcome measurements (e.g. scales, definitions, time points) within the outcome domain?
(1) Based on the information provided in the "Methods" and "Results" sections of the article, if any of the following situations exist: there is clear evidence (usually obtained through review of the trial protocol or statistical analysis plan) that the outcome measure was assessed using multiple eligible measurement methods, but only one or part of the measurement data is fully reported (without a valid reason), and the fully reported result is likely selectively presented based on the outcome, then answer “Yes” or “Probably Yes.”
(2) Based on the information provided in the "Methods" and "Results" sections of the article, if any of the following situations exist: (i) there is clear evidence (usually obtained through review of the trial protocol or statistical analysis plan) that all reported eligible results for the outcome fully correspond to the pre-specified measurement target; (ii) the outcome measure has only a single feasible measurement method; (iii) for different reports of the same trial, there are inconsistencies in the outcome measurement results, but the investigators have provided reasons for the inconsistencies that are unrelated to the outcomes themselves, then answer “No” or “Probably No.”
(3) Based on the information provided in the "Methods" and "Results" sections of the article, if any of the following situations exist: (i) the analysis intent is unavailable; (ii) the analysis intent is not reported in sufficient detail to allow assessment, and multiple possible ways of defining the measurement outcome exist, then answer “No Information.”
Question 5.3: Is the numerical result being assessed likely to have been selected, on the basis of the results, from multiple eligible analyses of the data?
(1) Based on the information provided in the “Methods” and “Results” sections of the article, if any of the following situations exist: there is clear evidence (usually through review of the trial protocol or statistical analysis plan) that a certain outcome measure was analyzed using multiple feasible methods, but only one or some of the analysis results were fully reported (without a justified reason), and the fully reported result is likely selected based on the outcome itself, then answer “Yes” or “Probably Yes.”
(2) Based on the information provided in the “Methods” and “Results” sections of the article, if any of the following situations exist: (i) there is clear evidence (usually through review of the trial protocol or statistical analysis plan) that all eligible results reported correspond to pre-specified analyses; (ii) only one possible analysis method exists for the outcome measure; (iii) analyses across different reports of the same trial are inconsistent, but the investigators have provided reasons for the inconsistency that are unrelated to the nature of the results, then answer “No” or “Probably No.”
(3) Based on the information provided in the “Methods” and “Results” sections of the article, if any of the following situations exist: (i) the analysis intent is not accessible; (ii) the analysis intent is not reported in sufficient detail to support assessment, and multiple possible analysis methods exist for the outcome measure, then answer “No Information.”


### Output format (JSON)

Return your evaluation in structured JSON format:
{{
  "article_title": "Insert the article title here",
  "domains": {{
     "domain_5": {{
        "Q5_1": {{
            "answer": "...",
             "confidence"
            "analysis": "..."
        }},
        "Q5_2": {{
            "answer": "...",
             "confidence"
            "analysis": "..."
        }},
        "Q5_3": {{
            "answer": "...",
             "confidence"
            "analysis": "..."
        }}       
    }}
}}    
    """
    return prompt;



def build_rob2_answer_prompt(result):
    prompt = f"""You are an expert assistant for systematic reviews and meta-analyses, specialized in applying the ROB2 (Risk of Bias 2) tool.

Your task: Evaluate a single randomized trial report (article), not the entire meta-analysis. 
You must assess the risk of bias using the ROB2 tool, strictly following the Cochrane guidelines.
 the article text is {result}
⚠️ Important rules:
- Base your answers ONLY on what is explicitly reported in the article.
- Do NOT make assumptions or positive inferences if information is missing.
- If information is not provided, answer with “No information” or “Insufficient information”.
- At the end of each domain, provide a judgment: 
  - Low risk of bias
  - Some concerns
  - High risk of bias

---

### Domains and Signaling Questions:

**Domain 1: Risk of bias arising from the randomization process**
1.1 Was the allocation sequence adequately generated?  

In this question, you must strictly rely on the information in the article and not make assumptions or implications about the information in the article
The most important: If the article only mentions random grouping without methods for generating random sequences is mentioned, don't be inclined to make positive assumptions, but could evaluate it as "NI", even if the study was randomly assigned; 
Only if the article describes the methods of sequence generating (computer-generated random numbers, block randomization, coin tossing, card or envelope shuffling, dice rolling, lot drawing, or minimization) were used, the answer to this question is "Y"; 
If the sequence was generated based on the odd or even date of birth, some rule based on the date (or day) of admission, or some rule based on hospital or clinic record number, the answer to this question is "PN".
If allocation was based on clinician judgment, participant preference, results of a series of laboratory tests, or availability of the intervention, the answer to this question is "N".

1.2 Was the allocation sequence concealed until participants were enrolled and assigned to interventions?  

In this question, you must strictly rely on the information in the article and not make assumptions or implications about the information in the article
The most important: If does not mention assignment concealment, the answer to this question is “NI”, even if the study was described as a double-blind or triple blind study;
If the article mentions allocation concealing or masking (including central allocation, sequentially numbered drug containers of identical appearance, or opaque envelopes), participants may not be aware of the assignment, the answer to this question is "PY"; 
If the article mentions allocation concealing or masking (including central allocation, sequentially numbered drug containers of identical appearance, or opaque envelopes), participants may be aware of the assignment, the answer to this question is "PN";
If the article describes the specific methods of sequence concealing (including central allocation, sequentially numbered drug containers of identical appearance, or opaque envelopes) were used, the answer to this question is "Y"; 
If an open random allocation schedule was used or if assignment envelopes were used without appropriate safeguards (e.g., if envelopes were unsealed, non-opaque, or not sequentially numbered), the answer to this question is "N".


1.3 Did baseline differences between intervention groups suggest a problem with the randomization process?  

If there are no significant differences between the intervention and control groups, or if any existing differences are attributed to random error, the answer to this question is "N"; 
If there are noticeable differences between the intervention and control groups that are attributed to randomization, including the following aspects: 1, The sample sizes between the two groups differ significantly beyond the expected allocation ratio, 2 There are statistically significant differences in baseline characteristics between the two groups, 3 The differences between the groups are substantial enough to introduce bias in the assessment of intervention effects, 4 One or more important prognostic factors or baseline measurements of outcome variables differ, and it's not due to random error, 5 Baseline characteristics are too similar to be explained by random error, then the answer to this question is "Y"; 
If there is no information in the article regarding differences in baseline characteristics between the intervention and control groups, the answer to this question is "NI".


**Domain 2: Risk of bias due to deviations from intended interventions**  
2.1 Were participants aware of their assigned intervention during the trial?  

In this question, you need to combine the information provided in the article with your own professional knowledge to make a comprehensive judgment on the question.
If participants were aware of their allocation, the answer to this question is "Y"; 
If the article states that this is a non blind or open label trial, the answer to this question is "Y"; 
If there is handling of potential side effects or toxicity of interventions suffered by participants, or if there are other circumstances that may lead participants to know their allocation, the answer to this question is "PY"; 
If participants were unaware of their allocation, the answer to this question is "N";
If the article states that participants received a placebo or sham intervention as part of the blinding procedure, the answer to this question is "N";
If there is no information in the article regarding blinding of participants, the answer to this question is "NI". 

2.2 Were carers and people delivering the interventions aware of participants’ assigned intervention during the trial?  

In this question, you need to combine the information provided in the article with your own professional knowledge to make a comprehensive judgment on the question.
If the intervention providers were aware of the participants' allocation, the answer to this question is "Y"; 
If there is handling of potential side effects or toxicity of interventions suffered by participants, or if there are other circumstances that may lead intervention providers to know the participants' allocation, the answer to this question is "PY"; 
If intervention providers were unaware of the participants' allocation, or if the article states that intervention providers administered a placebo or sham intervention as part of the blinding procedure, the answer to this question is "N"; 
If there is no information in the article regarding blinding of intervention providers, the answer to this question is "NI".

2.3 If Y/PY/NI to 2.1 or 2.2: Were there deviations from the intended intervention that arose because of the experimental context?  

In this question, you need to combine the information provided in the article with your own professional knowledge to make a comprehensive judgment on the question.
If the article does not report any deviations from the intended intervention, the answer to this question is "NI";
If the trial context led to failure to implement the protocol interventions or to implementation of interventions not allowed by the protocol., the answer to this question is "Y"; 
If blinding is compromised because participants report side effects or toxicities that are specific to one of the interventions, and there were changes from assigned intervention that are inconsistent with the trial protocol and arose because of the trial context., the answer to this question is "Y"; 
If the article describes changes from assigned intervention that are inconsistent with the trial protocol, but these changes are consistent with what could have occurred outside the trial context, such as non-inheritance to intervention, the answer to this question is "N";
If the article describes changes to intervention that are consistent with the trial protocol, for example cessation of a drug intervention because of acute toxicity or use of additional interventions whose aim is to treat consequences of one of the intended interventions., the answer to this question is "N".

2.4 If Y/PY to 2.3: Were these deviations likely to have affected the outcome?  

In this question, you need to combine the information provided in the article with your own professional knowledge to make a comprehensive judgment on the question.
If the article states that biases from the trial environment are likely to affect the outcomes, the answer to this question is "Y"; 
If, based on the information provided in the article, it can be inferred that biases from the trial environment may impact the outcomes, the answer to this question is "PY"; If the article states that biases from the trial environment are unlikely to affect the outcomes, the answer to this question is "N"; 
If, based on the information provided in the article, it can be inferred that biases from the trial environment are likely not to affect the outcomes, the answer to this question is "PN"; 
If the article does not provide any information that can help you make a judgment on the question, the answer to this question is "NI".

2.5 If Y/PY/NI to 2.4: Were these deviations from intended intervention balanced between groups?  

In this question, you need to combine the information provided in the article with your own professional knowledge to make a comprehensive judgment on the question.
If the article states that the impact of bias generated from the trial environment is equal in both groups, the answer to this question is "Y"; 
If, based on the information provided in the article, it can be inferred that the impact of bias generated from the trial environment may be equal in both groups, the answer to this question is "PY"; If the article states that the impact of bias generated from the trial environment is not equal in both groups, the answer to this question is "N"; 
If, based on the information provided in the article, it can be inferred that the impact of bias generated from the trial environment may not be equal in both groups, the answer to this question is "PN";
If the article does not provide any information that can help you make a judgment on the question, the answer to this question is "NI".

2.6 Was an appropriate analysis used to estimate the effect of assignment to intervention?  

In this question, you need to make a comprehensive judgment based on the information provided in the article, and your own professional knowledge.
If the article excludes participants with missing outcome data during data analysis, the answer to this question is "Y";
If the article state in the research protocol or methodology section the use of intent to treat (ITT) analyses and modified intent to treat (mITT) analyses, the answer to this question is "Y"; 
If the article states that “per-protocol” analyses (excluding trial participants who did not receive their assigned intervention) and “as treated”analyses (in which trial participants are grouped according to the intervention that they received, rather than according to their assigned intervention), the answer to this question is "N"; 
If the article states that analyses excluding eligible trial participants post-randomization , the answer to this question is "N";
If the article does not report the analysis method, but the number of participants in the result analysis is less than the number of participants after randomization, the answer to this question is "PY";
If the article does not report the analysis method, and the number of participants in the result analysis is the same as the number of participants after randomization, the answer to this question is "PN";
If the article does not provide any information that can help you make a judgment on the question, the answer to this question is "NI";
If the number of participants in the result analysis is consistent with the number of participants after randomization, and there is no clear evidence to suggest that the article used inappropriate analysis methods such as‘per-protocol, the answer to question cannot be N or PN;

2.7 Was there potential for a substantial impact (on the result) of the failure to analyse participants in the group to which they were randomized?

In this question, you need to combine the information provided in the article with your own professional knowledge to make a comprehensive judgment on the question.
If no randomized participants are excluded from the analysis, the answer to this question is "N"
If based on the information provided in the article and the type of results, it can be inferred that the number of participants who were analysed in the wrong intervention group, or excluded from the analysis, was sufficient that there could have been a substantial impact on the result, the answer to this question is "Y"
If based on the information provided in the article and the type of results, it can be inferred that the inappropriate handling of participants with missing outcome data may affect the outcomes, the answer to this question is "PY"; 
If based on the information provided in the article and the type of results, it can be determined that the number of participants who were analysed in the wrong intervention group, or excluded from the analysis cannot impact on the results, the answer to this question is "N"
If based on the information provided in the article and the type of results, it can be inferred that biases from the trial environment are likely not to affect the outcomes, the answer to this question is "PN"; 
If the article does not provide any information that can help you make a judgment on the question, the answer to this question is "NI".

**Domain 3: Risk of bias due to missing outcome data**  
3.1 Were data for this outcome available for all, or nearly all, participants randomized?  

In this question, you need to calculate the proportion of the number of participants in the result analysis to the total number of participants after randomization, and judge the answer of the question based on the calculated proportion:
If the outcome is a continuous variable and 95% or more of the randomized participants have complete outcome data (excluding imputed data), the answer is "Y";
If the outcome is a continuous variable and 90% to 95% of randomized participants have complete outcome data (excluding imputed data), the answer is "PN";
If the outcome is a continuous variable and the proportion of participants with complete outcome data after randomization is less than 90%, the answer is "N";
If the outcome is a binary variable and the number of observed events is much greater than the number of participants with missing outcomes, the answer is "Y";
If the outcome is a binary variable and the number of observed events is not much greater than the number of participants with missing outcomes, the answer is "N";
If the article does not provide the number of randomized individuals, the answer is "NI".

3.2 If N/PN/NI to 3.1: Is there evidence that the result was not biased by missing outcome data?  

In this question, you need to combine the information provided in the article with your own professional knowledge to make a comprehensive judgment on the question.
If the article uses analysis methods such as inverse probability weighting that can correct for bias, or provides evidence through sensitivity analysis that outcomes were not biased due to missing data, the answer is "Y"; 
If no information is provided regarding the relationship between missing outcome data and bias correction methods or if inappropriate methods like last observation carried forward (LOCF) or imputation based solely on the intervention group were used, the answer is "N".

3.3 If N/PN to 3.2: Could missingness in the outcome depend on its true value?  

In this question, you need to combine the information provided in the article with your own professional knowledge to make a comprehensive judgment on the question.
If, based on the information provided in the article, it can be inferred that participants dropped out of the study and follow-up due to health issues related to the outcome variable, the answer is "Y"; 
If, based on the information provided in the article, it can be inferred that participants dropped out of the study and follow-up due to their health status, and does not specify whether it is related to the outcome variable, the answer is "PY"; 
If, based on the information provided in the article, it can be inferred that all missing outcome data is unrelated to the outcome itself, the answer is "N"; 
If the article does not provide any information that can help you make a judgment on the question, the answer is "NI".

3.4 If Y/PY/NI to 3.3: Is it likely that missingness in the outcome depended on its true value?  

In this question, you need to combine the information provided in the article with your own professional knowledge to make a comprehensive judgment on the question.
If the article contains any of the following situations: 1) There is a discrepancy in the proportion of missing outcome data between the intervention and control groups, and this discrepancy is related to the outcome variable; 2) The reported reasons for missing outcome data suggest a relationship with the missing outcome variable; 3) Different intervention groups have different reasons for missing outcome data; 4) The actual circumstances of the study suggest that missing outcome data is likely related to the outcome itself; 5) In time-to-event analysis, when a participants drops out of the study and follow-up due to drug toxicity or side effects, the answer is "Y"; If the analysis explains the characteristics of participants that may explain the relationship between missing outcome data and the outcome variable, the answer is "N"; 
If the article does not provide any information that can help you make a judgment on the question, the answer is "NI".

**Domain 4: Risk of bias in measurement of the outcome**  
4.1 Was the method of measuring the outcome inappropriate?  

In this question, you need to extract the measurement method of the outcome in the article and make a judgment based on your professional knowledge
If the current measurement method cannot reliably measure the intervention effect (e.g., the outcome measure is beyond the detection range of the measurement method) or if the measurement tool's reliability is poor, the answer is "Y"; 
If the outcome measure was predefined and the measurement tool is reliable, the answer is "N"; 
If the article does not provide the outcome measurement method of the outcome, the answer is "NI".

4.2 Could measurement or ascertainment of the outcome have differed between intervention groups?  

In this question, you need to combine the information provided in the article with your own professional knowledge to make a comprehensive judgment on the question.
If the outcome variables for both groups should be measured in a comparable way, including using the same measurement method at comparable time points and having the same measurement thresholds, the answer is "N"; 
If there are differences in measurement between the two groups, such as more frequent visits in the intervention group, the answer is "Y"; 
If the article does not provide any information that can help you make a judgment on the question, the answer is "NI".

4.3 Were outcome assessors aware of the intervention received by study participants?  

In this question, you need to combine the information provided in the article with your own professional knowledge to make a comprehensive judgment on the question;
If the outcome is a patient reported outcome, and the participants were aware of their own group assignments, the answer is "Y";
If the outcome is not a patient reported outcome, and the outcome assessors were aware of the participants' group assignments, the answer is "Y"; 
If the outcome is a patient reported outcome, and the participants were not aware of their own group assignments, the answer is "N";
If the outcome is a patient reported outcome, and the article states that blinding methods like placebo or sham intervention were employed for the participants, the answer is "N";
If the outcome is not a patient reported outcome, and the outcome assessors were not aware of the participants' group assignments, the answer is "N";
If the outcome is not a patient reported outcome, and the article states that blinding methods like placebo or sham intervention were employed for the outcome assessors, the answer is "N"; 
If the article does not provide any information that can help you make a judgment on the question, the answer is "NI".

4.4 If Y/PY/NI to 4.3: Could assessment of the outcome have been influenced by knowledge of intervention received?  

In this question, you need to determine whether the outcome is subjective or objective.
If the outcome is an objective measure, such as all-cause mortality, the answer is "N"; 
If the outcome is a subjective measure and the measurement method does not specify whether it was assessed by the outcome assessor or reported by the patient, the answer is "PY"; 
If the outcome is a subjective measure reported by the patient, such as patient-reported pain level, the answer is "Y"; 
If the outcome is a subjective measure assessed by the outcome assessor, the answer is "Y"; 
If the article does not report a measurement method for the outcome, the answer is "NI".

4.5 If Y/PY/NI to 4.4: Is it likely that assessment of the outcome was influenced by knowledge of intervention received?  

In this question, you need to combine the information provided in the article with your own professional knowledge to make a comprehensive judgment on the question.
If there is no clear evidence to suggest that knowledge of intervention status was likely to influence outcome assessment, the answer is "N"; 
If there is clear evidence to suggest that knowledge of intervention status was likely to influence outcome assessment, (such as patient-reported symptoms in trials of homeopathy, or assessments of recovery of function by a physiotherapist who delivered the intervention), the answer is "Y"; 
If the article does not provide any information about this can help you make a judgment on the question, the answer is "NI".

**Domain 5: Risk of bias in selection of the reported result**  
5.1 Were the data that produced this result analyzed in accordance with a pre-specified analysis plan that was finalized before unblinded outcome data were available for analysis?  

In this question, you need to extract the measurement and the analyses method for all outcomes reported in the protocol of the article and compare them with the measurement method for all outcomes reported in the Results section
If the measurement and analysis methods of all results in the results section are consistent with those of all results in the methods section, and all outcomes reported in the methods section are reported in the results section, the answer to the question is "Y";
If the measurement and analysis methods of all results in the results section are  inconsistent with those of all results in the methods section, or if there is an outcome mentioned in the methods section that is not reported in the results section, but it can be clearly established that the changes to the plan are unrelated to the results, the answer to the question is "Y";
If the measurement and analysis methods of all results in the results section are  inconsistent with those of all results in the methods section, or if there is an outcome mentioned in the methods section that is not reported in the results section, in addition, it can be clearly established that the changes to the plan are related to the results, the answer to the question is "N";
If the article does not provide any information about the measurement and the analyses method of outcomes that can help you make a judgment on the question, the answer to the question is "NI".

5.2 Were there multiple eligible outcome measurements (e.g., scales, definitions, time points) within the outcome domain?  

In this question, you need to extract the measurement method for this outcome reported in the Methods section of the article and compare them with the measurement method for this outcome reported in the Results section
If there is clear evidence that multiple measurements were taken for the outcomes, but only one or a few of these measurements are fully reported, the answer to this question is "Y"; 
If all eligible reported results for the outcome domain correspond to all intended outcome measurements, the answer to this question is "N";
If there is only one possible way in which the outcome domain can be measured (hence there is no opportunity to select from multiple measures), the answer to this question is "N";
If outcome measurements are inconsistent across different reports on the same trial, but the article have provided the reason for the inconsistency and it is not related to the nature of the results, the answer to this question is "N";
If the article does not provide any information that can help you make a judgment on the question, the answer to this question is "NI".

5.3 Were there multiple eligible analyses of the data?  

In this question, you need to extract the analyses method reported in the Methods section of the article and compare them with the analyses method reported in the Results section
you need to compare the analyses method reported in the Methods section of the article with the outcome measurement method reported in the Results section.
If there is clear evidence that multiple analysis methods were used for the results, but only one or a few of these analyses are fully reported, the answer to this question is "Y"; 
If there is clear evidence that all eligible reported results for the outcome measurement correspond to all intended analyses., the answer is "N"; 
If there is only one possible way in which the outcome measurement can be analysed (hence there is no opportunity to select from multiple analyses).
If the article does not provide any information that can help you make a judgment on the question, the answer to this question is "NI".

---

### Output format (JSON)

Return your evaluation in structured JSON format:
{{
  "article_title": "Insert the article title here",
  "domains": {{
    "domain_1": {{
        "Q1_1": {{
            "answer": "...",
            "analysis": "Explanation of why this answer was chosen based on the article."
        }},
        "Q1_2": {{
            "answer": "...",
            "analysis": "Explanation of why this answer was chosen based on the article."
        }},
        "Q1_3": {{
            "answer": "...",
            "analysis": "Explanation of why this answer was chosen based on the article."
        }},
        "judgment": "Low risk of bias / Some concerns / High risk of bias"
    }},
    "domain_2": {{
        "Q2_1": {{
            "answer": "...",
            "analysis": "..."
        }},
        "Q2_2": {{
            "answer": "...",
            "analysis": "..."
        }},
        "Q2_3": {{
            "answer": "...",
            "analysis": "..."
        }},
        "Q2_4": {{
            "answer": "...",
            "analysis": "..."
        }},
        "Q2_5": {{
            "answer": "...",
            "analysis": "..."
        }},
        "Q2_6": {{
            "answer": "...",
            "analysis": "..."
        }},
        "Q2_7": {{
            "answer": "...",
            "analysis": "..."
        }},
        "judgment": "Low risk of bias / Some concerns / High risk of bias"
    }},
    "domain_3": {{
        "Q3_1": {{
            "answer": "...",
            "analysis": "..."
        }},
        "Q3_2": {{
            "answer": "...",
            "analysis": "..."
        }},
        "Q3_3": {{
            "answer": "...",
            "analysis": "..."
        }},
        "Q3_4": {{
            "answer": "...",
            "analysis": "..."
        }},
        "judgment": "Low risk of bias / Some concerns / High risk of bias"
    }},
    "domain_4": {{
        "Q4_1": {{
            "answer": "...",
            "analysis": "..."
        }},
        "Q4_2": {{
            "answer": "...",
            "analysis": "..."
        }},
        "Q4_3": {{
            "answer": "...",
            "analysis": "..."
        }},
        "Q4_4": {{
            "answer": "...",
            "analysis": "..."
        }},
        "Q4_5": {{
            "answer": "...",
            "analysis": "..."
        }},
        "judgment": "Low risk of bias / Some concerns / High risk of bias"
    }},
    "domain_5": {{
        "Q5_1": {{
            "answer": "...",
            "analysis": "..."
        }},
        "Q5_2": {{
            "answer": "...",
            "analysis": "..."
        }},
        "Q5_3": {{
            "answer": "...",
            "analysis": "..."
        }},
        "judgment": "Low risk of bias / Some concerns / High risk of bias"
    }}
 
  "overall_risk_of_bias": "Low risk of bias / Some concerns / High risk of bias"
}}
---

Now, carefully read the provided article text and complete this structured ROB2 assessment.
"""
    return prompt;


def build_rob2_single_answer_prompt(result):
    prompt = f"""You are an expert assistant for systematic reviews and meta-analyses, specialized in applying the ROB2 (Risk of Bias 2) tool.

Your task: Evaluate a single randomized trial report (article), not the entire meta-analysis. 
You must assess the risk of bias using the ROB2 tool, strictly following the Cochrane guidelines.
 the article text is {result}
### Domains and Signaling Questions:
**Domain 5: Risk of bias in selection of the reported result**  
5.1 Were the data that produced this result analyzed in accordance with a pre-specified analysis plan that was finalized before unblinded outcome data were available for analysis?  

In this question, you need to extract the measurement and the analyses method for all outcomes reported in the protocol of the article and compare them with the measurement method for all outcomes reported in the Results section
If the measurement and analysis methods of all results in the results section are consistent with those of all results in the methods section, and all outcomes reported in the methods section are reported in the results section, the answer to the question is "Y".
If the measurement and analysis methods of all results in the results section are  inconsistent with those of all results in the methods section, or if there is an outcome mentioned in the methods section that is not reported in the results section, but it can be clearly established that the changes to the plan are unrelated to the results, the answer to the question is "PY";
If the measurement and analysis methods of all results in the results section are  inconsistent with those of all results in the methods section, or if there is an outcome mentioned in the methods section that is not reported in the results section, in addition, it can be clearly established that the changes to the plan are related to the results, the answer to the question is "N";
If the article does not provide any information about the measurement and the analyses method of outcomes that can help you make a judgment on the question, the answer to the question is "NI".


5.2 Were there multiple eligible outcome measurements (e.g., scales, definitions, time points) within the outcome domain?  

In this question, you need to extract the measurement method for this outcome reported in the Methods section of the article and compare them with the measurement method for this outcome reported in the Results section
If there is clear evidence that multiple measurements were taken for the outcomes, but only one or a few of these measurements are fully reported, the answer to this question is "Y"; 
If all eligible reported results for the outcome domain correspond to all intended outcome measurements, the answer to this question is "N";
If there is only one possible way in which the outcome domain can be measured (hence there is no opportunity to select from multiple measures), the answer to this question is "N";
If outcome measurements are inconsistent across different reports on the same trial, but the article have provided the reason for the inconsistency and it is not related to the nature of the results, the answer to this question is "N";
If the article does not provide any information that can help you make a judgment on the question, the answer to this question is "NI".

5.3 Were there multiple eligible analyses of the data?  

In this question, you need to extract the analyses method reported in the Methods section of the article and compare them with the analyses method reported in the Results section
you need to compare the analyses method reported in the Methods section of the article with the outcome measurement method reported in the Results section.
If there is clear evidence that multiple analysis methods were used for the results, but only one or a few of these analyses are fully reported, the answer to this question is "Y"; 
If there is clear evidence that all eligible reported results for the outcome measurement correspond to all intended analyses., the answer is "N"; 
If there is only one possible way in which the outcome measurement can be analysed (hence there is no opportunity to select from multiple analyses).
If the article does not provide any information that can help you make a judgment on the question, the answer to this question is "NI".

---

### Output format (JSON)

Return your evaluation in structured JSON format:
{{
  "article_title": "Insert the article title here",
  "domains": {{  
    "domain_5": {{
        "Q5_1": {{
            "answer": "...",
            "analysis": "..."
        }},
        "Q5_2": {{
            "answer": "...",
            "analysis": "..."
        }},
        "Q5_3": {{
            "answer": "...",
            "analysis": "..."
        }},
        "judgment": "Low risk of bias / Some concerns / High risk of bias"
    }}

  "overall_risk_of_bias": "Low risk of bias / Some concerns / High risk of bias"
}}
---

Now, carefully read the provided article text and complete this structured ROB2 assessment.
"""
    return prompt;


def build_new_rob2_prompt(result):
    prompt = f"""
    You are an expert in systematic reviews and meta-analyses, specialized in applying the Cochrane RoB 2 (Risk of Bias 2) tool.  
Your task is to assess the risk of bias in a single randomized controlled trial (RCT) article.  
the article is {result}
⚠️ Important rules:
- Base your answers ONLY on what is explicitly reported in the article.
- Do NOT make assumptions or use external knowledge.
- If information is insufficient, state "No information reported."
- For each signalling question, provide:
  1. **Answer**: "Y" (Yes), "N" (No), "NI" (No Information), or "PN" (Probably No), "PY" (Probably Yes), following ROB 2 guidance.
  2. **Analysis**: A short justification using quotes or paraphrases from the article.

---

## Domains to Assess

### Domain 1: Bias arising from the randomization process
- Was the allocation sequence random?
- Was the allocation sequence concealed until participants were enrolled?
- Did baseline differences between groups suggest a problem with randomization?

### Domain 2: Bias due to deviations from intended interventions
- Were participants aware of their assigned intervention?
- Were carers and people delivering the intervention aware?
- Were there deviations from the intended intervention that could affect outcomes?
- Was the analysis appropriate to estimate the effect of assignment to intervention?

### Domain 3: Bias due to missing outcome data
- Were outcome data available for all or nearly all participants?
- Were participants with missing data balanced across groups?
- Is there evidence that results were biased by missing outcome data?

### Domain 4: Bias in measurement of the outcome
- Were outcome assessors blinded to intervention assignment?
- Could assessment of the outcome have been influenced by knowledge of intervention?
- Were measurement methods valid and reliable?

### Domain 5: Bias in selection of the reported result
- Were analyses conducted according to a pre-specified analysis plan?
- Were all outcomes listed in methods also reported in results?
- Were selective reporting or multiple analyses suspected?

---

### Output format (JSON)

Return your evaluation in structured JSON format:
{{
  "article_title": "Insert the article title here",
  "domains": {{
    "domain_1": {{
        "Q1_1": {{
            "answer": "...",
            "analysis": "Explanation of why this answer was chosen based on the article."
        }},
        "Q1_2": {{
            "answer": "...",
            "analysis": "Explanation of why this answer was chosen based on the article."
        }},
        "Q1_3": {{
            "answer": "...",
            "analysis": "Explanation of why this answer was chosen based on the article."
        }},
        "judgment": "Low risk of bias / Some concerns / High risk of bias"
    }},
    "domain_2": {{
        "Q2_1": {{
            "answer": "...",
            "analysis": "..."
        }},
        "Q2_2": {{
            "answer": "...",
            "analysis": "..."
        }},
        "Q2_3": {{
            "answer": "...",
            "analysis": "..."
        }},
        "Q2_4": {{
            "answer": "...",
            "analysis": "..."
        }},
        "Q2_5": {{
            "answer": "...",
            "analysis": "..."
        }},
        "Q2_6": {{
            "answer": "...",
            "analysis": "..."
        }},
        "Q2_7": {{
            "answer": "...",
            "analysis": "..."
        }},
        "judgment": "Low risk of bias / Some concerns / High risk of bias"
    }},
    "domain_3": {{
        "Q3_1": {{
            "answer": "...",
            "analysis": "..."
        }},
        "Q3_2": {{
            "answer": "...",
            "analysis": "..."
        }},
        "Q3_3": {{
            "answer": "...",
            "analysis": "..."
        }},
        "Q3_4": {{
            "answer": "...",
            "analysis": "..."
        }},
        "judgment": "Low risk of bias / Some concerns / High risk of bias"
    }},
    "domain_4": {{
        "Q4_1": {{
            "answer": "...",
            "analysis": "..."
        }},
        "Q4_2": {{
            "answer": "...",
            "analysis": "..."
        }},
        "Q4_3": {{
            "answer": "...",
            "analysis": "..."
        }},
        "Q4_4": {{
            "answer": "...",
            "analysis": "..."
        }},
        "Q4_5": {{
            "answer": "...",
            "analysis": "..."
        }},
        "judgment": "Low risk of bias / Some concerns / High risk of bias"
    }},
    "domain_5": {{
        "Q5_1": {{
            "answer": "...",
            "analysis": "..."
        }},
        "Q5_2": {{
            "answer": "...",
            "analysis": "..."
        }},
        "Q5_3": {{
            "answer": "...",
            "analysis": "..."
        }},
        "judgment": "Low risk of bias / Some concerns / High risk of bias"
    }}
 
  "overall_risk_of_bias": "Low risk of bias / Some concerns / High risk of bias"
}}
---
"""
    return prompt;

def read_content(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    return content;

#Gemini 2.5 Pro、 Claude 4.5 Sonnet
#gpt-5,claude-sonnet-4-5,gemini-2.5-pro

def compute_domain1_judgement(result):
    domain = result['domains']['domain_1'];
    q1:str = domain['Q1_1']['answer']
    q2:str = domain['Q1_2']['answer']
    q3:str = domain['Q1_3']['answer']
    q1 = q1.lower();
    q2 = q2.lower();
    q3 = q3.lower();

    if None in (q1, q2, q3):
        return None

    YES = {"Yes".lower(), "Probably Yes".lower()}
    YESNI = {"Yes".lower(), "Probably Yes".lower(), "No Information".lower()}
    NO = {"No".lower(), "NO".lower(),"Probably No".lower()}
    NONI = {"No".lower(), "NO".lower(),"Probably No".lower(), "No Information".lower()}
    NI = {"No Information".lower(),"NO".lower()}

    if q2 in NO:
        return "High"
    elif q2 in NI:
        if q3 in YES:
            return "High"
        elif q3 in NO:
            return "Some concerns"
        elif q3 in NI:
            return "Some concerns"
        else:
            return None
    elif q2 in YES:
        if q1 in NO:
            return "Some concerns"
        elif q1 in YESNI:
            if q3 in NONI:
                return "Low"
            elif q3 in YES:
                return "Some concerns"
            else:
                return None
        else:
            return None
    else:
        return None

def compute_domain2_judgement(result) -> str | None:
    """
    Compute the risk of bias judgement for the Domain using the algorithm
    from the RoB 2.0 deviations domain flowchart.
    """
    domain = None;
    if 'domain_2' in result['domains']:
        domain = result['domains']['domain_2'];
    else:
        domain = result['domains'][1];

    # Answers for each question
    q1 = domain['Q2_1']['answer'].lower()  # 2.1
    q2 = domain['Q2_2']['answer'].lower()
    q3 = domain['Q2_3']['answer'].lower()
    q4 = domain['Q2_4']['answer'].lower()
    q5 = domain['Q2_5']['answer'].lower()
    q6 = domain['Q2_6']['answer'].lower()
    q7 = domain['Q2_7']['answer'].lower()



    YES = {"Yes".lower(), "Probably Yes".lower()}
    NO = {"No".lower(), "Probably No".lower()}
    NI = {"No Information".lower()}

    # Part 1
    if q1 in NO and q2 in NO:
        part1 = "Low"
    else:
        if q3 in NO:
            part1 = "Low"
        elif q3 in NI:
            part1 = "Some concerns"
        else:  # q3 in YES
            if q4 in NO:
                part1 = "Some concerns"
            else:
                if q5 in YES:
                    part1 = "Some concerns"
                else:
                    part1 = "High"

    # Part 2
    if q6 in YES:
        part2 = "Low"
    else:
        if q7 in NO:
            part2 = "Some concerns"
        else:
            part2 = "High"

    if part1 == "Low" and part2 == "Low":
        return "Low"
    elif part1 == "High" or part2 == "High":
        return "High"
    else:
        return "Some concerns"

def compute_domain2_deviations_judgement(result) -> str | None:
    """
    Compute the risk of bias judgement for the 'Deviations from intended interventions' domain
    using the RoB 2.0 flowchart (6-question version).
    """

    # 获取每个问题的回答
    # Answers for each question

    domain = None;
    if 'domain_2' in result['domains']:
        domain = result['domains']['domain_2'];
    else:
        domain = result['domains'][1];


    q1 = domain['Q2_1']['answer'].lower()  # 2.1
    q2 = domain['Q2_2']['answer'].lower()
    q3 = domain['Q2_3']['answer'].lower()
    q4 = domain['Q2_4']['answer'].lower()
    q5 = domain['Q2_5']['answer'].lower()
    q6 = domain['Q2_6']['answer'].lower()

    YES = {"Yes".lower(), "Probably Yes".lower()}
    NO = {"No".lower(), "Probably No".lower()}
    NI = {"No Information".lower()}

    # ===== Part 1: deviations and blinding =====
    if q1 in NO and q2 in NO:
        part1 = "Low"
    else:
        if q3 in NO:
            part1 = "Low"
        elif q3 in NI:
            part1 = "Some concerns"
        else:  # q3 in YES
            if q4 in NO:
                part1 = "Some concerns"
            else:
                if q5 in YES:
                    part1 = "Some concerns"
                else:
                    part1 = "High"

    # ===== Part 2: appropriate analysis =====
    if q6 in YES:
        part2 = "Low"
    elif q6 in NO:
        part2 = "High"
    else:
        part2 = "Some concerns"

    # ===== Final judgement =====
    if part1 == "Low" and part2 == "Low":
        return "Low"
    elif part1 == "High" or part2 == "High":
        return "High"
    else:
        return "Some concerns"

def compute_domain3_judgement(result) -> str | None:
    """
    Compute the risk of bias judgement for the Domain.
    """
    #domain = result['domains']['domain_3'];

    domain = None;
    if 'domain_3' in result['domains']:
        domain = result['domains']['domain_3'];
    else:
        domain = result['domains'][2];


    q1 = domain['Q3_1']['answer'].lower()  # 2.1
    q2 = domain['Q3_2']['answer'].lower()
    q3 = domain['Q3_3']['answer'].lower()
    q4 = domain['Q3_3']['answer'].lower()

    # Return None if any required question is unanswered
    if None in (q1, q2, q3,q4):
        return None

    YES = {"Yes".lower(), "Probably Yes".lower()}
    NO = {"No".lower(), "Probably No".lower()}

    if q1 in YES:
        return "Low"
    else:
        if q2 in YES:
            return "Low"
        else:
            if q3 in NO:
                return "Low"
            else:
                if q4 in NO:
                    return "Some concerns"
                else:
                    return "High"

def compute_domain4_judgement(result) -> str | None:
    """
    Compute the risk of bias judgement for the measurement of the outcome domain.
    """

    #domain = result['domains']['domain_4'];
    domain = None;
    if 'domain_4' in result['domains']:
        domain = result['domains']['domain_4'];
    else:
        domain = result['domains'][3];



    q1 = domain['Q4_1']['answer'].lower()  # 2.1
    q2 = domain['Q4_2']['answer'].lower()
    q3 = domain['Q4_3']['answer'].lower()
    q4 = domain['Q4_4']['answer'].lower()
    q5 = domain['Q4_5']['answer'].lower()

    if None in (q1, q2, q3, q4, q5):
        return None

    YES = {"Yes".lower(), "Probably Yes".lower()}
    NO = {"No".lower(), "Probably No".lower()}

    if q1 in YES:
        return "High"
    else:
        if q2 in YES:
            return "High"
        elif q2 in NO:
            if q3 in NO:
                return "Low"
            else:
                if q4 in NO:
                    return "Low"
                else:
                    if q5 in NO:
                        return "Some concerns"
                    else:
                        return "High"
        else:  # q2 in NI
            if q3 in NO:
                return "Some concerns"
            else:
                if q4 in NO:
                    return "Some concerns"
                else:
                    if q5 in NO:
                        return "Some concerns"
                    else:
                        return "High"


def compute_domain5_judgement(result) -> str | None:
    """
    Risk-of-bias algorithm for Domain 5 – selection of the reported result.
    Diagram logic:

        • If either Q5.2 or Q5.3 = Y/PY  → High risk
        • If neither Y/PY but ≥1 NI      → Some concerns
        • If both Q5.2 & Q5.3 = N/PN:
              – Q5.1 = Y/PY              → Low risk
              – Q5.1 = N/PN/NI           → Some concerns
    """
    domain = result['domains']['domain_5'];
    q1 = domain['Q5_1']['answer'].lower()  # 2.1
    q2 = domain['Q5_2']['answer'].lower()
    q3 = domain['Q5_3']['answer'].lower()


    if None in (q1, q2, q3):
        return None  # incomplete

    YES = {"Yes".lower(), "Probably Yes".lower()}
    NO = {"No".lower(), "Probably No".lower()}

    if q2 in YES or q3 in YES:
        return "High"
    if q2 in NO and q3 in NO:
        if q1 in YES:
            return "Low"
        else:
            return "Some concerns"
    else:
        return "Some concerns"

def compute_overall_judgement(judgement_list) -> str | None:
    """Return the overall risk-of-bias judgement for the framework.

    The judgement corresponds to the highest (worst) domain judgement
    across all domains except any explicitly named "Overall". If any
    domain judgement is missing, ``None`` is returned.

    Returns
    -------
    str | None
        "Low", "Some concerns", or "High" when all domain judgements are
        available, otherwise ``None``.
    """

    ranking = {"low": 0, "some concerns": 1, "high": 2}
    inverse_ranking = {0: "Low", 1: "Some concerns", 2: "High"}

    worst = 0
    for judgement in judgement_list:
        if judgement is None:
            return None

        score = ranking.get(judgement.lower(), 0)
        worst = max(worst, score)

    return inverse_ranking[worst]


def rob2_analysis(result,  domain_type, model="gpt-5"):
    if domain_type == 'domain1':
        prompt = build_rob2_domain1_answer_prompt(result);
    elif domain_type == 'domain2':
        prompt = build_rob2_domain2_answer_prompt(result);
    elif domain_type =="domain2_deviations":
        prompt = build_rob2_domain2_adhering_answer_prompt(result);
    elif domain_type == "domain3":
        prompt = build_rob2_domain3_answer_prompt(result)
    elif domain_type == "domain4":
        prompt = build_rob2_domain4_answer_prompt(result)
    elif domain_type == "domain5":
        prompt = build_rob2_domain5_answer_prompt(result)


    #print(f" prompt is {prompt}")
    match_result = None;
    if model == "gpt-5":
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
        match_result = json.loads(response_text)
       # return match_result
    elif model.__contains__('claude'):
        response = anthropic_client.messages.create(
            max_tokens=21024,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=model,
        )

        response_text = response.content[0].text;
        response_text = response_text.replace("```json", "")
        response_text = response_text.replace("```", "");
        print(f" response_text is {response_text}");
        match_result = json.loads(response_text)
    elif model == "gemini-2.5-pro":
        #genai_client
        response = genai_client.models.generate_content(
            model='gemini-2.5-pro',
            contents=prompt,
            config=types.GenerateContentConfig()
        )

        response_text = response.text;
        response_text = response_text.replace("```json", "")
        response_text = response_text.replace("```","");
        match_result = json.loads(response_text)
        #return match_result;
        #print(response)
    if domain_type == "domain1":
        judgement = compute_domain1_judgement(match_result);
        match_result['domains']['domain_1']['judgment'] = judgement;
    elif domain_type == "domain2":
        judgement = compute_domain2_judgement(match_result);
        match_result['domains']['domain_2']['judgment'] = judgement;
    elif domain_type == "domain2_deviations":
        judgement = compute_domain2_deviations_judgement(match_result);
        match_result['domains']['domain_2']['judgment'] = judgement;
    elif domain_type == "domain3":
        judgement = compute_domain3_judgement(match_result);
        match_result['domains']['domain_3']['judgment'] = judgement;
    elif domain_type == "domain4":
        judgement = compute_domain4_judgement(match_result);
        match_result['domains']['domain_4']['judgment'] = judgement;
    elif domain_type == "domain5":
        judgement = compute_domain5_judgement(match_result);
        match_result['domains']['domain_5']['judgment'] = judgement;

    return match_result;


   #print(f" response is {response_text}")
    #match_result = json.loads(response_text)

   # response_text = response.text;
   # response_text = response_text.replace("```json", "")
    #response_text = response_text.replace("```", "");
   # print(f' match_result is {response_text}')


