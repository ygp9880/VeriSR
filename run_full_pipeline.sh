#!/usr/bin/env bash

set -euo pipefail

PYTHON_BIN="${PYTHON_BIN:-python3}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

META_NAME=""
META_FILE=""
STUDY_DIR=""
WORK_DIR=""
REPORT_FILE=""
META_PDF=""
PAPER_PDF_DIR=""
GEMINI_MODEL=""
OPENAI_MODEL=""
DRY_RUN=0

usage() {
  cat <<'EOF'
Usage:
  ./run_full_pipeline.sh \
    --meta-name SR1 \
    --meta-file all_txt/SR1.txt \
    --study-dir all_txt/SR1 \
    --work-dir all_txt \
    --report-file report_doc/SR1_output.docx \
    [--meta-pdf pdf/SR1.pdf] \
    [--paper-pdf-dir all_txt/SR1] \
    [--gemini-model gemini-3-flash-preview] \
    [--openai-model openai/gpt-5.1] \
    [--dry-run]

Required:
  --meta-name       Review name, for example SR1
  --meta-file       Meta review text file path, for example all_txt/SR1.txt
  --study-dir       Directory containing included study .txt files
  --work-dir        Directory for intermediate report files
  --report-file     Final merged .docx output path

Optional:
  --meta-pdf        Extract the meta review PDF to --meta-file first
  --paper-pdf-dir   Run PDF-to-text extraction for included studies in this directory
  --gemini-model    Override Gemini model for PDF extraction
  --openai-model    Override OpenAI-compatible model for audit steps
  --dry-run         Print commands without executing them
EOF
}

run_cmd() {
  printf '\n[%s] %s\n' "RUN" "$*"
  if [[ "$DRY_RUN" -eq 0 ]]; then
    "$@"
  fi
}

run_main() {
  local cmd=("$PYTHON_BIN" "$SCRIPT_DIR/main.py" "$@")
  run_cmd "${cmd[@]}"
}

run_main_gemini() {
  if [[ ${#GEMINI_ARGS[@]} -gt 0 ]]; then
    run_main "$@" "${GEMINI_ARGS[@]}"
  else
    run_main "$@"
  fi
}

run_main_openai() {
  if [[ ${#OPENAI_ARGS[@]} -gt 0 ]]; then
    run_main "$@" "${OPENAI_ARGS[@]}"
  else
    run_main "$@"
  fi
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --meta-name)
      META_NAME="$2"
      shift 2
      ;;
    --meta-file)
      META_FILE="$2"
      shift 2
      ;;
    --study-dir)
      STUDY_DIR="$2"
      shift 2
      ;;
    --work-dir)
      WORK_DIR="$2"
      shift 2
      ;;
    --report-file)
      REPORT_FILE="$2"
      shift 2
      ;;
    --meta-pdf)
      META_PDF="$2"
      shift 2
      ;;
    --paper-pdf-dir)
      PAPER_PDF_DIR="$2"
      shift 2
      ;;
    --gemini-model)
      GEMINI_MODEL="$2"
      shift 2
      ;;
    --openai-model)
      OPENAI_MODEL="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if [[ -z "$META_NAME" || -z "$META_FILE" || -z "$STUDY_DIR" || -z "$WORK_DIR" || -z "$REPORT_FILE" ]]; then
  echo "Missing required arguments." >&2
  usage
  exit 1
fi

mkdir -p "$WORK_DIR" "$STUDY_DIR" "$(dirname "$REPORT_FILE")"
export MPLCONFIGDIR="${MPLCONFIGDIR:-$WORK_DIR/.mplconfig}"
mkdir -p "$MPLCONFIGDIR"

GEMINI_ARGS=()
OPENAI_ARGS=()
if [[ -n "$GEMINI_MODEL" ]]; then
  GEMINI_ARGS=(-model "$GEMINI_MODEL")
fi
if [[ -n "$OPENAI_MODEL" ]]; then
  OPENAI_ARGS=(-model "$OPENAI_MODEL")
fi

echo "Meta name   : $META_NAME"
echo "Meta file   : $META_FILE"
echo "Study dir   : $STUDY_DIR"
echo "Work dir    : $WORK_DIR"
echo "Report file : $REPORT_FILE"

if [[ -n "$META_PDF" || -n "$PAPER_PDF_DIR" ]]; then
  run_main_gemini -c test_gemini
fi

if [[ -n "$META_PDF" ]]; then
  mkdir -p "$(dirname "$META_FILE")"
  run_main_gemini -c test_gemini -data "$META_PDF" -s "$META_FILE"
fi

if [[ -n "$PAPER_PDF_DIR" ]]; then
  run_main_gemini -c process -dir "$PAPER_PDF_DIR"
fi

run_main -c extract -m "$META_FILE" -data "$STUDY_DIR"
run_main -c check_info -m "$META_FILE" -data "$STUDY_DIR"
run_main_openai -c meta_data_correct -n "$META_NAME" -data "$WORK_DIR"
run_main -c meta_check -n "$META_NAME" -data "$WORK_DIR"

ROB2_DIR="$STUDY_DIR/rob2_result"
mkdir -p "$ROB2_DIR"
run_main_openai -c rob2_generate -data "$STUDY_DIR" -s "$ROB2_DIR"
run_main -c rob2_compare -m "$META_FILE" -n "$META_NAME" -data "$ROB2_DIR" -s "$WORK_DIR"

for report_type in report_1 report_2_1 report_2_2 report_2_3 report_2_4 report_2_5 report_3_1; do
  run_main -c report_json -m "$META_FILE" -t "$report_type" -s "$WORK_DIR" -n "$META_NAME"
done

run_main -c wrong_field_report -n "$META_NAME" -data "$WORK_DIR"
run_main -c data_wrong_summary -n "$META_NAME" -data "$WORK_DIR"
run_main -c report_2_3_4 -n "$META_NAME" -data "$WORK_DIR"
run_main -c report_2_4_4 -n "$META_NAME" -data "$WORK_DIR"

index=1
shopt -s nullglob
for paper_path in "$STUDY_DIR"/*.txt; do
  paper_name="$(basename "$paper_path")"
  if [[ "$paper_name" == *_extracted.txt ]]; then
    continue
  fi
  if [[ "$paper_name" == *meta* ]]; then
    continue
  fi

  rob2_path="$ROB2_DIR/$paper_name"
  if [[ ! -f "$rob2_path" ]]; then
    echo "Skip ROB2 attachment, missing result: $rob2_path"
    continue
  fi

  attachment_path="$WORK_DIR/${META_NAME}_rob2_${index}.txt"
  run_main -c rob2_paper_doc -r "$rob2_path" -data "$paper_path" -s "$attachment_path"
  index=$((index + 1))
done
shopt -u nullglob

run_main -c merge -n "$META_NAME" -data "$WORK_DIR" -s "$REPORT_FILE"

if [[ "$DRY_RUN" -eq 0 ]]; then
  if [[ ! -s "$REPORT_FILE" ]]; then
    echo "Final report was not created or is empty: $REPORT_FILE" >&2
    exit 1
  fi
fi

printf '\nFinal report: %s\n' "$REPORT_FILE"
