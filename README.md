# README

## Overview

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

All functions are orchestrated via **`main.py` using command-line arguments**.

---

## Requirements

* Python ≥ 3.9
* Windows / Linux / macOS

### Install Dependencies

```bash
pip install -r requirement.txt
```

(Additional dependencies may be required by submodules.)

---

## Environment Variables

Create a `.env` file in the project root directory:

```env
gemini_key=YOUR_GOOGLE_GEMINI_API_KEY
```

The application will automatically load this key at runtime.

---

## Project Structure

```
paperAgent/
├── main.py
├── prompt_extract_content.txt
├── agent.log
├── pdf/                     # Input PDF files
├── meta/                    # Meta text and intermediate results
├── data/                    # Extracted structured data
├── result/                  # Intermediate and final outputs
├── rob2_meta/               # ROB2 generation and refactoring
├── extract/                 # Information extraction modules
├── check/                   # Data validation and consistency checks
├── report/                  # Report generation and merging
├── utils/                   # Utility functions
├── .env
└── README.md
```

---

## Usage

All functionality is accessed through:

```bash
python main.py -c <command> [options]
```

---

## Commands

### 1. Extract Text from PDFs

```bash
python main.py -c process -dir pdf
```

* Reads PDF files from the `pdf/` directory
* Uses Google Gemini to extract full text
* Saves output as `.txt` files with the same name
* Skips files that have already been processed

---

### 2. Extract Meta Information

```bash
python main.py -c extract -m meta/SR1.txt -data data/SR1
```

---

### 3. Check Meta Table Consistency

```bash
python main.py -c check_info -m meta/SR1.txt -data data/SR1
```

---

### 4. Meta Data Correctness Analysis

```bash
python main.py -c meta_data_correct -n SR1 -data data
```

---

### 5. Meta Logic and Structure Validation

```bash
python main.py -c meta_check -n SR1 -data data
```

---

### 6. Generate ROB2 Assessments

```bash
python main.py -c rob2_generate -data data/SR1 -s data/SR1/rob2_result
```

---

### 7. Refactor ROB2 Results

```bash
python main.py -c rob2_refactor -data data/SR1/rob2_result
```

---

### 8. Compare ROB2 Results (Original vs Automated)

```bash
python main.py -c rob2_compare \
  -m meta/SR1.txt \
  -n SR1 \
  -data data/SR1/rob2_result \
  -s result
```

---

### 9. Export ROB2 Comparison to Word

```bash
python main.py -c rob2_doc \
  -data result/SR1_rob2_compare.txt \
  -s report_doc/rob2.docx
```

---

### 10. Generate Wrong-Field Report

```bash
python main.py -c wrong_field_report -n SR1 -data data
```

---

### 11. Generate Data Error Summary

```bash
python main.py -c data_wrong_summary -n SR1 -data data
```

---

### 12. Generate ROB2 Summary Report

```bash
python main.py -c report_2_3_4 -n SR1 -data data
```

---

### 13. Generate Meta-Analysis Summary Report

```bash
python main.py -c report_2_4_4 -n SR1 -data data
```

---

### 14. Export JSON Report

```bash
python main.py -c report_json \
  -m meta/SR1.txt \
  -t report_1 \
  -s result/SR1_report_1.json \
  -n SR1
```

---

### 15. Generate ROB2 Report for a Single Paper

```bash
python main.py -c rob2_paper_doc \
  -r data/SR1/rob2_result/SR1Agulloetal2023.txt \
  -data data/SR1/SR1Agulloetal2023.txt \
  -s report_doc/SR1_1.docx
```

(Outputs can be Word or TXT depending on the save path.)

---

### 16. Merge Multiple Reports into One Word File

```bash
python main.py -c merge -n SR1 -data data -s report_doc/SR1_output.docx
```

---

## Logging

* Logs are written to:

  * Console output
  * `agent.log`

---

## Notes

* Designed for **Systematic Review and Meta-Analysis automation**
* Commands can be executed independently or as a pipeline
* Recommended workflow:

```text
process → extract → check → rob2 → report
```
