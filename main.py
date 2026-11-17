"""
Main Entry Point for Log Data Classifier & Step Analyzer
Supports both CLI mode and GUI mode.
"""

import os
import sys
import argparse
import webbrowser
from datetime import datetime

from classifier import classify_and_copy_logs
from analyzer import AnalysisReport
from report_generator import generate_html_report

def run_pipeline(data_dir, output_dir, progress_callback=None, open_browser=True):
    """
    Executes the full pipeline:
    1. Scan & classify logs into output_dir
    2. Analyze results (yield, defects, step features)
    3. Generate standalone HTML web report
    """
    start_time = datetime.now()
    if progress_callback:
        progress_callback("START", 0, "로그 파일 스캔 및 분류를 시작합니다...")

    # 1. Classification & Copy
    def internal_progress(curr, tot, item):
        if progress_callback:
            pct = int((curr / tot) * 70) if tot > 0 else 0
            progress_callback("CLASSIFY", pct, f"[{curr}/{tot}] 분류 중: {item.file_name}")

    classified_items = classify_and_copy_logs(data_dir, output_dir, internal_progress)
    
    if progress_callback:
        progress_callback("ANALYZE", 75, "품질 통계 및 단계별 결함 특징 분석 중...")

    # 2. Analysis
    report = AnalysisReport(classified_items)

    if progress_callback:
        progress_callback("REPORT", 90, "웹 리포트(HTML Dashboard) 생성 중...")

    # 3. Report Generation
    report_html_path = os.path.join(output_dir, "report.html")
    generate_html_report(report, report_html_path)

    elapsed = (datetime.now() - start_time).total_seconds()
    if progress_callback:
        progress_callback("DONE", 100, f"완료! (소요시간: {elapsed:.1f}초, 총 {len(classified_items)}건 처리)")

    if open_browser:
        try:
            webbrowser.open(f"file:///{os.path.abspath(report_html_path).replace(os.sep, '/')}")
        except Exception:
            pass

    return report, report_html_path


def main():
    parser = argparse.ArgumentParser(description="Log Data Classifier & Quality Analyzer (Portable)")
    parser.add_argument("--data", default="Data", help="Path to input Data folder containing log files")
    parser.add_argument("--output", default="output", help="Path to destination Output folder")
    parser.add_argument("--no-gui", action="store_true", help="Run in CLI mode without launching GUI")
    parser.add_argument("--open-report", action="store_true", default=True, help="Automatically open report in web browser")
    
    args = parser.parse_args()

    # Determine whether to launch GUI:
    # If explicitly passed --no-gui, run CLI.
    # If running with arguments (e.g. --data specified by script), or if tkinter unavailable, run CLI.
    # Otherwise, if run via double-click or no args, launch GUI.
    should_launch_gui = not args.no_gui and (len(sys.argv) <= 1)

    if should_launch_gui:
        try:
            from gui import launch_gui
            launch_gui()
            return
        except Exception as e:
            print(f"GUI launch failed ({e}), falling back to CLI mode...")

    # CLI Execution
    print("=" * 60)
    print("🚀 Log Data Classifier & Step Analyzer (CLI Mode)")
    print("=" * 60)
    print(f"Input Data Folder : {os.path.abspath(args.data)}")
    print(f"Output Directory  : {os.path.abspath(args.output)}")
    print("-" * 60)

    def cli_progress(stage, pct, msg):
        print(f"[{pct:3d}%] {msg}")

    report, html_path = run_pipeline(
        data_dir=args.data,
        output_dir=args.output,
        progress_callback=cli_progress,
        open_browser=args.open_report
    )

    summary = report.to_dict()["summary"]
    print("\n" + "=" * 60)
    print("📊 [분석 완료 요약]")
    print(f" - 총 검사 수량: {summary['total']:,} 건")
    print(f" - 합격 (PASS) : {summary['pass']:,} 건 ({summary['yield_rate']}%)")
    print(f" - 불합격 (FAIL): {summary['fail']:,} 건 ({summary['defect_rate']}%)")
    print(f" - 웹 보고서   : {html_path}")
    print("=" * 60)

if __name__ == "__main__":
    main()
