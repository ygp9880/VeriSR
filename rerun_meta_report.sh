#!/usr/bin/env bash

set -euo pipefail

PYTHON_BIN="${PYTHON_BIN:-python3}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

META_NAME="${1:-SR1}"
WORK_DIR="${2:-all_txt}"
REPORT_FILE="${3:-report_doc/${META_NAME}_output.docx}"
DRY_RUN="${DRY_RUN:-0}"

usage() {
  cat <<EOF
Usage:
  ./rerun_meta_report.sh [META_NAME] [WORK_DIR] [REPORT_FILE]

Examples:
  ./rerun_meta_report.sh
  ./rerun_meta_report.sh SR1
  ./rerun_meta_report.sh SR2 all_txt report_doc/SR2_output.docx

Environment variables:
  PYTHON_BIN  Python executable, default: python3
  DRY_RUN     Set to 1 to print commands only
EOF
}

if [[ "${META_NAME}" == "-h" || "${META_NAME}" == "--help" ]]; then
  usage
  exit 0
fi

run_cmd() {
  printf '\n[%s] %s\n' "RUN" "$*"
  if [[ "${DRY_RUN}" == "0" ]]; then
    "$@"
  fi
}

mkdir -p "${WORK_DIR}" "$(dirname "${REPORT_FILE}")" "${WORK_DIR}/.mplconfig"
export MPLCONFIGDIR="${MPLCONFIGDIR:-${WORK_DIR}/.mplconfig}"

echo "Meta name   : ${META_NAME}"
echo "Work dir    : ${WORK_DIR}"
echo "Report file : ${REPORT_FILE}"
echo "Python      : ${PYTHON_BIN}"

run_cmd "${PYTHON_BIN}" "${SCRIPT_DIR}/main.py" -c meta_check -n "${META_NAME}" -data "${WORK_DIR}"
run_cmd "${PYTHON_BIN}" "${SCRIPT_DIR}/main.py" -c merge -n "${META_NAME}" -data "${WORK_DIR}" -s "${REPORT_FILE}"

if [[ "${DRY_RUN}" == "0" ]]; then
  if [[ ! -s "${REPORT_FILE}" ]]; then
    echo "Final report was not created or is empty: ${REPORT_FILE}" >&2
    exit 1
  fi
fi

printf '\nFinal report: %s\n' "${REPORT_FILE}"
