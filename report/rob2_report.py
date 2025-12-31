import os;
from utils.content_utils import read_content;
import json;
from openai import  OpenAI

client = OpenAI(base_url='https://api.openai-proxy.org/v1', api_key='sk-p8KW4EtRdh7i2MWf9o7YmmQZihySS5HA5D0Z1iEdddtLURpJ');

def extract_trial_fields(article_text: str) -> str:
    """
    Extracts clinical trial information from the provided text and outputs in readable text format.

    Args:
        article_text (str): Full text of the article or study to extract from.

    Returns:
        str: Extracted information in a text format.
    """
    prompt = f"""
You are an expert in clinical trial data extraction. Extract the following fields from the provided text and output them in clear, readable text. 
For fields with predefined options, select the most appropriate one. If information is missing, write "Not reported".

Fields to extract:
1. Study: Name of the study.
2. Output Format: Specify the format used for results (e.g., mean ± SD, median [IQR], risk ratio, etc.).
3. Article ID: Unique identifier of the source article.
4. Outcome Name: Name of the primary or secondary outcome.
5. Outcome Result: Extract the reported result for the outcome.
6. Registration Number: Clinical trial registration number, if available.
7. Study Design: Choose one:
   - Individually-randomized parallel-group trial
   - Cluster-randomized parallel-group trial
   - Individually randomized cross-over (or other matched) trial
8. Experimental Definition: Definition of the experimental intervention.
9. Comparator Definition: Definition of the comparator or control intervention.
10. Intervention Effect: Choose one:
    - intention-to-treat
    - per-protocol
11. Study Sources: Choose one or more from the following:
    - Journal article(s)
    - Trial protocol
    - Statistical analysis plan (SAP)
    - Non-commercial trial registry record (e.g. ClinicalTrials.gov record)
    - Company-owned trial registry record (e.g. GSK Clinical Study Register record)
    - “Grey literature” (e.g. unpublished thesis)
    - Conference abstract(s) about the trial
    - Regulatory document (e.g. Clinical Study Report, Drug Approval Package)
    - Research ethics application
    - Grant database summary (e.g. NIH RePORTER or Research Councils UK Gateway to Research)
    - Personal communication with trialist
    - Personal communication with the sponsor

Article Text:
\"\"\"{article_text}\"\"\"

Output format example:

Study: Kraus et al  
Output Format: mean ± SD  
Article ID: 12345  
Outcome Name: Pain intensity  
Outcome Result: Experimental group reduced by 2.3 points, Control group reduced by 1.1 points  
Registration Number: NCT01234567  
Study Design: Individually-randomized parallel-group trial  
Experimental Definition: Pharmacogenomic-guided opioid therapy  
Comparator Definition: Usual care  
Intervention Effect: intention-to-treat  
Study Sources: Journal article(s), Clinical trial registry
"""

    response = client.chat.completions.create(
        model="gpt-5",
        messages=[{"role": "user", "content": prompt}]
    )

    # Extract and return the text content
    return response.choices[0].message.content

def json_to_txt(data, output_file, field_content):
    """
    Convert ROB2 JSON data to formatted TXT.

    Args:
        data (dict): JSON object containing the ROB2 assessment.
        output_file (str): Path to output TXT file.
    """
    lines = []

    for idx, domain in enumerate(data.get("domains", []), start=1):
        lines.append(f"Domain {idx}")
        for q_key, q_val in domain.items():
            if q_key == "judgment":
                # Domain-level judgment
                judgment = q_val
                # Try to extract average confidence if available
                confidences = []
                for k, v in domain.items():
                    if isinstance(v, dict) and "confidence" in v:
                        conf = v["confidence"]
                        if isinstance(conf, dict) and "percentage" in conf:
                            confidences.append(conf["percentage"])
                        elif isinstance(conf, str):
                            # Try extract percentage from string like 'High (95%)'
                            import re
                            match = re.search(r'\((\d+)%\)', conf)
                            if match:
                                confidences.append(int(match.group(1)))
                avg_conf = int(sum(confidences)/len(confidences)) if confidences else 0
                lines.append(f"{q_key}: {judgment} ({avg_conf}%)")
            else:
                # Question-level
                answer = q_val.get("answer", "No Information")
                conf = q_val.get("confidence", "")
                if isinstance(conf, dict) and "percentage" in conf:
                    conf_pct = conf["percentage"]
                else:
                    import re
                    match = re.search(r'\((\d+)%\)', str(conf))
                    conf_pct = int(match.group(1)) if match else 0
                analysis = q_val.get("analysis", "")
                lines.append(f"{q_key} : {answer} ({conf_pct}%)")
                lines.append(f"{analysis}")
        lines.append("")  # Empty line between domains

    overall = data.get("overall", "Unclear")
    # Try to average domain confidences
    domain_confs = []
    for domain in data.get("domains", []):
        for k, v in domain.items():
            if k != "judgment" and isinstance(v, dict) and "confidence" in v:
                conf = v["confidence"]
                if isinstance(conf, dict) and "percentage" in conf:
                    domain_confs.append(conf["percentage"])
                elif isinstance(conf, str):
                    match = re.search(r'\((\d+)%\)', conf)
                    if match:
                        domain_confs.append(int(match.group(1)))
    overall_conf = int(sum(domain_confs)/len(domain_confs)) if domain_confs else 0
    lines.append(f"Overall Bias Risk for the Article: {overall} ({overall_conf}%)")

    # Write to file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(field_content)
        f.write("\n".join(lines))


def paper_to_doc(paper_path, rob2_full_path, save_path):
    content = read_content(rob2_full_path);
    rob2_json = json.loads(content);

    sr_content = read_content(paper_path);
    field_content = extract_trial_fields(sr_content);

    json_to_txt(rob2_json, save_path, field_content)


'''
file_name = "SR1Thomasetal2021.txt";
data_path=f"D:\\project\\zky\\paperAgent\\all_txt\\SR1\\{file_name}";
rob2_path=f"D:\\project\\zky\\paperAgent\\all_txt\\SR1\\rob2_result\\{file_name}";
save_path="D:\\project\\zky\\paperAgent\\report_doc\\SR1_rob2_6.txt";
paper_to_doc(data_path, rob2_path,save_path);
'''

for j in range(1, 6):
    print(f" i is {j}");

'''
path = "D:\\project\\zky\\paperAgent\\rob2_run_gpt_sr1";
rob2_files = os.listdir(path);
sr_path = "D:\\project\\zky\\paperAgent\\all_txt\\SR1";
sr_files = os.listdir(sr_path);
for file in sr_files:
    if file.__contains__(".txt"):
        rob2_full_path = path + "\\" + file;
        sr_full_path = sr_path + "\\" + file;
        content = read_content(rob2_full_path);
        rob2_json = json.loads(content);

        sr_content = read_content(sr_full_path);
        field_content = extract_trial_fields(sr_content);

        json_to_txt(rob2_json, f"D:\\project\\zky\\paperAgent\\result\\{file}", field_content)
        #print(f" rob2 path is {rob2_full_path}");

        #print(f" field_content is {field_content} ");
      #  print(f" sr path is {sr_full_path}");
'''