import os;
from utils.content_utils import read_content;
from openai import  OpenAI
client = OpenAI(base_url='https://api.openai-proxy.org/v1', api_key='sk-p8KW4EtRdh7i2MWf9o7YmmQZihySS5HA5D0Z1iEdddtLURpJ');

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

base_path = "D:\\project\\zky\\paperAgent\\check_data";
data_files = os.listdir(base_path);
result = "";
for file in data_files:
    if file.__contains__("json"):
        full_path = base_path + "\\" + file;
        content = read_content(full_path);
        result = result + content + "\n";

prompt = generate_error_extraction_prompt_en(result);

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
print(response_text);