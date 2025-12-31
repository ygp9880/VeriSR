from utils.content_utils import read_content;
from openai import  OpenAI
client = OpenAI(base_url='https://api.openai-proxy.org/v1', api_key='sk-p8KW4EtRdh7i2MWf9o7YmmQZihySS5HA5D0Z1iEdddtLURpJ');

def generate_audit_prompt(content, report_3_2_3):
    """
    Generate a full English prompt for creating an Audit Summary
    based on extraction JSON content and discrepancy tables.
    """

    prompt = f"""
You are an expert in systematic review methodology, data extraction quality auditing, and evidence verification.  
Your task is to analyze the provided extraction JSON content and discrepancy tables, and then produce a concise, rigorous “Audit Summary” written in English.

--------------------------------------
INPUT CONTENT
--------------------------------------
Extraction content:
{content}

Discrepancy tables:
{report_3_2_3}

--------------------------------------
OUTPUT REQUIREMENTS
--------------------------------------

### (A) Overall Summary
Write a short paragraph (3–5 sentences) that:
- Evaluates the rigor of the extraction process,
- Identifies systemic or critical extraction errors,
- Explains potential impacts on reliability,
- States that full verification against original sources is required.

### (B) Key Issues Section (bullet-point format)
List 4–6 major issues, each following this structure:

1. Issue Title (e.g., “Major baseline inconsistencies”)
   - Brief description (1–2 sentences), specifying affected studies when relevant.
   - Link the issue to discrepancy category (e.g., Table 2, Table 3, Table 4).
   - Provide explicit corrective actions (e.g., re-extraction, recalculation, annotation, exclusion).

Do NOT copy table text; summarize the risks revealed by the tables.

### Writing Style Requirements
- Professional, precise, methodologically rigorous tone.
- Focus on key risks and required actions.
- Entirely in English.
- Reference studies using numbers (e.g., [21]).
- Structure must follow the final output format below.

--------------------------------------
FINAL OUTPUT FORMAT
--------------------------------------

### Audit Summary

(Overall summary paragraph)

1. (Issue Title)
   - (Description of issue and affected studies)
   - (Discrepancy category)
   - (Corrective action)

2. (Issue Title)
   - (Description)
   - (Corrective action)

(Provide 4–6 issues total)
"""

    return prompt


def generate_audit(base_path, meta_name):
    file_path = f"{base_path}\\";


conent = read_content("D:\\project\\zky\\paperAgent\\result\\report_3_2.json");
report_3_2_3 = read_content("D:\\project\\zky\\paperAgent\\result\\report_3_2_3.txt");
#print(f" content is {conent}");
#print(f" report_3_2_3 is {report_3_2_3}");
prompt = generate_audit_prompt(conent,report_3_2_3);
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
print(f" reponse is {response_text}");