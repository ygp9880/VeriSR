# VeriSR

`VeriSR` is an agent for systematic review evidence workflows.  
It orchestrates PDF-to-text processing, structured information extraction, consistency verification, ROB2 generation, and final report export.

## Agent Overview

This system is a large language model–based intelligent agent designed to assist in the auditing of systematic reviews. 
Using pharmacogenomics as an example, it enables automated review and textual interpretation of data extraction, meta-analysis, and risk-of-bias assessment results reported
in systematic review articles. The study aims to provide empirical evidence for the development of an intelligent, traceable, and verifiable quality control framework for systematic reviews, 
thereby improving the quality of peer review and reducing the risk of publishing flawed or biased studies.
It supports an end-to-end workflow including:

* PDF full-text extraction (powered by Google Gemini)
* Meta-data extraction
* Data consistency and correctness checks
* Automated ROB2 (Risk of Bias 2) generation, refactoring, and comparison
* Automatic report generation (Word / JSON)
* Merging multiple reports into a single document



## Project Structure

Top-level folders and their responsibilities:

| Folder | Contains | Function |
|---|---|---|
| `all_txt/` | Meta-review text files (for example `SR1.txt`), included-study text files under subfolders (for example `SR1/*.txt`), and runtime intermediate files | Primary working data space for agent ingestion, extraction, verification, and ROB2/report staging |
| `check/` | Verification modules such as `check_info.py`, `meta_check.py`, `meta_analysis.py` | Verification agent logic that checks extracted content consistency and performs meta-check tasks |
| `extract/` | Extraction modules such as `etract_info_main.py`, `extract_info.py`, `meta_extract_info.py` | Extraction agent logic that parses source content and produces structured outputs |
| `meta/` | Meta-processing helpers such as `continue_meta_code.py`, `bin_meta_code.py` | Shared meta-analysis support logic used by checking/reporting steps |
| `pdf/` | Source PDF inputs (for example `SR1.pdf`) | Input area for PDF ingestion before conversion/extraction |
| `prompt_1/` | Prompt templates and prompt-driven modules (for extraction, meta analysis, reporting, ROB2) | Prompt layer for LLM-backed agent behaviors |
| `report/` | Report assembly and export modules such as `report_merge.py`, `report_to_doc.py`, `rob2_report.py` | Reporting agent logic that transforms intermediate outputs into reviewable report artifacts |
| `report_doc/` | Generated report outputs (typically `.docx` and ROB2-related text artifacts) | Final export/output directory for deliverables |
| `rob2_meta/` | ROB2 modules such as `rob2_generate.py`, `ROB2_analysis.py` | ROB2 agent logic for risk-of-bias generation/refinement |
| `utils/` | Shared helpers such as `client_utils.py`, `content_utils.py`, `alg_util.py` | Cross-module utilities for API client setup, file/content operations, and common helpers |

Top-level key files:

- `main.py`: CLI entry point and command router for agent tasks (`process`, `extract`, `check_info`, `rob2_generate`, etc.)
- `run_full_pipeline.py` and `run_full_pipeline.sh`: one-command end-to-end orchestration scripts
- `rerun_meta_report.sh` and `rerun_meta_report.bat`: rerun meta-check + final report merge only
- `prompt_extract_content.txt`: auxiliary prompt text resource

## Requirements

- Python 3.10+ (recommended)
- Valid model API credentials

Install dependencies:

```bash
pip install openai google-genai anthropic python-dotenv python-docx openpyxl numpy pandas scipy matplotlib PyPDF2 camelot-py json5
```

## Configuration

Create a `.env` file in the repository root (you can copy from `.env.example`):

```env
gemini_key=YOUR_GEMINI_KEY
openai_key=YOUR_OPENAI_KEY
openai_base_url=YOUR_OPENAI_BASE_URL
OPENAI_MODEL=YOUR_MODEL_NAME
```

Do not commit real API keys or private endpoints.

## Quick Start

1. Validate API credentials:

```bash
python main.py -c test_gemini
```

2. Run the standard agent workflow steps:

```bash
python main.py -c process -dir pdf
python main.py -c extract -m all_txt/SR1.txt -data all_txt/SR1
python main.py -c check_info -m all_txt/SR1.txt -data all_txt/SR1
python main.py -c rob2_generate -data all_txt/SR1 -s all_txt/SR1/rob2_result
```

## Full Agent Workflow (Cross-Platform)

Run the end-to-end agent workflow with one command:

```bash
python run_full_pipeline.py \
  --meta-name SR1 \
  --meta-file all_txt/SR1.txt \
  --study-dir all_txt/SR1 \
  --work-dir all_txt \
  --report-file report_doc/SR1_output.docx
```

On Linux/macOS, shell wrapper is also available:

```bash
chmod +x run_full_pipeline.sh
./run_full_pipeline.sh \
  --meta-name SR1 \
  --meta-file all_txt/SR1.txt \
  --study-dir all_txt/SR1 \
  --work-dir all_txt \
  --report-file report_doc/SR1_output.docx
```

## Typical Outputs

- `all_txt/extract_result_all_SR1.json`
- `all_txt/SR1_meta_check_output.json`
- `all_txt/SR1_rob2_compare.txt`
- `all_txt/SR1_report_*.json`
- `all_txt/SR1_rob2_*.txt`
- `report_doc/SR1_output.docx`

## Rerun Meta + Final Report Only

If extraction/verification steps are already done and you only need to rerun meta-check and merge:

Linux/macOS:

```bash
./rerun_meta_report.sh SR1
```

Windows:

```bat
rerun_meta_report.bat SR1
```

Optional argument order: `META_NAME WORK_DIR REPORT_FILE`  
Defaults: `SR1`, `all_txt`, `report_doc/SR1_output.docx`

## Troubleshooting

- Credential errors: run `python main.py -c test_gemini` first
- Missing dependencies: re-check Python version and installed packages
- Path issues: run commands from repository root and verify relative paths


