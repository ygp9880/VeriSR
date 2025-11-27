import json
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH


def json_to_word(json_data, output_filename='output.docx'):
    """
    将JSON数据转换为格式化的Word文档

    参数:
        json_data: JSON字符串或字典
        output_filename: 输出的Word文件名
    """
    # 如果输入是字符串，解析为字典
    if isinstance(json_data, str):
        data = json.loads(json_data)
    else:
        data = json_data

    # 创建Word文档
    doc = Document()

    # 添加标题

    doc.add_heading('一. Evaluation Summary', level=1)

    doc.add_heading('Title', level=2)
    p = doc.add_paragraph(data.get('Title', ''))
    p.paragraph_format.space_after = Pt(12)

    # 添加目标/目的
    doc.add_heading('Objective', level=2)
    p = doc.add_paragraph(data.get('Objective', ''))
    p.paragraph_format.space_after = Pt(12)

    # 添加研究信息
    doc.add_heading('Study Information', level=2)
    info_items = [
        ('Number of studies included', data.get('Number_of_studies_included', 'N/A')),
        ('Total sample size', data.get('Sample_size_total', 'N/A'))
    ]

    for label, value in info_items:
        p = doc.add_paragraph()
        p.add_run(f'{label}: ').bold = True
        p.add_run(str(value))

    # 添加纳入标准
    doc.add_heading('Inclusion Criteria', level=2)
    inclusion = data.get('Inclusion_criteria', {})
    for key, value in inclusion.items():
        p = doc.add_paragraph()
        p.add_run(f'{key}: ').bold = True
        p.add_run(str(value))
        p.paragraph_format.left_indent = Inches(0.25)

    # 添加主要结果
    doc.add_heading('Results', level=2)
    main_results = data.get('Results', [])
    for i, result in enumerate(main_results, 1):
        p = doc.add_paragraph(result, style='List Number')
        p.paragraph_format.space_after = Pt(6)

    # 添加注释
    if 'Notes' in data:
        doc.add_heading('Notes', level=2)
        p = doc.add_paragraph(data.get('Notes', ''))
        # 设置注释段落的背景色（通过添加边框和底纹）
        p.paragraph_format.space_after = Pt(12)

    # 保存文档
    doc.save(output_filename)
    print(f'Word文档已成功创建: {output_filename}')

    return output_filename


def add_methodology_to_word(doc, json_data):
    """
    将方法学相关的JSON数据添加到现有Word文档

    参数:
        doc: Document对象（现有的Word文档）
        json_data: JSON字符串或字典
    """
    # 如果输入是字符串，解析为字典
    if isinstance(json_data, str):
        data = json.loads(json_data)
    else:
        data = json_data

    # 添加分页符
    doc.add_page_break()

    # 添加方法学部分的主标题
    doc.add_heading('二. Report Body', level=1)
    doc.add_heading('1. Literature Search Review', level=1)

    # 1. 搜索策略
    if 'Search_Strategy' in data:
        doc.add_heading('Search Strategy', level=3)
        p = doc.add_paragraph(data['Search_Strategy'])
        p.paragraph_format.space_after = Pt(12)
        p.paragraph_format.line_spacing = 1.15

    # 2. 筛选流程
    if 'Screening_Process' in data:
        doc.add_heading('Screening Process', level=3)
        p = doc.add_paragraph(data['Screening_Process'])
        p.paragraph_format.space_after = Pt(12)
        p.paragraph_format.line_spacing = 1.15

    # 3. 结果呈现
    if 'Results_Presentation' in data:
        doc.add_heading('Results Presentation', level=3)
        p = doc.add_paragraph(data['Results_Presentation'])
        p.paragraph_format.space_after = Pt(12)
        p.paragraph_format.line_spacing = 1.15

    # 4. 方法学总结
    if 'Methodology_Summary' in data:
        doc.add_heading('Methodology Summary', level=3)
        p = doc.add_paragraph(data['Methodology_Summary'])
        p.paragraph_format.space_after = Pt(12)
        p.paragraph_format.line_spacing = 1.15

        # 为总结添加浅色背景效果（通过添加表格实现）
        # 注：python-docx不直接支持段落背景色，这里用边框来突出显示
        from docx.oxml.ns import qn
        from docx.oxml import OxmlElement

        # 添加底纹
        shading_elm = OxmlElement('w:shd')
        shading_elm.set(qn('w:fill'), 'F0F0F0')  # 浅灰色背景
        p._element.get_or_add_pPr().append(shading_elm)

    return doc



if __name__ == '__main__':
    # 读取JSON文件

    title_map = {};
    title_map[1] = "1. Literature Search Review";
    title_map[2] = "2. Data Extraction Review";
    title_map[3] = "3. Risk of Bias Assessment";
    title_map[4] = "4. Meta-Analysis Review";
    title_map[5] = "5. Additional Analyses and Evidence Quality Assessment";

    index = 5;

    with open(f'D:\\project\\zky\\paperAgent\\all_txt\\SR1\\report_result\\report_3_{index}.txt', 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    # 转换为Word
    #json_to_word(json_data, 'output.docx')
    keys = json_data.keys();
    doc = Document('output.docx');
    title = title_map[index];
    print(f" title is {title}");
    doc.add_heading(title, level=2)

    for key in keys:
        value = json_data[key];
        doc.add_heading(key, level=3)

        p = doc.add_paragraph(value)
        p.paragraph_format.space_after = Pt(12)
        p.paragraph_format.line_spacing = 1.15
        print(f" value is {value}");
    #print(f" json_data is {json_data}");
    doc.save("output.docx")
    '''
    doc = Document('output.docx');
    doc = add_methodology_to_word(doc,json_data);
    doc.save("output_1.docx")
    '''