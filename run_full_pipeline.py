import argparse
import os
import subprocess
import sys


def run_cmd(cmd, dry_run=False):
    print(f"\n[RUN] {' '.join(cmd)}")
    if not dry_run:
        subprocess.run(cmd, check=True)


def run_main(python_bin, script_dir, args, dry_run=False, extra_model=None):
    cmd = [python_bin, os.path.join(script_dir, "main.py"), *args]
    if extra_model:
        cmd.extend(["-model", extra_model])
    run_cmd(cmd, dry_run=dry_run)


def build_parser():
    parser = argparse.ArgumentParser(description="Run the full paperAgent pipeline across platforms.")
    parser.add_argument("--meta-name", required=True, help="Review name, for example SR1")
    parser.add_argument("--meta-file", required=True, help="Meta review text file path")
    parser.add_argument("--study-dir", required=True, help="Directory containing included study .txt files")
    parser.add_argument("--work-dir", required=True, help="Directory for intermediate outputs")
    parser.add_argument("--report-file", required=True, help="Final merged .docx output path")
    parser.add_argument("--meta-pdf", help="Extract the meta review PDF to --meta-file first")
    parser.add_argument("--paper-pdf-dir", help="Run PDF-to-text extraction for included studies in this directory")
    parser.add_argument("--python-bin", default=sys.executable, help="Python interpreter to use")
    parser.add_argument("--gemini-model", help="Override Gemini model for PDF extraction")
    parser.add_argument("--openai-model", help="Override OpenAI-compatible model for audit steps")
    parser.add_argument("--dry-run", action="store_true", help="Print commands without executing them")
    return parser


def main():
    args = build_parser().parse_args()
    script_dir = os.path.dirname(os.path.abspath(__file__))

    os.makedirs(args.work_dir, exist_ok=True)
    os.makedirs(args.study_dir, exist_ok=True)
    report_dir = os.path.dirname(args.report_file)
    if report_dir:
        os.makedirs(report_dir, exist_ok=True)

    os.environ.setdefault("MPLCONFIGDIR", os.path.join(args.work_dir, ".mplconfig"))
    os.makedirs(os.environ["MPLCONFIGDIR"], exist_ok=True)

    print(f"Meta name   : {args.meta_name}")
    print(f"Meta file   : {args.meta_file}")
    print(f"Study dir   : {args.study_dir}")
    print(f"Work dir    : {args.work_dir}")
    print(f"Report file : {args.report_file}")

    if args.meta_pdf or args.paper_pdf_dir:
        run_main(args.python_bin, script_dir, ["-c", "test_gemini"], dry_run=args.dry_run, extra_model=args.gemini_model)

    if args.meta_pdf:
        meta_file_dir = os.path.dirname(args.meta_file)
        if meta_file_dir:
            os.makedirs(meta_file_dir, exist_ok=True)
        run_main(
            args.python_bin,
            script_dir,
            ["-c", "test_gemini", "-data", args.meta_pdf, "-s", args.meta_file],
            dry_run=args.dry_run,
            extra_model=args.gemini_model,
        )

    if args.paper_pdf_dir:
        run_main(
            args.python_bin,
            script_dir,
            ["-c", "process", "-dir", args.paper_pdf_dir],
            dry_run=args.dry_run,
            extra_model=args.gemini_model,
        )

    run_main(args.python_bin, script_dir, ["-c", "extract", "-m", args.meta_file, "-data", args.study_dir], dry_run=args.dry_run)
    run_main(args.python_bin, script_dir, ["-c", "check_info", "-m", args.meta_file, "-data", args.study_dir], dry_run=args.dry_run)
    run_main(args.python_bin, script_dir, ["-c", "meta_data_correct", "-n", args.meta_name, "-data", args.work_dir], dry_run=args.dry_run, extra_model=args.openai_model)
    run_main(args.python_bin, script_dir, ["-c", "meta_check", "-n", args.meta_name, "-data", args.work_dir], dry_run=args.dry_run)

    rob2_dir = os.path.join(args.study_dir, "rob2_result")
    os.makedirs(rob2_dir, exist_ok=True)
    run_main(args.python_bin, script_dir, ["-c", "rob2_generate", "-data", args.study_dir, "-s", rob2_dir], dry_run=args.dry_run, extra_model=args.openai_model)
    run_main(args.python_bin, script_dir, ["-c", "rob2_compare", "-m", args.meta_file, "-n", args.meta_name, "-data", rob2_dir, "-s", args.work_dir], dry_run=args.dry_run)

    for report_type in ("report_1", "report_2_1", "report_2_2", "report_2_3", "report_2_4", "report_2_5", "report_3_1"):
        run_main(
            args.python_bin,
            script_dir,
            ["-c", "report_json", "-m", args.meta_file, "-t", report_type, "-s", args.work_dir, "-n", args.meta_name],
            dry_run=args.dry_run,
        )

    run_main(args.python_bin, script_dir, ["-c", "wrong_field_report", "-n", args.meta_name, "-data", args.work_dir], dry_run=args.dry_run)
    run_main(args.python_bin, script_dir, ["-c", "data_wrong_summary", "-n", args.meta_name, "-data", args.work_dir], dry_run=args.dry_run)
    run_main(args.python_bin, script_dir, ["-c", "report_2_3_4", "-n", args.meta_name, "-data", args.work_dir], dry_run=args.dry_run)
    run_main(args.python_bin, script_dir, ["-c", "report_2_4_4", "-n", args.meta_name, "-data", args.work_dir], dry_run=args.dry_run)

    index = 1
    for paper_name in sorted(os.listdir(args.study_dir)):
        paper_path = os.path.join(args.study_dir, paper_name)
        if not os.path.isfile(paper_path):
            continue
        if not paper_name.endswith(".txt"):
            continue
        if paper_name.endswith("_extracted.txt") or "meta" in paper_name:
            continue

        rob2_path = os.path.join(rob2_dir, paper_name)
        if not os.path.isfile(rob2_path):
            print(f"Skip ROB2 attachment, missing result: {rob2_path}")
            continue

        attachment_path = os.path.join(args.work_dir, f"{args.meta_name}_rob2_{index}.txt")
        run_main(
            args.python_bin,
            script_dir,
            ["-c", "rob2_paper_doc", "-r", rob2_path, "-data", paper_path, "-s", attachment_path],
            dry_run=args.dry_run,
        )
        index += 1

    run_main(args.python_bin, script_dir, ["-c", "merge", "-n", args.meta_name, "-data", args.work_dir, "-s", args.report_file], dry_run=args.dry_run)

    if not args.dry_run:
        if not os.path.isfile(args.report_file) or os.path.getsize(args.report_file) == 0:
            raise RuntimeError(f"Final report was not created or is empty: {args.report_file}")

    print(f"\nFinal report: {args.report_file}")


if __name__ == "__main__":
    main()
