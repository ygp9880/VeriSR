from utils.content_utils import read_content;
from openai import  OpenAI
client = OpenAI(base_url='https://api.openai-proxy.org/v1', api_key='sk-p8KW4EtRdh7i2MWf9o7YmmQZihySS5HA5D0Z1iEdddtLURpJ');

def get_bias_and_audit_prompt(meta_analysis_text: str) -> str:
    """
    根据提供的 Meta 分析文本生成用于大模型的 Prompt，
    指示模型返回两个字段：risk_of_bias_review 和 original_evidence。

    参数:
        meta_analysis_text (str): Meta分析文章内容

    返回:
        str: 用于大模型的完整 Prompt
    """
    prompt = f"""
You are an expert in systematic review methodology, risk-of-bias assessment, and evidence quality auditing.

Task:
- Analyze the following meta-analysis text.
- Generate a structured risk-of-bias review and quote supporting evidence from the text.
- Output must be in English in the following JSON format,and keep each field to a maximum of two or three sentences.

{{
    "risk_of_bias_review": "<请生成偏倚风险审核结果>",
    "original_evidence": "<引用的原文证据>"
}}

Meta-analysis text:
\"\"\"
{meta_analysis_text}
\"\"\"
"""
    return prompt


meta_analysis_text = read_content("D:\\project\\zky\\paperAgent\\all_txt\\SR1.txt");
#print(f" meta_analysis_text is {meta_analysis_text} ");
#print(f" content is {conent}");
#print(f" report_3_2_3 is {report_3_2_3}");

prompt = get_bias_and_audit_prompt(meta_analysis_text);
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
