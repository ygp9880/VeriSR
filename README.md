---

# ROB2 Analysis Pipeline

A modular pipeline for extracting structured content from PDFs, performing ROB2 bias assessments with LLMs, and validating meta-analysis datasets.

---

## 💡 Overview

This project provides a command-line based processing pipeline that supports:


### ✅ **1. ROB2 risk-of-bias evaluation** (Domain1–Domain5 + overall)

Automatically evaluates ROB2 domains using a large language model (e.g., GPT-5).

### ✅ **2. Meta-analysis data validation**

Supports both **binary outcomes** and **continuous outcomes**.

### ✅ **2. Report generate**

### ✅ **4. Configurable runtime**

Using:

* `.env` variables
* Command-line arguments
* Logging to file + console
* Modular task-based execution (`rob`, `report`, `check`)

---

## 📂 Project Structure

```
evaluation_Systematic_review/
│
├─ data/                    # Input data: text and Excel files
│   ├─ SR1.txt
│   ├─ SR1Aguloetal2023.txt
│   ├─ SR1Hamiltonetal2020.txt
│   ├─ SR1Hamiltonetal2022.txt
│   ├─ SR1Krausetal2023.txt
│   ├─ SR1Mosleyetal2023.txt
│   ├─ SR1Thomasetal2021.txt
│   └─ SR1Thomasetal2021.xlsx
│
├─ prompt/                  # LLM prompt templates and processing functions
│   ├─ __init__.py
│   ├─ bin_meta_code.py         # Binary outcome meta-analysis checks
│   ├─ continue_meta_code.py    # Continuous outcome checks
│   ├─ extract_info.py          # Extract structured info from text
│   ├─ meta_analysis.py
│   ├─ report_generator.py
│   ├─ ROB2_analysis.py         # Main ROB2 evaluation
│   ├─ ROB2_analysis_bak.py     # Backup / old ROB2 version
│   ├─ rr_test.py
│   └─ system_prompt.py         # Base prompts for LLMs
│
├─ report/                  # Report generation and plotting
│   ├─ __init__.py
│   ├─ check_info.py
│   ├─ plot_meta_forest.py     # Forest plot generation
│   ├─ report_info.py          # Extract report sections
│   ├─ report_to_doc.py        # Generate DOCX reports
│   └─ rob_compare.py          # Compare ROB2 results across studies
│
├─ utils/                   # Utility functions
│   ├─ __init__.py
│   ├─ alg_util.py
│   └─ content_utils.py       # read/write text, JSON
│
├─ vector/                  # Vector search / embeddings
│   ├─ __init__.py
│   └─ vector_search.py
│
├─ main.py                  # Entry point with command-line args
├─ .env                     # Environment variables
└─ mylog.log                # Runtime logs

```

---

## ⚙️ Installation

### **1. Install dependencies**

```bash
pip install -r requirement.txt
```


```

---

## 🔧 Environment Variables

Create a `.env` file in the root directory:

```
OPENAI_API_KEY=
GEMINI_KEY=
OPENAI_BASE_URL=

```

---

## 🚀 How to Run

### **1. Base command**

```bash
python main.py
```

### **2. Override via arguments**

| Argument      | Description                    |
| ------------- | ------------------------------ |
| `--command`   | rob / report / check           |
| `--meta_path` | path to metadata               |
| `--data_path` | input PDF directory            |
| `--save_path` | directory for generated output |

Example:

```bash
python main.py --command rob --data_path ./data --save_path ./save
```

---

## 🧠 Commands

### ### **🔹 1. ROB2 Evaluation**

```
--command rob
```

For each file in `data_path`, this will:

* load the text
* extract ROB2-specific info
* run 5 domain evaluations via LLM
* compute overall judgment
* save results as JSON

Output example:

```
/save/study1.json
/save/study2.json
```

---

### ### **🔹 2. Report Info Extraction**

```
--command report
```

This reads a metadata file and extracts sections such as:

* report_1
* report_3_1
* report_3_2
* report_3_3
* report_3_4
* report_3_5

Usage:

```bash
python main.py --command report --save_path ./meta/report.txt
```

---

### ### **🔹 3. Meta-analysis Checking**

```
--command check
```

This command:

* loads extracted meta-analysis data
* determines whether the dataset is binary or continuous
* runs appropriate statistical validation
* outputs corrected values + diagnostics

Output example:

```
SR4_output.json
```

---

## 📝 Logging

Two logging channels are enabled:

1. **Console**
2. **File `mylog.log`**

You will see detailed information for debugging, including:

* current configuration
* file processing progress
* ROB2 domain evaluation results

---

## 🧩 Key Functions

### `rob_run(file_path, file, save_path)`

Performs ROB2 domain analysis.

### `extract_report_info()`

Extracts predefined structured items from report text.

### `meta_check()`

Checks consistency of meta-analysis datasets (binary & continuous).

### `read_content()` / `write_str_to_file()`

Basic IO utilities.

---

## 📤 Output Example

### ROB2 JSON Output

```json
{
    "domains": [
        { "domain_1": { "judgment": "low" } },
        { "domain_2": { "judgment": "some concerns" } },
        ...
    ],
    "overall": "some concerns"
}
```

---

