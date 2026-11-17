"""
Web Report Generator Module (Deep-Dive Analysis Version)
Creates an enhanced, self-contained, responsive HTML dashboard report.
Includes:
- Executive Summary Cards
- Comprehensive Visualizations (Charts rendered via SVG & JS)
- 19 Individual Test Items Performance & Duration Analysis
- In-depth Numerical Measurements (Pass vs Fail Comparison: VDDA, Baseline, Untouched Deltas Saturation)
- Multi-dimensional Classifications (Defect Mechanisms, Timeline, Screen Sizes, Stability)
- Step-by-Step Deep-Dive Feature & Defect Analysis Cards
- Hierarchical Breakdown Table (Vendor > Model > Step > Pass/Fail)
- Filterable & Searchable Log Explorer Table with Extended Measurements & CSV Export
"""

import os
import json
from datetime import datetime

def generate_html_report(analysis_report, output_html_path):
    report_data = analysis_report.to_dict()
    items_data = [item.to_dict() for item in analysis_report.log_items]
    
    report_json_str = json.dumps(report_data, ensure_ascii=False)
    items_json_str = json.dumps(items_data, ensure_ascii=False)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>로그 데이터 정밀 분석 및 품질 검사 보고서</title>
  <style>
    :root {{
      --bg: #0b1120;
      --card-bg: #1e293b;
      --card-border: #334155;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --accent: #38bdf8;
      --accent-glow: rgba(56, 189, 248, 0.15);
      --pass: #10b981;
      --pass-bg: rgba(16, 185, 129, 0.15);
      --fail: #ef4444;
      --fail-bg: rgba(239, 68, 68, 0.15);
      --warning: #f59e0b;
      --warning-bg: rgba(245, 158, 11, 0.15);
      --purple: #a855f7;
      --purple-bg: rgba(168, 85, 247, 0.15);
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      background-color: var(--bg);
      color: var(--text-main);
      line-height: 1.6;
      padding-bottom: 80px;
    }}

    .container {{
      max-width: 1480px;
      margin: 0 auto;
      padding: 0 24px;
    }}

    header {{
      background: linear-gradient(135deg, #0b1120 0%, #1e1b4b 50%, #0b1120 100%);
      border-bottom: 1px solid var(--card-border);
      padding: 32px 0 24px 0;
      margin-bottom: 32px;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
    }}

    .header-content {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 16px;
    }}

    .header-title h1 {{
      font-size: 26px;
      font-weight: 800;
      color: #fff;
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .header-title p {{
      color: var(--text-muted);
      font-size: 14px;
      margin-top: 6px;
    }}

    .badge-report {{
      display: inline-block;
      padding: 4px 10px;
      background: rgba(56, 189, 248, 0.12);
      color: var(--accent);
      border: 1px solid rgba(56, 189, 248, 0.3);
      border-radius: 9999px;
      font-size: 12px;
      font-weight: 600;
    }}

    .btn {{
      padding: 10px 18px;
      border-radius: 8px;
      font-weight: 600;
      font-size: 14px;
      cursor: pointer;
      border: none;
      transition: all 0.2s;
      display: inline-flex;
      align-items: center;
      gap: 8px;
    }}
    .btn-primary {{ background: #3b82f6; color: #fff; }}
    .btn-primary:hover {{ background: #2563eb; transform: translateY(-1px); }}
    .btn-outline {{ background: transparent; color: var(--accent); border: 1px solid var(--accent); }}
    .btn-outline:hover {{ background: rgba(56, 189, 248, 0.1); }}

    /* KPI Grid */
    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
      gap: 20px;
      margin-bottom: 32px;
    }}

    .kpi-card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 20px;
      position: relative;
      overflow: hidden;
      box-shadow: 0 4px 12px rgba(0,0,0,0.25);
    }}
    .kpi-card::before {{
      content: '';
      position: absolute;
      top: 0; left: 0; right: 0; height: 3px;
      background: var(--accent);
    }}
    .kpi-card.pass::before {{ background: var(--pass); }}
    .kpi-card.fail::before {{ background: var(--fail); }}
    .kpi-card.warn::before {{ background: var(--warning); }}
    .kpi-card.purple::before {{ background: var(--purple); }}

    .kpi-label {{
      font-size: 12px;
      color: var(--text-muted);
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}
    .kpi-val {{
      font-size: 26px;
      font-weight: 800;
      margin: 8px 0 4px 0;
      color: #fff;
    }}
    .kpi-sub {{
      font-size: 12px;
      color: var(--text-muted);
    }}

    /* Section Styling */
    .section-title {{
      font-size: 20px;
      font-weight: 700;
      color: #fff;
      margin: 36px 0 20px 0;
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    .section-title::before {{
      content: '';
      display: inline-block;
      width: 4px;
      height: 20px;
      background: var(--accent);
      border-radius: 2px;
    }}

    /* Chart Grid */
    .chart-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;
      margin-bottom: 36px;
    }}
    @media (max-width: 992px) {{
      .chart-grid {{ grid-template-columns: 1fr; }}
    }}

    .chart-card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 24px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }}
    .chart-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      border-bottom: 1px solid rgba(255,255,255,0.06);
      padding-bottom: 12px;
    }}
    .chart-title {{ font-size: 16px; font-weight: 700; color: #fff; }}

    .svg-container {{
      width: 100%;
      height: 250px;
      display: flex;
      align-items: center;
      justify-content: center;
    }}

    /* Tables */
    .table-card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 24px;
      margin-bottom: 32px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.2);
      overflow-x: auto;
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      text-align: left;
      font-size: 13px;
    }}
    th {{
      background: #0f172a;
      padding: 12px 14px;
      color: var(--text-muted);
      font-weight: 600;
      border-bottom: 2px solid var(--card-border);
      white-space: nowrap;
    }}
    td {{
      padding: 12px 14px;
      border-bottom: 1px solid rgba(255,255,255,0.05);
      white-space: nowrap;
    }}
    tr:hover td {{
      background: rgba(255,255,255,0.02);
    }}

    .tag-pass {{ background: var(--pass-bg); color: var(--pass); padding: 3px 8px; border-radius: 4px; font-weight: 700; font-size: 11px; }}
    .tag-fail {{ background: var(--fail-bg); color: var(--fail); padding: 3px 8px; border-radius: 4px; font-weight: 700; font-size: 11px; }}
    .tag-warn {{ background: var(--warning-bg); color: var(--warning); padding: 3px 8px; border-radius: 4px; font-weight: 700; font-size: 11px; }}
    .tag-info {{ background: var(--purple-bg); color: var(--purple); padding: 3px 8px; border-radius: 4px; font-weight: 700; font-size: 11px; }}

    /* Measurements Comparison Cards */
    .meas-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(440px, 1fr));
      gap: 20px;
      margin-bottom: 32px;
    }}
    @media (max-width: 768px) {{
      .meas-grid {{ grid-template-columns: 1fr; }}
    }}

    .meas-card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 20px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }}
    .meas-title {{
      font-size: 15px;
      font-weight: 700;
      color: #fff;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .meas-spec {{
      font-size: 12px;
      color: var(--accent);
      background: rgba(56, 189, 248, 0.1);
      padding: 2px 8px;
      border-radius: 4px;
    }}

    .meas-stat-row {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
      background: rgba(15, 23, 42, 0.6);
      padding: 12px;
      border-radius: 8px;
    }}
    .meas-col {{
      display: flex;
      flex-direction: column;
      gap: 4px;
    }}
    .meas-col-header {{
      font-size: 12px;
      font-weight: 700;
      display: flex;
      align-items: center;
      gap: 6px;
    }}
    .meas-num {{
      font-size: 16px;
      font-weight: 800;
      color: #fff;
    }}
    .meas-sub {{
      font-size: 11px;
      color: var(--text-muted);
    }}
    .meas-insight {{
      font-size: 12px;
      color: #cbd5e1;
      background: rgba(255,255,255,0.03);
      border-left: 3px solid var(--accent);
      padding: 8px 12px;
      border-radius: 4px;
      margin-top: auto;
    }}

    /* Step Feature Deep-Dive Cards */
    .step-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(420px, 1fr));
      gap: 24px;
      margin-bottom: 40px;
    }}
    @media (max-width: 768px) {{
      .step-grid {{ grid-template-columns: 1fr; }}
    }}

    .step-card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 14px;
      padding: 24px;
      display: flex;
      flex-direction: column;
      gap: 16px;
      box-shadow: 0 4px 16px rgba(0,0,0,0.25);
    }}
    .step-card-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      border-bottom: 1px solid rgba(255,255,255,0.08);
      padding-bottom: 14px;
    }}
    .step-badge-name {{ font-size: 17px; font-weight: 700; color: #fff; }}
    .step-badge-rate {{ padding: 4px 12px; border-radius: 20px; font-size: 13px; font-weight: 700; }}
    .rate-good {{ background: var(--pass-bg); color: var(--pass); border: 1px solid rgba(16, 185, 129, 0.4); }}
    .rate-bad {{ background: var(--fail-bg); color: var(--fail); border: 1px solid rgba(239, 68, 68, 0.4); }}

    .step-metrics {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 12px;
      background: rgba(15, 23, 42, 0.5);
      padding: 12px;
      border-radius: 8px;
    }}
    .step-metric-item {{ text-align: center; }}
    .step-metric-num {{ font-size: 16px; font-weight: 700; }}
    .step-metric-lbl {{ font-size: 11px; color: var(--text-muted); }}

    .progress-track {{
      background: #334155;
      height: 8px;
      border-radius: 4px;
      overflow: hidden;
      margin: 8px 0;
      display: flex;
    }}
    .progress-fill-pass {{ background: var(--pass); }}
    .progress-fill-fail {{ background: var(--fail); }}

    .fail-items-title {{
      font-size: 13px;
      font-weight: 700;
      color: #cbd5e1;
      margin-bottom: 8px;
    }}
    .fail-list {{
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 6px;
    }}
    .fail-list li {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: rgba(239, 68, 68, 0.08);
      border-left: 3px solid var(--fail);
      padding: 6px 10px;
      border-radius: 4px;
      font-size: 12px;
    }}

    .insight-box {{
      background: rgba(56, 189, 248, 0.06);
      border: 1px solid rgba(56, 189, 248, 0.2);
      border-radius: 8px;
      padding: 14px;
      margin-top: auto;
    }}
    .insight-title {{
      font-size: 12px;
      font-weight: 700;
      color: var(--accent);
      margin-bottom: 6px;
    }}
    .insight-box ul {{ padding-left: 18px; font-size: 12px; color: #cbd5e1; }}
    .insight-box li {{ margin-bottom: 4px; }}

    /* Multi-dimensional Cards */
    .multi-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 20px;
      margin-bottom: 32px;
    }}

    /* Search & Filter Bar */
    .table-controls {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      margin-bottom: 16px;
      flex-wrap: wrap;
    }}
    .search-input {{
      background: #0f172a;
      border: 1px solid var(--card-border);
      color: #fff;
      padding: 8px 14px;
      border-radius: 6px;
      font-size: 13px;
      width: 280px;
    }}
    .filter-btn-group {{ display: flex; gap: 6px; }}
    .filter-btn {{
      padding: 6px 12px;
      border-radius: 6px;
      background: #0f172a;
      border: 1px solid var(--card-border);
      color: var(--text-muted);
      cursor: pointer;
      font-size: 12px;
      font-weight: 600;
    }}
    .filter-btn.active {{
      background: #3b82f6;
      color: #fff;
      border-color: #3b82f6;
    }}

    @media print {{
      body {{ background: #fff; color: #000; }}
      .kpi-card, .chart-card, .step-card, .table-card, .meas-card {{
        background: #fff;
        border: 1px solid #ccc;
        box-shadow: none;
        color: #000;
      }}
      .btn, .table-controls {{ display: none; }}
      .kpi-val, .step-badge-name, .chart-title, .meas-title {{ color: #000; }}
    }}
  </style>
</head>
<body>

  <header>
    <div class="container header-content">
      <div class="header-title">
        <span class="badge-report">ADVANCED LOG DEEP-DIVE QUALITY REPORT</span>
        <h1><span>🔬</span> 로그 데이터 정밀 측정 분석 및 공정 품질 리포트</h1>
        <p>19개 검사 항목 정밀 수치 분석 (Pass vs Fail 비교) &bull; 다차원 결함 분류 &bull; 4단계 계층 분류</p>
      </div>
      <div>
        <button class="btn btn-primary" onclick="exportToCSV()">📥 정밀 분석 CSV 다운로드</button>
        <button class="btn btn-outline" onclick="window.print()">🖨️ 보고서 인쇄</button>
      </div>
    </div>
  </header>

  <div class="container">

    <!-- KPI Summary Grid -->
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-label">총 검사 로그 수량</div>
        <div class="kpi-val">{report_data['summary']['total']:,} <span style="font-size:15px;color:var(--text-muted);font-weight:normal">건</span></div>
        <div class="kpi-sub">생성 일시: {now_str}</div>
      </div>
      <div class="kpi-card pass">
        <div class="kpi-label">총 합격 수량 (PASS)</div>
        <div class="kpi-val" style="color:var(--pass)">{report_data['summary']['pass']:,} <span style="font-size:15px;font-weight:normal">건</span></div>
        <div class="kpi-sub">종합 양품률: <strong style="color:var(--pass)">{report_data['summary']['yield_rate']}%</strong></div>
      </div>
      <div class="kpi-card fail">
        <div class="kpi-label">총 불합격 수량 (FAIL)</div>
        <div class="kpi-val" style="color:var(--fail)">{report_data['summary']['fail']:,} <span style="font-size:15px;font-weight:normal">건</span></div>
        <div class="kpi-sub">종합 불량률: <strong style="color:var(--fail)">{report_data['summary']['defect_rate']}%</strong></div>
      </div>
      <div class="kpi-card purple">
        <div class="kpi-label">고유 검사 항목 (Test Items)</div>
        <div class="kpi-val" style="color:var(--purple)">{len(report_data['test_items_summary'])} <span style="font-size:15px;font-weight:normal">항목</span></div>
        <div class="kpi-sub">VDDA, Baseline, Pin Leakage, Deltas 등</div>
      </div>
      <div class="kpi-card warn">
        <div class="kpi-label">재시도 발생 건수 (Retries)</div>
        <div class="kpi-val" style="color:var(--warning)">{sum(1 for i in items_data if i['retry_count'] > 0):,} <span style="font-size:15px;font-weight:normal">건</span></div>
        <div class="kpi-sub">Attempt 2 이상 또는 Reset 후 회복</div>
      </div>
    </div>

    <!-- NEW SECTION: Detailed Numerical Measurements (Pass vs Fail Comparison) -->
    <div class="section-title">📐 세부 측정값 정밀 분석 및 Pass vs Fail 비교 분석 (최대/최소/평균)</div>
    <div class="meas-grid">
"""

    # Populate Numerical Measurements Comparison Cards
    for m_key, m_info in report_data['measurements_comparison'].items():
        p_stat = m_info['pass']
        f_stat = m_info['fail']

        p_avg_str = f"{p_stat['avg']} {m_info['unit']}" if p_stat['avg'] is not None else "-"
        p_range_str = f"Min: {p_stat['min']} ~ Max: {p_stat['max']}" if p_stat['min'] is not None else "-"
        
        f_avg_str = f"{f_stat['avg']} {m_info['unit']}" if f_stat['avg'] is not None else "-"
        f_range_str = f"Min: {f_stat['min']} ~ Max: {f_stat['max']}" if f_stat['min'] is not None else "-"

        html_content += f"""
        <div class="meas-card">
          <div class="meas-title">
            <span>{m_info['metric_name']}</span>
            <span class="meas-spec">규격: {m_info['normal_spec']}</span>
          </div>

          <div class="meas-stat-row">
            <div class="meas-col">
              <div class="meas-col-header" style="color:var(--pass)">
                <span>●</span> PASS (양품 {p_stat['count']}건)
              </div>
              <div class="meas-num" style="color:var(--pass)">{p_avg_str}</div>
              <div class="meas-sub">{p_range_str}</div>
            </div>

            <div class="meas-col">
              <div class="meas-col-header" style="color:var(--fail)">
                <span>▲</span> FAIL (불량 {f_stat['count']}건)
              </div>
              <div class="meas-num" style="color:var(--fail)">{f_avg_str}</div>
              <div class="meas-sub">{f_range_str}</div>
            </div>
          </div>

          <div class="meas-insight">
            💡 <strong>불량 분석 인사이트:</strong> {m_info['insight']}
          </div>
        </div>
        """

    html_content += """
    </div>

    <!-- NEW SECTION: All 19 Test Items Performance Table -->
    <div class="section-title">📋 19개 개별 검사 항목별 최종 결과 및 실행 통계 (중복 시 최종 판정 기준)</div>
    <div class="table-card">
      <table>
        <thead>
          <tr>
            <th>검사 항목명 (Test Step Name)</th>
            <th style="text-align:right">총 실행 수</th>
            <th style="text-align:right">PASS</th>
            <th style="text-align:right">FAIL</th>
            <th style="text-align:right">WARNING</th>
            <th style="text-align:right">합격률 (%)</th>
            <th style="text-align:right">불량률 (%)</th>
            <th style="text-align:right">평균 시도 횟수</th>
            <th style="text-align:right">PASS 평균 소요시간</th>
            <th style="text-align:right">FAIL 평균 소요시간</th>
            <th>시간 편차 (Fail - Pass)</th>
          </tr>
        </thead>
        <tbody>
    """

    for t_name, t_stat in report_data['test_items_summary'].items():
        p_rate = t_stat['pass_rate']
        f_rate = t_stat['fail_rate']
        diff = t_stat['time_diff_sec']
        diff_str = f"+{diff}s" if diff > 0 else f"{diff}s"
        diff_color = "var(--fail)" if diff > 5.0 else ("var(--accent)" if diff < -1.0 else "var(--text-muted)")

        badge_class = "tag-pass" if f_rate == 0 else ("tag-warn" if f_rate < 10 else "tag-fail")

        html_content += f"""
        <tr>
          <td><strong>{t_name}</strong></td>
          <td style="text-align:right;font-weight:600">{t_stat['executed']:,}</td>
          <td style="text-align:right;color:var(--pass);font-weight:600">{t_stat['pass']:,}</td>
          <td style="text-align:right;color:{'var(--fail)' if t_stat['fail'] > 0 else 'var(--text-muted)'};font-weight:600">{t_stat['fail']:,}</td>
          <td style="text-align:right;color:{'var(--warning)' if t_stat['warn'] > 0 else 'var(--text-muted)'}">{t_stat['warn']:,}</td>
          <td style="text-align:right">{p_rate}%</td>
          <td style="text-align:right"><span class="{badge_class}">{f_rate}%</span></td>
          <td style="text-align:right">{t_stat['avg_attempts']}회</td>
          <td style="text-align:right">{t_stat['avg_pass_time_sec']}초</td>
          <td style="text-align:right">{t_stat['avg_fail_time_sec']}초</td>
          <td style="text-align:right;color:{diff_color};font-weight:600">{diff_str}</td>
        </tr>
        """

    html_content += """
        </tbody>
      </table>
    </div>

    <!-- NEW SECTION: Multi-Dimensional Classifications -->
    <div class="section-title">🏷️ 추가 다차원 분류 분석 (결함 메커니즘 &bull; 생산 일정 &bull; 폼팩터 &bull; 안정성)</div>
    <div class="multi-grid">
      
      <!-- Multi 1: Defect Mechanism -->
      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-title">1. 결함 메커니즘별 분류</div>
          <span style="font-size:12px;color:var(--text-muted)">Defect Root Cause</span>
        </div>
        <table>
          <thead><tr><th>결함 원인 분류</th><th style="text-align:right">수량</th><th style="text-align:right">비율</th></tr></thead>
          <tbody>
    """
    for mech, m_data in report_data['defect_mechanism_stats'].items():
        is_norm = "Normal" in mech
        color = "var(--pass)" if is_norm else "var(--fail)"
        html_content += f"""
        <tr>
          <td><span style="color:{color};font-weight:600">{mech}</span></td>
          <td style="text-align:right;font-weight:600">{m_data['count']}건</td>
          <td style="text-align:right">{m_data['pct']}%</td>
        </tr>
        """
    html_content += """
          </tbody>
        </table>
      </div>

      <!-- Multi 2: Date Timeline -->
      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-title">2. 생산 일자 / 배치별 추이</div>
          <span style="font-size:12px;color:var(--text-muted)">Timeline Breakdown</span>
        </div>
        <table>
          <thead><tr><th>검사 일자</th><th style="text-align:right">검사수</th><th style="text-align:right">PASS</th><th style="text-align:right">양품률</th></tr></thead>
          <tbody>
    """
    for d_str, d_stat in report_data['date_timeline_stats'].items():
        y_rate = d_stat['yield_rate']
        color = "var(--pass)" if y_rate > 90 else ("var(--warning)" if y_rate > 30 else "var(--fail)")
        html_content += f"""
        <tr>
          <td><strong>{d_str}</strong></td>
          <td style="text-align:right">{d_stat['total']:,}건</td>
          <td style="text-align:right;color:var(--pass)">{d_stat['pass']:,}건</td>
          <td style="text-align:right;color:{color};font-weight:700">{y_rate}%</td>
        </tr>
        """
    html_content += """
          </tbody>
        </table>
      </div>

      <!-- Multi 3: Screen Size Form Factor -->
      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-title">3. 화면 크기 / 규격별 품질</div>
          <span style="font-size:12px;color:var(--text-muted)">Form Factor Analysis</span>
        </div>
        <table>
          <thead><tr><th>화면 크기 규격</th><th style="text-align:right">총 수량</th><th style="text-align:right">양품률</th><th style="text-align:right">불량률</th></tr></thead>
          <tbody>
    """
    for sz_name, sz_stat in report_data['screen_size_stats'].items():
        html_content += f"""
        <tr>
          <td><strong>{sz_name}</strong></td>
          <td style="text-align:right">{sz_stat['total']:,}건</td>
          <td style="text-align:right;color:var(--pass)">{sz_stat['yield_rate']}%</td>
          <td style="text-align:right;color:{'var(--fail)' if sz_stat['defect_rate'] > 10 else 'var(--text-muted)'}">{sz_stat['defect_rate']}%</td>
        </tr>
        """
    html_content += """
          </tbody>
        </table>
      </div>

      <!-- Multi 4: Test Stability -->
      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-title">4. 검사 안정성 (재시도 및 회복)</div>
          <span style="font-size:12px;color:var(--text-muted)">Test Stability</span>
        </div>
        <table>
          <thead><tr><th>안정성 분류</th><th style="text-align:right">수량</th><th style="text-align:right">점유율</th></tr></thead>
          <tbody>
    """
    for stb_name, stb_stat in report_data['stability_stats'].items():
        tag = "tag-pass" if "Clean" in stb_name else ("tag-warn" if "Recovered" in stb_name else "tag-fail")
        html_content += f"""
        <tr>
          <td><span class="{tag}">{stb_name}</span></td>
          <td style="text-align:right;font-weight:600">{stb_stat['count']:,}건</td>
          <td style="text-align:right">{stb_stat['pct']}%</td>
        </tr>
        """
    html_content += """
          </tbody>
        </table>
      </div>

    </div>

    <!-- Charts Section -->
    <div class="section-title">📊 종합 시각화 차트 (도넛, 막대, 파레토)</div>
    <div class="chart-grid">
      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-title">종합 양품률 vs 불량률 비율</div>
          <span style="font-size:12px;color:var(--text-muted)">Total: {report_data['summary']['total']:,}건</span>
        </div>
        <div class="svg-container" id="donutChartContainer"></div>
      </div>

      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-title">공정 단계(Step)별 검사 수량 및 불량률(%)</div>
          <span style="font-size:12px;color:var(--text-muted)">Stacked Bar &amp; Rate</span>
        </div>
        <div class="svg-container" id="stepBarChartContainer"></div>
      </div>

      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-title">업체(Vendor)별 수량 및 양품률 비교</div>
          <span style="font-size:12px;color:var(--text-muted)">Vendor Overview</span>
        </div>
        <div class="svg-container" id="vendorChartContainer"></div>
      </div>

      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-title">주요 불합격(FAIL) 원인 파레토 분석</div>
          <span style="font-size:12px;color:var(--text-muted)">Top Defect Modes</span>
        </div>
        <div class="svg-container" id="paretoChartContainer"></div>
      </div>
    </div>

    <!-- Step Features Deep Dive Section -->
    <div class="section-title">🔬 공정 단계(Step)별 세부 품질 분석 및 결함 특징</div>
    <div class="step-grid">
"""

    for s_name, feat in report_data['step_features'].items():
        is_high_defect = feat['defect_rate'] > 30.0
        badge_class = "rate-bad" if is_high_defect else "rate-good"
        pass_pct = feat['yield_rate']
        fail_pct = feat['defect_rate']
        
        fail_sub_html = ""
        if feat['failed_substeps']:
            items_li = []
            for sub, cnt in list(feat['failed_substeps'].items())[:5]:
                items_li.append(f"<li><span class='name'>{sub}</span><span class='count'>{cnt}건</span></li>")
            fail_sub_html = f"""
            <div>
              <div class="fail-items-title">⚠️ 주요 실패 검사항목 (TOP Failed Sub-steps)</div>
              <ul class="fail-list">{''.join(items_li)}</ul>
            </div>
            """
        elif feat['warnings']:
            items_li = []
            for w, cnt in list(feat['warnings'].items())[:3]:
                items_li.append(f"<li style='border-left-color:var(--warning);background:rgba(245,158,11,0.08)'><span class='name' style='color:#fde68a'>{w}</span><span class='count'>{cnt}건</span></li>")
            fail_sub_html = f"""
            <div>
              <div class="fail-items-title" style="color:#fde68a">⚠️ 주의 검사항목 (Warning Sub-steps)</div>
              <ul class="fail-list">{''.join(items_li)}</ul>
            </div>
            """
        else:
            fail_sub_html = """
            <div style="background:rgba(16,185,129,0.05);padding:10px;border-radius:6px;border:1px dashed rgba(16,185,129,0.3);color:var(--pass);font-size:12px;text-align:center;">
              ✅ 특이 결함 검사항목 없음 (100% 양품 유지)
            </div>
            """

        insights_li = "".join([f"<li>{ins}</li>" for ins in feat['insights']])
        
        html_content += f"""
        <div class="step-card">
          <div class="step-card-header">
            <div>
              <div class="step-badge-name">{feat['step_name']}</div>
              <div style="font-size:12px;color:var(--text-muted);margin-top:2px;">검사 파일 총 {feat['total']:,}건</div>
            </div>
            <div class="step-badge-rate {badge_class}">
              불량률 {feat['defect_rate']}%
            </div>
          </div>

          <div class="step-metrics">
            <div class="step-metric-item">
              <div class="step-metric-num" style="color:var(--pass)">{feat['pass']:,}</div>
              <div class="step-metric-lbl">PASS (양품)</div>
            </div>
            <div class="step-metric-item">
              <div class="step-metric-num" style="color:var(--fail)">{feat['fail']:,}</div>
              <div class="step-metric-lbl">FAIL (불량)</div>
            </div>
            <div class="step-metric-item">
              <div class="step-metric-num" style="color:var(--accent)">{feat['avg_total_time']}s</div>
              <div class="step-metric-lbl">평균 검사시간</div>
            </div>
          </div>

          <div>
            <div style="display:flex;justify-content:space-between;font-size:11px;color:var(--text-muted);">
              <span>양품: {pass_pct}%</span>
              <span>불량: {fail_pct}%</span>
            </div>
            <div class="progress-track">
              <div class="progress-fill-pass" style="width: {pass_pct}%;"></div>
              <div class="progress-fill-fail" style="width: {fail_pct}%;"></div>
            </div>
          </div>

          {fail_sub_html}

          <div class="insight-box">
            <div class="insight-title">💡 단계별 공정 특징 및 엔지니어링 분석</div>
            <ul>{insights_li}</ul>
          </div>
        </div>
        """

    html_content += """
    </div>

    <!-- Hierarchical Summary Table -->
    <div class="section-title">📂 4단계 계층별 분류 결과 요약 (1.업체 &gt; 2.Model &gt; 3.Step &gt; 4.Pass/Fail)</div>
    <div class="table-card">
      <table>
        <thead>
          <tr>
            <th>1. 업체 (Vendor)</th>
            <th>2. Model (모델)</th>
            <th>3. Step (공정 단계)</th>
            <th style="text-align:right">총 수량</th>
            <th style="text-align:right">PASS (합격)</th>
            <th style="text-align:right">FAIL (불합격)</th>
            <th style="text-align:right">양품률 (%)</th>
            <th style="text-align:right">불량률 (%)</th>
            <th>품질 판정 현황</th>
          </tr>
        </thead>
        <tbody>
    """

    for v, m_dict in report_data['hierarchical'].items():
        for m, s_dict in m_dict.items():
            for s, stats in s_dict.items():
                p_rate = stats['yield_rate']
                d_rate = stats['defect_rate']
                badge = f"<span class='tag-pass'>우수 ({p_rate}%)</span>" if d_rate < 10 else f"<span class='tag-fail'>주의 ({d_rate}%)</span>"
                html_content += f"""
                <tr>
                  <td><strong>{v}</strong></td>
                  <td>{m}</td>
                  <td><code>{s}</code></td>
                  <td style="text-align:right;font-weight:600">{stats['total']:,}</td>
                  <td style="text-align:right;color:var(--pass);font-weight:600">{stats['pass']:,}</td>
                  <td style="text-align:right;color:var(--fail);font-weight:600">{stats['fail']:,}</td>
                  <td style="text-align:right">{p_rate}%</td>
                  <td style="text-align:right;color:{'var(--fail)' if d_rate > 30 else '#cbd5e1'}">{d_rate}%</td>
                  <td>{badge}</td>
                </tr>
                """

    html_content += f"""
        </tbody>
      </table>
    </div>

    <!-- Full Log Explorer Table -->
    <div class="section-title">📋 개별 검사 로그 정밀 데이터 탐색기 (1,152건 측정값 포함)</div>
    <div class="table-card">
      <div class="table-controls">
        <input type="text" id="searchInput" class="search-input" placeholder="🔍 파일명, 바코드, 업체, 결함 원인 검색..." onkeyup="filterTable()">
        <div class="filter-btn-group">
          <button class="filter-btn active" onclick="setFilter('ALL', this)">전체 ({report_data['summary']['total']:,})</button>
          <button class="filter-btn" onclick="setFilter('PASS', this)">PASS만 ({report_data['summary']['pass']:,})</button>
          <button class="filter-btn" onclick="setFilter('FAIL', this)">FAIL만 ({report_data['summary']['fail']:,})</button>
        </div>
      </div>

      <div style="max-height: 540px; overflow-y: auto;">
        <table id="logTable">
          <thead>
            <tr>
              <th>결과</th>
              <th>파일명</th>
              <th>검사일자</th>
              <th>바코드</th>
              <th>업체</th>
              <th>Model</th>
              <th>Step</th>
              <th>VDDA</th>
              <th>Baseline Avg</th>
              <th>Deltas (Min)</th>
              <th>검사시간</th>
              <th>결함 메커니즘 / 사유</th>
            </tr>
          </thead>
          <tbody id="tableBody">
          </tbody>
        </table>
      </div>
      <div style="font-size:12px;color:var(--text-muted);margin-top:12px;text-align:right;" id="tableCountDisplay">
        전체 로그 표시 중
      </div>
    </div>

  </div>

  <script>
    const reportData = {report_json_str};
    const logItems = {items_json_str};

    let currentFilter = 'ALL';
    let currentSearch = '';

    function renderTable() {{
      const tbody = document.getElementById('tableBody');
      const filtered = logItems.filter(item => {{
        if (currentFilter !== 'ALL' && item.result !== currentFilter) return false;
        if (currentSearch) {{
          const q = currentSearch.toLowerCase();
          const target = (item.file_name + ' ' + (item.barcode || '') + ' ' + item.vendor + ' ' + item.model + ' ' + item.step + ' ' + item.defect_mechanism).toLowerCase();
          if (!target.includes(q)) return false;
        }}
        return true;
      }});

      const slice = filtered.slice(0, 500);
      let html = '';
      slice.forEach(item => {{
        const isPass = item.result === 'PASS';
        const tag = isPass ? '<span class="tag-pass">PASS</span>' : '<span class="tag-fail">FAIL</span>';
        const vddaStr = item.vdda_mv ? item.vdda_mv + 'mV' : '-';
        const baseStr = item.baseline_avg ? item.baseline_avg.toLocaleString() : '-';
        const dMinStr = item.delta_min !== null && item.delta_min !== undefined ? item.delta_min : '-';
        const dMinColor = (item.delta_min !== null && item.delta_min <= -30000) ? 'color:var(--fail);font-weight:700;' : '';

        html += `<tr>
          <td>${{tag}}</td>
          <td><strong style="color:#fff;">${{item.file_name}}</strong></td>
          <td>${{item.test_date}}</td>
          <td><code>${{item.barcode || '-'}}</code></td>
          <td>${{item.vendor}}</td>
          <td>${{item.model}}</td>
          <td><code>${{item.step}}</code></td>
          <td>${{vddaStr}}</td>
          <td>${{baseStr}}</td>
          <td style="${{dMinColor}}">${{dMinStr}}</td>
          <td>${{item.total_time_str}}</td>
          <td style="color:${{isPass ? 'var(--text-muted)' : '#fca5a5'}}">${{item.defect_mechanism}}</td>
        </tr>`;
      }});

      tbody.innerHTML = html;
      document.getElementById('tableCountDisplay').innerText = 
        `총 ${{filtered.length.toLocaleString()}}개 중 ${{slice.length}}개 표시 (전체 데이터는 상단 CSV 저장 가능)`;
    }}

    function filterTable() {{
      currentSearch = document.getElementById('searchInput').value.trim();
      renderTable();
    }}

    function setFilter(type, btn) {{
      currentFilter = type;
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      renderTable();
    }}

    function exportToCSV() {{
      const headers = ["FileName", "TestDate", "Barcode", "Vendor", "Model", "Step", "Result", "VDDA_mV", "BaselineAvg", "BaselineDevPct", "DeltaMin", "DeltaMax", "TotalTime", "DefectMechanism", "FailedSubsteps", "SrcPath", "DestPath"];
      let csvContent = "data:text/csv;charset=utf-8,\uFEFF";
      csvContent += headers.join(",") + "\\r\\n";

      logItems.forEach(item => {{
        const row = [
          `"${{item.file_name}}"`,
          `"${{item.test_date}}"`,
          `"${{item.barcode || ''}}"`,
          `"${{item.vendor}}"`,
          `"${{item.model}}"`,
          `"${{item.step}}"`,
          `"${{item.result}}"`,
          `"${{item.vdda_mv || ''}}"`,
          `"${{item.baseline_avg || ''}}"`,
          `"${{item.baseline_dev || ''}}"`,
          `"${{item.delta_min !== null ? item.delta_min : ''}}"`,
          `"${{item.delta_max !== null ? item.delta_max : ''}}"`,
          `"${{item.total_time_str}}"`,
          `"${{item.defect_mechanism}}"`,
          `"${{(item.failed_substeps || []).join('; ')}}"`,
          `"${{item.src_path.replace(/\\\\/g, '/')}}"`,
          `"${{item.dest_path.replace(/\\\\/g, '/')}}"`
        ];
        csvContent += row.join(",") + "\\r\\n";
      }});

      const encodedUri = encodeURI(csvContent);
      const link = document.createElement("a");
      link.setAttribute("href", encodedUri);
      link.setAttribute("download", "Log_DeepDive_Analysis.csv");
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }}

    function renderCharts() {{
      renderDonutChart();
      renderStepBarChart();
      renderVendorBarChart();
      renderParetoChart();
    }}

    function renderDonutChart() {{
      const p = reportData.summary.pass;
      const f = reportData.summary.fail;
      const tot = p + f;
      if (tot === 0) return;
      const pPct = (p / tot * 100);
      const fPct = (f / tot * 100);

      const r = 80;
      const c = 2 * Math.PI * r;
      const pDash = (pPct / 100) * c;
      const fDash = (fPct / 100) * c;

      const svg = `
      <svg width="280" height="240" viewBox="0 0 280 240">
        <circle cx="140" cy="110" r="${{r}}" fill="none" stroke="#1e293b" stroke-width="32" />
        <circle cx="140" cy="110" r="${{r}}" fill="none" stroke="#10b981" stroke-width="32"
          stroke-dasharray="${{pDash}} ${{c}}" stroke-dashoffset="0" transform="rotate(-90 140 110)" />
        <circle cx="140" cy="110" r="${{r}}" fill="none" stroke="#ef4444" stroke-width="32"
          stroke-dasharray="${{fDash}} ${{c}}" stroke-dashoffset="-${{pDash}}" transform="rotate(-90 140 110)" />
        <text x="140" y="105" text-anchor="middle" fill="#fff" font-size="22" font-weight="800">${{pPct.toFixed(1)}}%</text>
        <text x="140" y="125" text-anchor="middle" fill="#94a3b8" font-size="12">양품률 (Yield)</text>
        <circle cx="70" cy="210" r="5" fill="#10b981" />
        <text x="82" y="214" fill="#cbd5e1" font-size="12">PASS (${{p.toLocaleString()}}건)</text>
        <circle cx="170" cy="210" r="5" fill="#ef4444" />
        <text x="182" y="214" fill="#cbd5e1" font-size="12">FAIL (${{f.toLocaleString()}}건)</text>
      </svg>
      `;
      document.getElementById('donutChartContainer').innerHTML = svg;
    }}

    function renderStepBarChart() {{
      const steps = Object.values(reportData.steps);
      const maxTot = Math.max(...steps.map(s => s.total), 1);
      const svgW = 460;
      const svgH = 240;
      const barH = 22;
      const gap = 14;

      let barsSvg = '';
      steps.forEach((s, idx) => {{
        const y = idx * (barH + gap) + 10;
        const pW = (s.pass / maxTot) * 220;
        const fW = (s.fail / maxTot) * 220;
        const nameShort = s.step_name.length > 16 ? s.step_name.substring(0, 15) + '..' : s.step_name;

        barsSvg += `
          <text x="110" y="${{y + 16}}" text-anchor="end" fill="#cbd5e1" font-size="11">${{nameShort}}</text>
          <rect x="120" y="${{y}}" width="${{pW}}" height="${{barH}}" fill="#10b981" rx="2" />
          <rect x="${{120 + pW}}" y="${{y}}" width="${{fW}}" height="${{barH}}" fill="#ef4444" rx="2" />
          <text x="${{125 + pW + fW}}" y="${{y + 16}}" fill="#fff" font-size="11" font-weight="600">${{s.total}} (${{s.defect_rate}}% FAIL)</text>
        `;
      }});

      const svg = `
      <svg width="100%" height="240" viewBox="0 0 ${{svgW}} ${{svgH}}">
        ${{barsSvg}}
      </svg>
      `;
      document.getElementById('stepBarChartContainer').innerHTML = svg;
    }}

    function renderVendorBarChart() {{
      const vendors = Object.entries(reportData.vendors);
      const svgW = 420;
      const svgH = 220;
      const barH = 26;
      const gap = 16;
      let bars = '';

      vendors.forEach(([vname, vstat], idx) => {{
        const y = idx * (barH + gap) + 15;
        const rate = vstat.yield_rate;
        const w = (rate / 100) * 200;

        bars += `
          <text x="90" y="${{y + 18}}" text-anchor="end" fill="#cbd5e1" font-size="12" font-weight="600">${{vname}}</text>
          <rect x="100" y="${{y}}" width="200" height="${{barH}}" fill="#334155" rx="4" />
          <rect x="100" y="${{y}}" width="${{w}}" height="${{barH}}" fill="#38bdf8" rx="4" />
          <text x="${{110 + w}}" y="${{y + 18}}" fill="#fff" font-size="12" font-weight="700">${{rate}}% (${{vstat.pass}}/${{vstat.total}})</text>
        `;
      }});

      const svg = `
      <svg width="100%" height="220" viewBox="0 0 ${{svgW}} ${{svgH}}">
        ${{bars}}
      </svg>
      `;
      document.getElementById('vendorChartContainer').innerHTML = svg;
    }}

    function renderParetoChart() {{
      const allFailures = {{}};
      Object.values(reportData.step_features).forEach(feat => {{
        for (const [k, v] of Object.entries(feat.failed_substeps)) {{
          allFailures[k] = (allFailures[k] || 0) + v;
        }}
      }});

      const sorted = Object.entries(allFailures).sort((a,b) => b[1] - a[1]).slice(0, 5);
      const maxF = sorted.length > 0 ? sorted[0][1] : 1;
      const svgW = 440;
      const svgH = 220;

      let bars = '';
      sorted.forEach(([fname, fcnt], idx) => {{
        const y = idx * 36 + 15;
        const w = (fcnt / maxF) * 190;
        const shortName = fname.replace(/^\\d+\\.\\s*/, '');
        const label = shortName.length > 15 ? shortName.substring(0, 14) + '..' : shortName;

        bars += `
          <text x="125" y="${{y + 16}}" text-anchor="end" fill="#fca5a5" font-size="11">${{label}}</text>
          <rect x="135" y="${{y}}" width="${{w}}" height="22" fill="#ef4444" rx="3" />
          <text x="${{145 + w}}" y="${{y + 16}}" fill="#fff" font-size="12" font-weight="700">${{fcnt}}건</text>
        `;
      }});

      const svg = `
      <svg width="100%" height="220" viewBox="0 0 ${{svgW}} ${{svgH}}">
        ${{bars}}
      </svg>
      `;
      document.getElementById('paretoChartContainer').innerHTML = svg;
    }}

    window.onload = function() {{
      renderTable();
      renderCharts();
    }};
  </script>
</body>
</html>
"""

    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return output_html_path
