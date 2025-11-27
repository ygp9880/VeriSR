from openai import OpenAI

client = OpenAI(base_url='https://api.openai-proxy.org/v1', api_key='sk-p8KW4EtRdh7i2MWf9o7YmmQZihySS5HA5D0Z1iEdddtLURpJ');

def build_meta_audit_prompt(data_consistency_text: str,original_txt :str) -> str:
    """
    构建用于Meta分析审核的Prompt，只插入“数据一致性复核”部分，其余由模型生成。
    参数：
        data_consistency_text: str，“数据一致性复核”部分的结果描述
    返回：
        prompt_text: str，完整Prompt
    """
    prompt = f"""
你是一名循证医学与Meta分析方法学专家。
请基于下方提供的“数据一致性复核结果”跟META分析原文
完整撰写一份系统综述/Meta分析的“检索与数据分析过程审核报告”。

=======================
META分析的原文是：
{original_txt}
=======================
=======================
【已提供的原始分析结果】
数据分析过程审核 - 数据一致性复核：
{data_consistency_text}
=======================

【任务要求】
1. 请生成完整的报告结构，包括以下五个部分：
   一、检索过程审核
      1. 检索策略完整性:
         是否详细描述了数据库名称、检索词、检索时间范围、检索步骤？
         是否提供检索式或附录？
      2. 检索执行与独立性
         是否由两人独立进行？
         是否有第三方仲裁？
   二、风险偏倚评价过程审核
      1.评价工具选择
        纳入研究类型是否与评价工具匹配（如RCT → RoB 2.0）？
      2. 评价过程规范性
        是否由两人独立完成？
        分歧是否经第三方解决？
        是否说明评价者是否受过培训？
        是否提供了判断依据或原文引用？
      3. 结果呈现与充分性
         是否提供了风险偏倚总结图或表？
	     是否对所有纳入研究和主要结局均进行评估？
	     是否进行了敏感性分析以验证偏倚影响？
   三、数据提取过程审核
      1. 数据提取流程
         是否说明提取方法和内容？
	    是否由两人独立提取？
	    是否说明如何解决分歧？   
	  2.提取内容完整性
	    是否包括研究特征、参与者特征、干预措施、结局指标？
        是否提取了所有预设结局？
   四、数据分析过程审核
       1. 数据一致性复核
          Meta分析表格/森林图中的数据是否与原研究一致？
       2. 效应量选择与模型合理性
	      效应量（SMD、OR、RR等）选择是否合理？
	      模型选择（固定效应或随机效应）是否依据异质性？
	  3. 数据转换与统计方法
	      是否说明数据转换方法？
	      是否明确使用的软件与版本？
	  4. 异质性处理
	      是否报告I²和Q检验结果？
          是否进行亚组分析或Meta回归？
   五、敏感性分析与发表偏倚审核
      1. 敏感性分析
         是否通过剔除高风险文献或更换模型验证结论稳健性？
      2. 发表偏倚分析
          是否进行了漏斗图或Egger’s检验？
         样本数量是否足以支持发表偏倚分析？
   六、总体结论
        
2. 其中：
   - “四、数据分析过程审核”中的“数据一致性复核”请直接使用我提供的分析结构；
  
3. 所有审核意见应采用正式、学术性中文；
4. 在最后增加“总体审核结论”，总结研究方法的规范性、透明度与改进方向。

生成的报告格式如下：
一、检索过程审核
1. 检索策略完整性
•	是否详细描述了数据库名称、检索词、检索时间范围、检索步骤？
•	是否提供检索式或附录？
审核意见：
（填写示例）【结合原文分析】原Meta分析提供了完整的检索策略，包括数据库、检索词及检索日期，检索过程透明，可重复性高。


"""
    return prompt


def generate_meta_audit_report(data_consistency_text: str,original_txt :str):
    """生成审核报告"""
    prompt = build_meta_audit_prompt(data_consistency_text, original_txt)

    response = client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": "你是循证医学和Meta分析方法学专家。"},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content



file_path = "D:\\project\\zky\\paperAgent\\txt\\meta-analyze.txt"  # 替换为你的文件路径

def read_content(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    return content;


# ========== 示例使用 ==========
if __name__ == "__main__":
    content = read_content(file_path);
    #print(f" content is {content}");
    my_result = """
    对META分析结构数据检查如下：study_name is Agullo et al 2023 mean_exp check result: Truesd_exp check result: Truen_exp check result: Truemean_ctrl check result: Truesd_ctrl check result: Truen_ctrl check result: True study_name is Kraus et al 2024 mean_exp check result: Truesd_exp check result: Truen_exp check result: Truemean_ctrl check result: Truesd_ctrl check result: Truen_ctrl check result: False study_name is Thomas et al 2021 mean_exp check result: Falsesd_exp check result: Falsen_exp check result: Falsemean_ctrl check result: Falsesd_ctrl check result: Falsen_ctrl check result: True study_name is Kraus et al 2024 mean_exp check result: Falsesd_exp check result: Falsen_exp check result: Truemean_ctrl check result: Falsesd_ctrl check result: Falsen_ctrl check result: False study_name is Thomas et al 2021 mean_exp check result: Truen_exp check result: Falsemean_ctrl check result: Truen_ctrl check result: False
    """

    report = generate_meta_audit_report(content, my_result)
    print(f" report is {report} ");

